# Robô de Trading com Bandas de Bollinger

Este projeto implementa um robô de trading automático em Python utilizando a API do MetaTrader 5. A estratégia baseia-se nas Bandas de Bollinger no gráfico diário, com regras específicas de entrada, saída, gestão de risco e um filtro de mercado usando o indicador ADX. Além disso, incorpora um modelo de Aprendizado de Máquina para validar sinais de trade.

## Estratégia

- **Indicador**: Bandas de Bollinger (período = 20, desvio padrão = 2)
- **Timeframe**: Diário
- **Regras de Entrada**:
    - **COMPRA**:
        1. O candle do dia fecha **abaixo** da banda inferior.
        2. O candle seguinte fecha **acima** da banda inferior.
    - **VENDA**:
        1. O candle do dia fecha **acima** da banda superior.
        2. O candle seguinte fecha **abaixo** da banda superior.
- **Take Profit**:
    - Opção 1: Linha central (média móvel).
    - Opção 2: Banda oposta à de entrada.
- **Stop Loss**: Fixo logo após a máxima/mínima do candle de sinal.
- **Filtro de Mercado**: Operar apenas se ADX < 25 (mercado lateralizado).
- **Multiativos**: Monitora uma lista de ativos (pares de moedas forex + XAUUSD).
- **Gestão de Risco**: Risco configurável por trade (ex: 1% do saldo).
- **Aprendizado de Máquina**: Modelo classifica novos sinais como "bons" ou "ruins" com base no histórico.

## Estrutura do Projeto

```
│
├── data/                   # Armazena dados históricos e arquivos CSV de trades
│   ├── trades_log.csv
│   ├── market_data.csv
│   ├── decisions_log.csv
│
├── models/                 # Modelos treinados da IA
│   ├── bollinger_ai.pkl
│
├── src/                    # Código-fonte do robô
│   ├── __init__.py
│   ├── config.py           # Configurações gerais do robô
│   ├── indicators.py       # Cálculo das Bandas de Bollinger, ADX, etc.
│   ├── strategy.py         # Lógica principal da estratégia
│   ├── risk_management.py  # Gestão de risco e cálculo de lote
│   ├── ai_model.py         # Treinamento e previsão com IA
│   ├── mt5_connection.py   # Conexão e funções de envio de ordens no MT5
│   ├── backtest.py         # Backtesting da estratégia
│   ├── main.py             # Script principal para rodar o robô
│
├── tests/                  # Testes unitários e de integração
│   ├── test_strategy.py
│   ├── test_ai_model.py
│
├── requirements.txt        # Dependências do projeto
├── README.md               # Documentação do projeto
├── CORRECOES.md            # Registro de correções e melhorias
```

## Configuração

1.  Instale as dependências: `pip install -r requirements.txt`
2.  Configure os parâmetros no arquivo `src/config.py`.
3.  Certifique-se de ter o MetaTrader 5 instalado e configurado para permitir conexões via API.

## Execução

- Para rodar o robô em tempo real: `python src/main.py`
- Para executar um backtest: `python src/backtest.py`

## Aprendizado de Máquina

O modelo de IA é treinado periodicamente com os dados dos trades anteriores. Ele analisa as condições de mercado no momento da entrada e classifica o potencial do sinal antes da execução.

## Registro de Correções

Consulte o arquivo `CORRECOES.md` para informações detalhadas sobre as correções de bugs e melhorias implementadas.