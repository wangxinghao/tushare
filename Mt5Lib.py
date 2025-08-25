import MetaTrader5 as mt5
import pandas as pd
import time
from datetime import datetime, timedelta
import logging


logger = logging.getLogger('app')

TIMEFRAME_M15 = mt5.TIMEFRAME_M15
TIMEFRAME_M1 = mt5.TIMEFRAME_M1
TIMEFRAME_M5 = mt5.TIMEFRAME_M5
ORDER_TYPE_BUY = mt5.ORDER_TYPE_BUY
ORDER_TYPE_SELL = mt5.ORDER_TYPE_SELL

POSITION_TYPE_BUY = mt5.POSITION_TYPE_BUY
POSITION_TYPE_SELL = mt5.POSITION_TYPE_SELL


def shutdown():
    mt5.shutdown()
    
def positions_get(symbol):
    return mt5.positions_get(symbol=symbol)


# 发送订单
def send_order(symbol, volume, order_type):
    """
    发送交易订单
    symbol: 交易品种
    volume: 交易量(手)
    order_type: 订单类型, mt5.ORDER_TYPE_BUY或mt5.ORDER_TYPE_SELL
    """
    # 获取当前报价
    tick = mt5.symbol_info_tick(symbol)
    if tick is None:
        logger.info(f"获取{symbol}报价失败, 错误代码: {mt5.last_error()}")
        return False
    
    # 准备订单请求
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": volume,
        "type": order_type,
        "price": tick.ask if order_type == ORDER_TYPE_BUY else tick.bid,
        "deviation": 1,  # 允许的滑点(点)
        "type_time": mt5.ORDER_TIME_GTC,  # 订单有效期: 永久有效
        "type_filling": mt5.ORDER_FILLING_FOK,  # 成交方式: 立即全部成交否则取消
    }
    
    # 发送订单
    result = mt5.order_send(request)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        logger.info(f"订单发送失败, 错误代码: {result.retcode}, 错误信息: {result.comment}")
        return False
    
    logger.info(f"订单执行成功, 订单号: {result.order}")
    return True


# 平仓指定订单
def close_position(symbol, ticket, order_type, volume):
    """
    平仓指定订单
    symbol: 交易品种
    ticket: 订单号
    order_type: 原订单类型
    volume: 交易量
    """
    # 确定平仓类型 (买单用卖价平仓，卖单用买价平仓)
    close_type = mt5.ORDER_TYPE_SELL if order_type == ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY
    
    # 获取当前报价
    tick = mt5.symbol_info_tick(symbol)
    if tick is None:
        logger.info(f"获取{symbol}报价失败, 错误代码: {mt5.last_error()}")
        return False
    
    # 准备平仓请求
    price = tick.bid if close_type == mt5.ORDER_TYPE_SELL else tick.ask

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": volume,
        "type": close_type,
        "position": ticket,
        "price": price,
        "deviation": 1,
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_FOK
    }
    
    # 发送平仓订单
    logger.info(f"begin close!")

    result = mt5.order_send(request)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        logger.info(f"平仓失败, 错误代码: {result.retcode}, 错误信息: {result.comment}")
        return False
    
    logger.info(f"平仓成功, 订单号: {result.order}")
    return True


# 初始化MT5连接
def initialize_mt5():
    if not mt5.initialize():
        logger.info(f"初始化MT5失败, 错误代码: {mt5.last_error()}")
        return False
    logger.info("MT5初始化成功")
    return True

# 获取历史数据
def get_historical_data(symbol, timeframe, count):
    """
    获取指定交易品种的历史K线数据
    symbol: 交易品种，如"EURUSD"
    timeframe: 时间周期，如mt5.TIMEFRAME_H1
    count: 获取的K线数量
    """
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, count)
    if rates is None:
        logger.info(f"获取{symbol}数据失败, 错误代码: {mt5.last_error()}")
        return None
    
    # 转换为DataFrame
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    return df