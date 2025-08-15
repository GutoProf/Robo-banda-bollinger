import pandas as pd
import numpy as np
import talib as ta

def calcular_bandas_bollinger(df, periodo=20, desvio_padrao=2):
    """
    Calcula as Bandas de Bollinger para um DataFrame de preços.
    
    Args:
        df (pd.DataFrame): DataFrame com colunas 'high', 'low', 'close'.
        periodo (int): Período para calcular a média móvel.
        desvio_padrao (int): Número de desvios padrões para as bandas.
        
    Returns:
        pd.DataFrame: DataFrame com as colunas adicionais 'bb_upper', 'bb_middle', 'bb_lower'.
    """
    df = df.copy()
    df['bb_middle'] = ta.SMA(df['close'], timeperiod=periodo)
    df['bb_upper'] = df['bb_middle'] + (ta.STDDEV(df['close'], timeperiod=periodo) * desvio_padrao)
    df['bb_lower'] = df['bb_middle'] - (ta.STDDEV(df['close'], timeperiod=periodo) * desvio_padrao)
    
    return df

def calcular_adx(df, periodo=14):
    """
    Calcula o ADX para um DataFrame de preços.
    
    Args:
        df (pd.DataFrame): DataFrame com colunas 'high', 'low', 'close'.
        periodo (int): Período para calcular o ADX.
        
    Returns:
        pd.DataFrame: DataFrame com a coluna adicional 'adx'.
    """
    df = df.copy()
    df['adx'] = ta.ADX(df['high'], df['low'], df['close'], timeperiod=periodo)
    
    return df

def calcular_atr(df, periodo=14):
    """
    Calcula o ATR (Average True Range) para um DataFrame de preços.
    
    Args:
        df (pd.DataFrame): DataFrame com colunas 'high', 'low', 'close'.
        periodo (int): Período para calcular o ATR.
        
    Returns:
        pd.DataFrame: DataFrame com a coluna adicional 'atr'.
    """
    df = df.copy()
    df['atr'] = ta.ATR(df['high'], df['low'], df['close'], timeperiod=periodo)
    
    return df