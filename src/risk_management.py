 import pandas as pd
 import numpy as np
 from src.config import RISCO_POR_TRADE, TP_OPTION
 from src.indicators import calcular_atr
 
 def calcular_nivel_stop_loss(ativo, df, tipo_operacao):
     """
     Calcula o nível do stop loss com base na estratégia.
     
     Args:
         ativo (str): Símbolo do ativo.
         df (pd.DataFrame): DataFrame com dados de preços.
         tipo_operacao (str): 'compra' ou 'venda'.
         
     Returns:
         float: Nível do stop loss.
     """
     # Índice do candle de sinal (penúltimo candle)
     i_sinal = -2
     
     if tipo_operacao == 'compra':
         # Stop abaixo da mínima do candle que fechou fora da banda
         sl = df['low'].iloc[i_sinal] - 0.0001  # Pequena margem de segurança
     elif tipo_operacao == 'venda':
         # Stop acima da máxima do candle que fechou fora da banda
         sl = df['high'].iloc[i_sinal] + 0.0001  # Pequena margem de segurança
     else:
         raise ValueError("Tipo de operação inválido. Use 'compra' ou 'venda'.")
     
     return sl
 
 def calcular_nivel_take_profit(ativo, df, tipo_operacao, banda_oposta):
     """
     Calcula o nível do take profit com base na estratégia.
     
     Args:
         ativo (str): Símbolo do ativo.
         df (pd.DataFrame): DataFrame com dados de preços e indicadores.
         tipo_operacao (str): 'compra' ou 'venda'.
         banda_oposta (bool): Se True, usa a banda oposta; se False, usa a linha central.
         
     Returns:
         float: Nível do take profit.
     """
     # Índice atual
     i_atual = -1
     
     if not banda_oposta:
         # Primeiro alvo: linha central
         tp = df['bb_middle'].iloc[i_atual]
     else:
         # Segundo alvo: banda oposta
         if tipo_operacao == 'compra':
             tp = df['bb_upper'].iloc[i_atual]
         elif tipo_operacao == 'venda':
             tp = df['bb_lower'].iloc[i_atual]
         else:
             raise ValueError("Tipo de operação inválido. Use 'compra' ou 'venda'.")
     
     return tp
 
 def calcular_distancia_stop_loss(ativo, df, tipo_operacao):
     """
     Calcula a distância do stop loss em pontos.
     
     Args:
         ativo (str): Símbolo do ativo.
         df (pd.DataFrame): DataFrame com dados de preços.
         tipo_operacao (str): 'compra' ou 'venda'.
         
     Returns:
         float: Distância do stop loss em pontos.
     """
     # Índice do candle de sinal (penúltimo candle)
     i_sinal = -2
     
     # Calcular ATR para estimar a volatilidade
     df = calcular_atr(df)
     atr = df['atr'].iloc[i_sinal]
     
     # Usar ATR como base para a distância do stop loss
     # Este é um exemplo; você pode ajustar conforme sua estratégia
     distancia_sl = atr * 1.5  # 1.5 vezes o ATR
     
     return distancia_sl
 
 def aplicar_gestao_risco(ativo, df, tipo_operacao):
     """
     Aplica a gestão de risco para determinar o lote e níveis de SL/TP.
     
     Args:
         ativo (str): Símbolo do ativo.
         df (pd.DataFrame): DataFrame com dados de preços.
         tipo_operacao (str): 'compra' ou 'venda'.
         
     Returns:
         dict: Dicionário com lote, stop loss e take profit.
     """
     # Calcular níveis de SL e TP
     sl = calcular_nivel_stop_loss(ativo, df, tipo_operacao)
     
     # Determinar se usa banda oposta ou linha central para TP
     banda_oposta = TP_OPTION == 2
     tp = calcular_nivel_take_profit(ativo, df, tipo_operacao, banda_oposta)
     
     # Calcular distância do SL para determinar o lote
     distancia_sl = calcular_distancia_stop_loss(ativo, df, tipo_operacao)
     
     # Calcular lote (esta função será implementada no mt5_connection.py)
     # Por enquanto, retornamos os valores calculados
     lote = 0.01  # Valor padrão, será ajustado na implementação real
     
     return {
         'lote': lote,
         'stop_loss': sl,
         'take_profit': tp,
         'distancia_sl': distancia_sl
     }