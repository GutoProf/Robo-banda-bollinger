import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib
from src.config import MIN_TRADES_FOR_AI
import os

# Caminho para o modelo treinado
MODEL_PATH = "models/bollinger_ai.pkl"

def extrair_caracteristicas(df, index):
    """
    Extrai características do mercado no momento da entrada.
    
    Args:
        df (pd.DataFrame): DataFrame com dados de preços e indicadores.
        index (int): Índice do candle de entrada.
        
    Returns:
        dict: Dicionário com as características extraídas.
    """
    if index < 20:  # Precisamos de pelo menos 20 candles para os indicadores
        return None
    
    # Calcular posição relativa do preço em relação às bandas de Bollinger
    bb_upper = df['bb_upper'].iloc[index]
    bb_lower = df['bb_lower'].iloc[index]
    close = df['close'].iloc[index]
    
    # Evitar divisão por zero
    bb_width = bb_upper - bb_lower
    if bb_width == 0:
        bb_position = 0.5
    else:
        bb_position = (close - bb_lower) / bb_width
    
    # Calcular volatilidade
    bb_middle = df['bb_middle'].iloc[index]
    if bb_middle == 0:
        volatility = 0
    else:
        volatility = bb_width / bb_middle
    
    # Calcular RSI se disponível
    rsi = df['rsi'].iloc[index] if 'rsi' in df.columns else 0
    
    # Calcular posição do MACD se disponível
    macd_position = 0
    if 'macd' in df.columns and 'macd_signal' in df.columns:
        macd = df['macd'].iloc[index]
        macd_signal = df['macd_signal'].iloc[index]
        # Evitar divisão por zero
        if macd_signal != 0:
            macd_position = macd / macd_signal
    
    # Calcular posição do Stochastic se disponível
    stochastic_position = 0
    if 'slowk' in df.columns and 'slowd' in df.columns:
        slowk = df['slowk'].iloc[index]
        slowd = df['slowd'].iloc[index]
        # Evitar divisão por zero
        if slowd != 0:
            stochastic_position = slowk / slowd
    
    caracteristicas = {
        'bb_position': bb_position,
        'adx': df['adx'].iloc[index],
        'volatility': volatility,
        'rsi': rsi,
        'macd_position': macd_position,
        'stochastic_position': stochastic_position,
        'day_of_week': df['time'].iloc[index].dayofweek,
        'hour': df['time'].iloc[index].hour,
    }
    
    return caracteristicas

def treinar_modelo(dados_trades):
    """
    Treina o modelo de Aprendizado de Máquina com os dados de trades.
    
    Args:
        dados_trades (pd.DataFrame): DataFrame com dados de trades e resultados.
        
    Returns:
        object: Modelo treinado ou None se não houver dados suficientes.
    """
    if len(dados_trades) < MIN_TRADES_FOR_AI:
        print(f"Não há dados suficientes para treinar o modelo. Mínimo necessário: {MIN_TRADES_FOR_AI}")
        return None
    
    # Preparar os dados para treinamento
    caracteristicas_cols = ['bb_position', 'adx', 'volatility', 'rsi', 'macd_position', 'stochastic_position', 'day_of_week', 'hour']
    X = dados_trades[caracteristicas_cols]
    y = dados_trades['resultado']  # 1 para lucro, 0 para prejuízo
    
    # Dividir os dados em treinamento e teste
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Criar e treinar o modelo
    modelo = RandomForestClassifier(n_estimators=100, random_state=42)
    modelo.fit(X_train, y_train)
    
    # Avaliar o modelo
    y_pred = modelo.predict(X_test)
    acuracia = accuracy_score(y_test, y_pred)
    print(f"Acurácia do modelo: {acuracia:.2f}")
    
    # Salvar o modelo
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    joblib.dump(modelo, MODEL_PATH)
    
    return modelo

def carregar_modelo():
    """
    Carrega o modelo treinado do disco.
    
    Returns:
        object: Modelo carregado ou None se o arquivo não existir.
    """
    if not os.path.exists(MODEL_PATH):
        print("Modelo não encontrado.")
        return None
    
    modelo = joblib.load(MODEL_PATH)
    return modelo

def prever_qualidade_sinal(modelo, caracteristicas):
    """
    Usa o modelo para prever a qualidade de um sinal.
    
    Args:
        modelo (object): Modelo treinado.
        caracteristicas (dict): Características do sinal.
        
    Returns:
        int: 1 se o sinal for classificado como bom, 0 se ruim.
    """
    if modelo is None:
        # Se não houver modelo, assumir que o sinal é bom
        return 1
    
    # Converter características para o formato esperado pelo modelo
    caracteristicas_array = np.array([[
        caracteristicas['bb_position'],
        caracteristicas['adx'],
        caracteristicas['volatility'],
        caracteristicas['rsi'],
        caracteristicas['macd_position'],
        caracteristicas['stochastic_position'],
        caracteristicas['day_of_week'],
        caracteristicas['hour']
    ]])
    
    # Fazer a previsão
    previsao = modelo.predict(caracteristicas_array)
    
    return previsao[0]