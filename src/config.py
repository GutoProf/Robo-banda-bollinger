# Configurações gerais do robô

# Parâmetros da estratégia
BB_PERIOD = 20
BB_STDDEV = 2
ADX_PERIOD = 14

# Lista de ativos a serem monitorados
ATIVOS = [
    "EURUSD", "GBPUSD", "USDJPY", "USDCAD", "USDCHF",
    "AUDUSD", "NZDUSD", "XAUUSD"
]

# Gestão de risco
RISCO_POR_TRADE = 0.01  # 1% do saldo
MAX_RISCO_DIARIO = 0.05 # 5% do saldo

# Configurações de Take Profit
# 1 para linha central, 2 para banda oposta
TP_OPTION = 2

# Modo de operação
# True para conta demo, False para conta real
MODO_DEMO = True

# Configurações do Aprendizado de Máquina
RETRAIN_INTERVAL = 7  # Re-treinar a cada 7 dias
MIN_TRADES_FOR_AI = 20 # Mínimo de trades para ativar a IA