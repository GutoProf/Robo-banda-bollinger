import pandas as pd
import numpy as np
from src.indicators import calcular_bandas_bollinger, calcular_adx, calcular_rsi, calcular_macd, calcular_stochastic

def verificar_sinal_compra(df):
    """
    Verifica se há um sinal de compra de acordo com a estratégia.
    
    Args:
        df (pd.DataFrame): DataFrame com dados de preços e indicadores.
        
    Returns:
        bool: True se houver sinal de compra, False caso contrário.
    """
    if len(df) < 3:
        return False
        
    # Índices dos últimos candles
    i_anterior = -2
    i_atual = -1
    
    # Regras de compra
    # 1. O candle anterior fecha abaixo da banda inferior
    # 2. O candle atual fecha acima da banda inferior
    if (df['close'].iloc[i_anterior] < df['bb_lower'].iloc[i_anterior] and
        df['close'].iloc[i_atual] > df['bb_lower'].iloc[i_atual]):
        return True
        
    return False

def verificar_sinal_venda(df):
    """
    Verifica se há um sinal de venda de acordo com a estratégia.
    
    Args:
        df (pd.DataFrame): DataFrame com dados de preços e indicadores.
        
    Returns:
        bool: True se houver sinal de venda, False caso contrário.
    """
    if len(df) < 3:
        return False
        
    # Índices dos últimos candles
    i_anterior = -2
    i_atual = -1
    
    # Regras de venda
    # 1. O candle anterior fecha acima da banda superior
    # 2. O candle atual fecha abaixo da banda superior
    if (df['close'].iloc[i_anterior] > df['bb_upper'].iloc[i_anterior] and
        df['close'].iloc[i_atual] < df['bb_upper'].iloc[i_atual]):
        return True
        
    return False

def preparar_dados_para_estrategia(df):
    """
    Prepara os dados calculando os indicadores necessários.
    
    Args:
        df (pd.DataFrame): DataFrame com dados de preços.
        
    Returns:
        pd.DataFrame: DataFrame com indicadores calculados.
    """
    df = calcular_bandas_bollinger(df)
    df = calcular_adx(df)
    df = calcular_rsi(df)
    df = calcular_macd(df)
    df = calcular_stochastic(df)
    
    return df

def filtrar_mercado_lateralizado(df, limiar_adx=25):
    """
    Verifica se o mercado está lateralizado usando o ADX.
    
    Args:
        df (pd.DataFrame): DataFrame com dados de preços e indicador ADX.
        limiar_adx (int): Valor limite do ADX para considerar mercado lateralizado.
        
    Returns:
        bool: True se o mercado está lateralizado, False caso contrário.
    """
    if len(df) < 1 or pd.isna(df['adx'].iloc[-1]):
        return False
        
    return df['adx'].iloc[-1] < limiar_adx