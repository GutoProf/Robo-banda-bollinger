import pandas as pd
import numpy as np
import time
from datetime import datetime
from src.config import ATIVOS, RETRAIN_INTERVAL
from src.mt5_connection import conectar_mt5, obter_dados_historicos
from src.strategy import preparar_dados_para_estrategia, verificar_sinal_compra, verificar_sinal_venda, filtrar_mercado_lateralizado
from src.risk_management import aplicar_gestao_risco
from src.ai_model import extrair_caracteristicas, prever_qualidade_sinal, carregar_modelo, treinar_modelo
from src.backtest import registrar_trade
import MetaTrader5 as mt5
import os

# Caminho para o arquivo de log de decisões
DECISIONS_LOG_PATH = "data/decisions_log.csv"

def registrar_decisao(decision_info):
    """
    Registra informações de uma decisão (incluindo sinais ignorados) em um arquivo CSV.
    
    Args:
        decision_info (dict): Dicionário com informações da decisão.
    """
    # Criar diretório se não existir
    os.makedirs(os.path.dirname(DECISIONS_LOG_PATH), exist_ok=True)
    
    # Converter para DataFrame
    df_decision = pd.DataFrame([decision_info])
    
    # Salvar no CSV (adicionar ao final se já existir)
    if os.path.exists(DECISIONS_LOG_PATH):
        df_decision.to_csv(DECISIONS_LOG_PATH, mode='a', header=False, index=False)
    else:
        df_decision.to_csv(DECISIONS_LOG_PATH, index=False)

def verificar_e_executar_sinais():
    """
    Verifica sinais para todos os ativos e executa operações quando apropriado.
    """
    # Carregar modelo de IA
    modelo = carregar_modelo()
    
    # Obter data atual para verificar se é hora de re-treinar
    hoje = datetime.now().date()
    
    # Verificar se é hora de re-treinar o modelo
    if os.path.exists("data/trades_log.csv"):
        df_trades = pd.read_csv("data/trades_log.csv")
        if len(df_trades) > 0:
            ultima_data = pd.to_datetime(df_trades['data_entrada']).max().date()
            dias_desde_ultimo_treino = (hoje - ultima_data).days
            
            if dias_desde_ultimo_treino >= RETRAIN_INTERVAL:
                print("Re-treinando modelo de IA...")
                modelo = treinar_modelo(df_trades)
    
    # Processar cada ativo
    for ativo in ATIVOS:
        print(f"Processando {ativo}...")
        
        # Obter dados históricos
        df = obter_dados_historicos(ativo, mt5.TIMEFRAME_D1, 100)
        if df.empty:
            continue
            
        # Verificar se temos dados suficientes
        if len(df) < 25:  # Precisamos de pelo menos 25 candles para indicadores e análise
            print(f"Dados insuficientes para {ativo}")
            continue
            
        # Preparar dados com indicadores
        df = preparar_dados_para_estrategia(df)
        
        # Verificar se mercado está lateralizado
        if not filtrar_mercado_lateralizado(df):
            decision_info = {
                'ativo': ativo,
                'data': datetime.now(),
                'decisao': 'ignorado',
                'motivo': 'Mercado não lateralizado (ADX >= 25)',
                'detalhes': f"ADX: {df['adx'].iloc[-1]:.2f}"
            }
            registrar_decisao(decision_info)
            continue
            
        # Verificar sinais de compra e venda
        sinal_compra = verificar_sinal_compra(df)
        sinal_venda = verificar_sinal_venda(df)
        
        # Processar sinal de compra
        if sinal_compra:
            # Extrair características para IA
            caracteristicas = extrair_caracteristicas(df, -2)  # -2 porque o sinal é no penúltimo candle
            if caracteristicas:
                # Verificar com IA se é um bom sinal
                qualidade_sinal = prever_qualidade_sinal(modelo, caracteristicas)
                
                if qualidade_sinal == 0:
                    decision_info = {
                        'ativo': ativo,
                        'data': datetime.now(),
                        'decisao': 'ignorado',
                        'motivo': 'IA classificou sinal como ruim',
                        'detalhes': str(caracteristicas)
                    }
                    registrar_decisao(decision_info)
                    continue  # Ignorar sinal classificado como ruim
            
            # Aplicar gestão de risco
            gestao = aplicar_gestao_risco(ativo, df, 'compra')
            
            # Registrar decisão de compra
            decision_info = {
                'ativo': ativo,
                'data': datetime.now(),
                'decisao': 'compra',
                'motivo': 'Sinal válido identificado',
                'detalhes': f"SL: {gestao['stop_loss']:.5f}, TP: {gestao['take_profit']:.5f}"
            }
            registrar_decisao(decision_info)
            
            # Aqui você chamaria a função para enviar a ordem de compra
            # enviar_ordem_compra(ativo, gestao)
            print(f"Sinal de COMPRA para {ativo}. SL: {gestao['stop_loss']:.5f}, TP: {gestao['take_profit']:.5f}")
        
        # Processar sinal de venda
        elif sinal_venda:
            # Extrair características para IA
            caracteristicas = extrair_caracteristicas(df, -2)  # -2 porque o sinal é no penúltimo candle
            if caracteristicas:
                # Verificar com IA se é um bom sinal
                qualidade_sinal = prever_qualidade_sinal(modelo, caracteristicas)
                
                if qualidade_sinal == 0:
                    decision_info = {
                        'ativo': ativo,
                        'data': datetime.now(),
                        'decisao': 'ignorado',
                        'motivo': 'IA classificou sinal como ruim',
                        'detalhes': str(caracteristicas)
                    }
                    registrar_decisao(decision_info)
                    continue  # Ignorar sinal classificado como ruim
            
            # Aplicar gestão de risco
            gestao = aplicar_gestao_risco(ativo, df, 'venda')
            
            # Registrar decisão de venda
            decision_info = {
                'ativo': ativo,
                'data': datetime.now(),
                'decisao': 'venda',
                'motivo': 'Sinal válido identificado',
                'detalhes': f"SL: {gestao['stop_loss']:.5f}, TP: {gestao['take_profit']:.5f}"
            }
            registrar_decisao(decision_info)
            
            # Aqui você chamaria a função para enviar a ordem de venda
            # enviar_ordem_venda(ativo, gestao)
            print(f"Sinal de VENDA para {ativo}. SL: {gestao['stop_loss']:.5f}, TP: {gestao['take_profit']:.5f}")

def main():
    """
    Função principal que executa o robô.
    """
    # Conectar ao MetaTrader 5
    if not conectar_mt5():
        return
    
    print("Robô iniciado. Pressione Ctrl+C para interromper.")
    
    try:
        while True:
            # Verificar e executar sinais
            verificar_e_executar_sinais()
            
            # Aguardar até a próxima verificação (1 hora)
            # Em um ambiente de produção, você pode querer usar um agendador mais sofisticado
            print("Aguardando próximo ciclo...")
            time.sleep(1 * 60 * 60)  # 1 hora em segundos
            
    except KeyboardInterrupt:
        print("\nRobô interrompido pelo usuário.")
    finally:
        # Finalizar conexão com MT5
        mt5.shutdown()

if __name__ == "__main__":
    main()