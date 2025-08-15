import pandas as pd
import numpy as np
from src.strategy import preparar_dados_para_estrategia, verificar_sinal_compra, verificar_sinal_venda, filtrar_mercado_lateralizado
from src.risk_management import aplicar_gestao_risco
from src.ai_model import extrair_caracteristicas, prever_qualidade_sinal, carregar_modelo
from src.mt5_connection import obter_dados_historicos
import MetaTrader5 as mt5
import os
from datetime import datetime

# Caminho para o arquivo de log de trades
TRADES_LOG_PATH = "data/trades_log.csv"

# Caminho para o arquivo de log de decisões
DECISIONS_LOG_PATH = "data/decisions_log.csv"

def registrar_trade(trade_info):
    """
    Registra informações de um trade em um arquivo CSV.
    
    Args:
        trade_info (dict): Dicionário com informações do trade.
    """
    # Criar diretório se não existir
    os.makedirs(os.path.dirname(TRADES_LOG_PATH), exist_ok=True)
    
    # Converter para DataFrame
    df_trade = pd.DataFrame([trade_info])
    
    # Salvar no CSV (adicionar ao final se já existir)
    if os.path.exists(TRADES_LOG_PATH):
        df_trade.to_csv(TRADES_LOG_PATH, mode='a', header=False, index=False)
    else:
        df_trade.to_csv(TRADES_LOG_PATH, index=False)

def executar_backtest(ativo, dados_historicos):
    """
    Executa um backtest da estratégia para um ativo.
    
    Args:
        ativo (str): Símbolo do ativo.
        dados_historicos (pd.DataFrame): Dados históricos do ativo.
        
    Returns:
        dict: Resultados do backtest.
    """
    # Preparar dados com indicadores
    df = preparar_dados_para_estrategia(dados_historicos)
    
    # Inicializar variáveis para resultados
    trades = []
    saldo = 10000  # Saldo inicial para o backtest
    num_trades = 0
    acertos = 0
    
    # Carregar modelo de IA
    modelo = carregar_modelo()
    
    # Percorrer os dados para identificar sinais
    for i in range(20, len(df)-1):  # Começar após ter dados suficientes para indicadores
        # Verificar se mercado está lateralizado
        if not filtrar_mercado_lateralizado(df.iloc[:i+1]):
            continue
            
        # Verificar sinais de compra e venda
        sinal_compra = verificar_sinal_compra(df.iloc[:i+1])
        sinal_venda = verificar_sinal_venda(df.iloc[:i+1])
        
        # Processar sinal de compra
        if sinal_compra:
            # Extrair características para IA
            caracteristicas = extrair_caracteristicas(df, i-1)  # i-1 porque o sinal é no candle anterior
            if caracteristicas:
                # Verificar com IA se é um bom sinal
                qualidade_sinal = prever_qualidade_sinal(modelo, caracteristicas)
                if qualidade_sinal == 0:
                    continue  # Ignorar sinal classificado como ruim
            
            # Aplicar gestão de risco
            gestao = aplicar_gestao_risco(ativo, df.iloc[:i+1], 'compra')
            
            # Registrar trade (simulado)
            preco_entrada = df['close'].iloc[i]
            sl = gestao['stop_loss']
            tp = gestao['take_profit']
            
            # Simular resultado do trade
            # Encontrar quando SL ou TP seriam atingidos
            resultado = simular_trade(df.iloc[i+1:], preco_entrada, sl, tp, 'compra')
            
            # Atualizar saldo e estatísticas
            saldo += resultado['lucro']
            num_trades += 1
            if resultado['lucro'] > 0:
                acertos += 1
                
            # Registrar informações do trade
            trade_info = {
                'ativo': ativo,
                'data_entrada': df['time'].iloc[i],
                'tipo': 'compra',
                'preco_entrada': preco_entrada,
                'sl': sl,
                'tp': tp,
                'resultado': 'lucro' if resultado['lucro'] > 0 else 'prejuizo',
                'lucro': resultado['lucro'],
                'data_saida': resultado['data_saida']
            }
            trades.append(trade_info)
        
        # Processar sinal de venda
        elif sinal_venda:
            # Extrair características para IA
            caracteristicas = extrair_caracteristicas(df, i-1)  # i-1 porque o sinal é no candle anterior
            if caracteristicas:
                # Verificar com IA se é um bom sinal
                qualidade_sinal = prever_qualidade_sinal(modelo, caracteristicas)
                if qualidade_sinal == 0:
                    continue  # Ignorar sinal classificado como ruim
            
            # Aplicar gestão de risco
            gestao = aplicar_gestao_risco(ativo, df.iloc[:i+1], 'venda')
            
            # Registrar trade (simulado)
            preco_entrada = df['close'].iloc[i]
            sl = gestao['stop_loss']
            tp = gestao['take_profit']
            
            # Simular resultado do trade
            resultado = simular_trade(df.iloc[i+1:], preco_entrada, sl, tp, 'venda')
            
            # Atualizar saldo e estatísticas
            saldo += resultado['lucro']
            num_trades += 1
            if resultado['lucro'] > 0:
                acertos += 1
                
            # Registrar informações do trade
            trade_info = {
                'ativo': ativo,
                'data_entrada': df['time'].iloc[i],
                'tipo': 'venda',
                'preco_entrada': preco_entrada,
                'sl': sl,
                'tp': tp,
                'resultado': 'lucro' if resultado['lucro'] > 0 else 'prejuizo',
                'lucro': resultado['lucro'],
                'data_saida': resultado['data_saida']
            }
            trades.append(trade_info)
    
    # Calcular métricas finais
    taxa_acerto = acertos / num_trades if num_trades > 0 else 0
    lucro_total = saldo - 10000
    
    resultados = {
        'ativo': ativo,
        'saldo_final': saldo,
        'lucro_total': lucro_total,
        'num_trades': num_trades,
        'taxa_acerto': taxa_acerto,
        'trades': trades
    }
    
    return resultados

def simular_trade(df_futuro, preco_entrada, sl, tp, tipo_operacao):
    """
    Simula o resultado de um trade.
    
    Args:
        df_futuro (pd.DataFrame): Dados futuros após a entrada.
        preco_entrada (float): Preço de entrada do trade.
        sl (float): Nível do stop loss.
        tp (float): Nível do take profit.
        tipo_operacao (str): 'compra' ou 'venda'.
        
    Returns:
        dict: Resultado da simulação com lucro e data de saída.
    """
    for index, row in df_futuro.iterrows():
        if tipo_operacao == 'compra':
            # Verificar se atingiu SL (mínima do candle)
            if row['low'] <= sl:
                lucro = (sl - preco_entrada) * 100000  # Assumindo 1 lote padrão
                return {'lucro': lucro, 'data_saida': row['time']}
            
            # Verificar se atingiu TP (máxima do candle)
            if row['high'] >= tp:
                lucro = (tp - preco_entrada) * 100000  # Assumindo 1 lote padrão
                return {'lucro': lucro, 'data_saida': row['time']}
                
        elif tipo_operacao == 'venda':
            # Verificar se atingiu SL (máxima do candle)
            if row['high'] >= sl:
                lucro = (preco_entrada - sl) * 100000  # Assumindo 1 lote padrão
                return {'lucro': lucro, 'data_saida': row['time']}
            
            # Verificar se atingiu TP (mínima do candle)
            if row['low'] <= tp:
                lucro = (preco_entrada - tp) * 100000  # Assumindo 1 lote padrão
                return {'lucro': lucro, 'data_saida': row['time']}
    
    # Se não atingiu nem SL nem TP, sair no último candle
    ultimo_preco = df_futuro['close'].iloc[-1]
    if tipo_operacao == 'compra':
        lucro = (ultimo_preco - preco_entrada) * 100000
    else:
        lucro = (preco_entrada - ultimo_preco) * 100000
        
    return {'lucro': lucro, 'data_saida': df_futuro['time'].iloc[-1]}