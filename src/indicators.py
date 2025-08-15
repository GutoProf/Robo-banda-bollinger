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

def calcular_rsi(df, periodo=14):
    """
    Calcula o RSI (Relative Strength Index) para um DataFrame de preços.
    
    Args:
        df (pd.DataFrame): DataFrame com coluna 'close'.
        periodo (int): Período para calcular o RSI.
        
    Returns:
        pd.DataFrame: DataFrame com a coluna adicional 'rsi'.
    """
    df = df.copy()
    df['rsi'] = ta.RSI(df['close'], timeperiod=periodo)
    
    return df

def calcular_macd(df, fastperiod=12, slowperiod=26, signalperiod=9):
    """
    Calcula o MACD (Moving Average Convergence Divergence) para um DataFrame de preços.
    
    Args:
        df (pd.DataFrame): DataFrame com coluna 'close'.
        fastperiod (int): Período para a média móvel rápida.
        slowperiod (int): Período para a média móvel lenta.
        signalperiod (int): Período para a linha de sinal.
        
    Returns:
        pd.DataFrame: DataFrame com as colunas adicionais 'macd' e 'macd_signal'.
    """
    df = df.copy()
    df['macd'], df['macd_signal'], _ = ta.MACD(df['close'], fastperiod=fastperiod, slowperiod=slowperiod, signalperiod=signalperiod)
    
    return df

def calcular_stochastic(df, fastk_period=14, slowk_period=3, slowd_period=3):
    """
    Calcula o Stochastic Oscillator para um DataFrame de preços.
    
    Args:
        df (pd.DataFrame): DataFrame com colunas 'high', 'low', 'close'.
        fastk_period (int): Período para o %K rápido.
        slowk_period (int): Período para o %K lento.
        slowd_period (int): Período para o %D.
        
    Returns:
        pd.DataFrame: DataFrame com as colunas adicionais 'slowk' e 'slowd'.
    """
    df = df.copy()
    df['slowk'], df['slowd'] = ta.STOCH(df['high'], df['low'], df['close'], 
                                       fastk_period=fastk_period, 
                                       slowk_period=slowk_period, 
                                       slowk_matype=0, 
                                       slowd_period=slowd_period, 
                                       slowd_matype=0)
    
    return df