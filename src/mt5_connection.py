import MetaTrader5 as mt5
import pandas as pd
from src.config import MODO_DEMO

def conectar_mt5():
    """
    Estabelece conexão com o MetaTrader 5.
    
    Returns:
        bool: True se a conexão for bem-sucedida, False caso contrário.
    """
    if not mt5.initialize():
        print("Falha ao inicializar o MetaTrader 5")
        return False
    
    # Configurar conta demo ou real
    if MODO_DEMO:
        # Lógica específica para conta demo, se necessário
        # Por exemplo, selecionar um servidor específico
        pass
    
    return True

def obter_dados_historicos(ativo, timeframe, periodo):
    """
    Obtém dados históricos de um ativo.
    
    Args:
        ativo (str): Símbolo do ativo.
        timeframe: Timeframe MT5 (ex: mt5.TIMEFRAME_D1).
        periodo (int): Número de candles para buscar.
        
    Returns:
        pd.DataFrame: DataFrame com os dados históricos.
    """
    rates = mt5.copy_rates_from_pos(ativo, timeframe, 0, periodo)
    
    if rates is None or len(rates) == 0:
        print(f"Não foi possível obter dados para {ativo}")
        return pd.DataFrame()
    
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    
    return df

def enviar_ordem(ativo, tipo, volume, price, sl, tp, comment=""):
    """
    Envia uma ordem de compra ou venda.
    
    Args:
        ativo (str): Símbolo do ativo.
        tipo (int): Tipo da ordem (mt5.ORDER_TYPE_BUY ou mt5.ORDER_TYPE_SELL).
        volume (float): Volume da ordem.
        price (float): Preço de entrada.
        sl (float): Nível do Stop Loss.
        tp (float): Nível do Take Profit.
        comment (str): Comentário para a ordem.
        
    Returns:
        dict: Resultado da operação de envio da ordem.
    """
    # Preparar a solicitação
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": ativo,
        "volume": volume,
        "type": tipo,
        "price": price,
        "sl": sl,
        "tp": tp,
        "deviation": 20,
        "magic": 10032025,
        "comment": comment,
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    
    # Enviar ordem
    result = mt5.order_send(request)
    
    return result

def calcular_lote(ativo, risco_por_trade, stop_loss_distancia):
    """
    Calcula o volume do lote com base no risco por trade e distância do stop loss.
    
    Args:
        ativo (str): Símbolo do ativo.
        risco_por_trade (float): Percentual do saldo a arriscar.
        stop_loss_distancia (float): Distância do stop loss em pontos.
        
    Returns:
        float: Volume calculado para a ordem.
    """
    # Obter informações do símbolo
    symbol_info = mt5.symbol_info(ativo)
    if symbol_info is None:
        print(f"Não foi possível obter informações para {ativo}")
        return 0.01
    
    # Obter saldo da conta
    account_info = mt5.account_info()
    if account_info is None:
        print("Não foi possível obter informações da conta")
        return 0.01
    
    saldo = account_info.balance
    
    # Calcular risco em valor monetário
    risco_valor = saldo * risco_por_trade
    
    # Converter distância do stop loss para valor monetário
    # Esta é uma aproximação; pode ser necessário ajustar conforme o ativo
    tick_value = symbol_info.trade_tick_value
    tick_size = symbol_info.trade_tick_size
    
    # Calcular pontos por tick
    pontos_por_tick = tick_value / tick_size if tick_size > 0 else 1
    
    # Converter distância em pontos para valor monetário
    sl_valor = stop_loss_distancia * pontos_por_tick
    
    # Calcular lote
    if sl_valor > 0:
        lote = risco_valor / sl_valor
    else:
        lote = 0.01
    
    # Arredondar para o lote mínimo permitido
    lote = round(lote, 2)
    lote_min = symbol_info.volume_min
    lote_max = symbol_info.volume_max
    lote_step = symbol_info.volume_step
    
    # Ajustar o lote para estar dentro dos limites e incrementos permitidos
    if lote < lote_min:
        lote = lote_min
    elif lote > lote_max:
        lote = lote_max
    else:
        # Arredondar para o incremento mais próximo
        lote = round(lote / lote_step) * lote_step
    
    return lote