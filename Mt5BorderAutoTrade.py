import pandas as pd
from datetime import datetime, timedelta
import Mt5Lib
import TradeUtils
from logging.handlers import TimedRotatingFileHandler
import logConfig
import context



FIVE_MIN_OPEN_FLAG = False 
FIVE_MIN_VOLUME_FLAG = False



# 检查当前持仓
def close_position_if_neccessary(symbol,positions,current_price,close_point,box_high,box_low):
    global FIVE_MIN_OPEN_FLAG, FIVE_MIN_VOLUME_FLAG,TARGET_OBJECT_PRICE_1,TARGET_OBJECT_PRICE_2
    df5 = Mt5Lib.get_historical_data(symbol, Mt5Lib.TIMEFRAME_M5, 3)
    m5_entity_min = min(df5.iloc[-2]['close'],df5.iloc[-2]['open'])
    logger.info(f'上一m5 least {m5_entity_min}')
    m5_entity_max = max(df5.iloc[-2]['close'],df5.iloc[-2]['open'])
    logger.info(f'上一m5 most {m5_entity_max}')
    df1 = Mt5Lib.get_historical_data(symbol, Mt5Lib.TIMEFRAME_M1, 3)
    for position in positions:
        # 对于买单，如果当前价格低于开仓价格4点则平仓
        if position.type == Mt5Lib.POSITION_TYPE_BUY:
            # 平仓判断
            loss_points = position.price_open - current_price
            if loss_points >= close_point:
                logger.info(f"做多仓位 {position.price_open} 点，现在为{current_price}，达到{close_point}点close条件，平仓")
                Mt5Lib.close_position(symbol, position.ticket, Mt5Lib.ORDER_TYPE_BUY, position.volume)
                FIVE_MIN_OPEN_FLAG,FIVE_MIN_VOLUME_FLAG,TARGET_OBJECT_PRICE_1,TARGET_OBJECT_PRICE_2 \
                    = False,False,0,0
            elif box_high >= current_price:
                logger.info(f"做多仓位 {position.price_open} 点，现在为{current_price}， is in box {box_high} close条件，平仓")   
                Mt5Lib.close_position(symbol, position.ticket, Mt5Lib.ORDER_TYPE_BUY, position.volume)
                FIVE_MIN_OPEN_FLAG,FIVE_MIN_VOLUME_FLAG,TARGET_OBJECT_PRICE_1,TARGET_OBJECT_PRICE_2 \
                    = False,False,0,0
            elif not FIVE_MIN_VOLUME_FLAG and FIVE_MIN_OPEN_FLAG and df5.iloc[-2]['high'] < df5.iloc[-3]['high'] :
                logger.info(f"做多仓位 {position.price_open} 点，现在为{current_price}，last m5 dose not high enough  close条件，平仓")
                Mt5Lib.close_position(symbol, position.ticket, Mt5Lib.ORDER_TYPE_BUY, position.volume)
                FIVE_MIN_OPEN_FLAG,FIVE_MIN_VOLUME_FLAG,TARGET_OBJECT_PRICE_1,TARGET_OBJECT_PRICE_2 \
                    = False,False,0,0
            elif m5_entity_min >= current_price:
                logger.info(f"做多仓位 {position.price_open} 点，现在为{current_price}，is less than m5 {m5_entity_min} close条件，平仓")
                Mt5Lib.close_position(symbol, position.ticket, Mt5Lib.ORDER_TYPE_BUY, position.volume)
                FIVE_MIN_OPEN_FLAG,FIVE_MIN_VOLUME_FLAG,TARGET_OBJECT_PRICE_1,TARGET_OBJECT_PRICE_2 \
                    = False,False,0,0
            elif TARGET_OBJECT_PRICE_1 > 0 and current_price >= TARGET_OBJECT_PRICE_1:
                logger.info(f"做空仓位 {position.price_open} 点，现在为{current_price}，is more than TARGET_OBJECT_PRICE_1 {TARGET_OBJECT_PRICE_1} close条件，平仓")
                Mt5Lib.close_position(symbol, position.ticket, Mt5Lib.ORDER_TYPE_BUY, position.volume/2)
                FIVE_MIN_OPEN_FLAG,FIVE_MIN_VOLUME_FLAG,TARGET_OBJECT_PRICE_1,TARGET_OBJECT_PRICE_2 \
                    = False,False,0,0
            elif TARGET_OBJECT_PRICE_2 > 0 and current_price >= TARGET_OBJECT_PRICE_2:
                logger.info(f"做空仓位 {position.price_open} 点，现在为{current_price}，is more than TARGET_OBJECT_PRICE_1 {TARGET_OBJECT_PRICE_2} close条件，平仓")
                Mt5Lib.close_position(symbol, position.ticket, Mt5Lib.ORDER_TYPE_BUY, position.volume)
                FIVE_MIN_OPEN_FLAG,FIVE_MIN_VOLUME_FLAG,TARGET_OBJECT_PRICE_1,TARGET_OBJECT_PRICE_2 \
                    = False,False,0,0
            elif (df1.iloc[-1]['close'] - df1.iloc[-1]['open'] < 0) and (df1.iloc[-2]['close'] - df1.iloc[-2]['open'] < 0) \
                and (df1.iloc[-3]['close'] - df1.iloc[-3]['open'] < 0):
                logger.info(f"做空仓位 {position.price_open} 点，现在为{current_price}， 三根1m close条件，平仓")
                Mt5Lib.close_position(symbol, position.ticket, Mt5Lib.ORDER_TYPE_BUY, position.volume)
                FIVE_MIN_OPEN_FLAG,FIVE_MIN_VOLUME_FLAG,TARGET_OBJECT_PRICE_1,TARGET_OBJECT_PRICE_2 \
                    = False,False,0,0
                                    
        # 对于卖单，如果当前价格高于开仓价格4点则平仓
        elif position.type == Mt5Lib.POSITION_TYPE_SELL:
            # 平仓判断
            loss_points = current_price - position.price_open
            if loss_points >= close_point:
                logger.info(f"做空仓位 {position.price_open} 点，现在为{current_price}，达到{close_point}点close条件，平仓")
                Mt5Lib.close_position(symbol, position.ticket, Mt5Lib.ORDER_TYPE_SELL, position.volume)
                FIVE_MIN_OPEN_FLAG,FIVE_MIN_VOLUME_FLAG,TARGET_OBJECT_PRICE_1,TARGET_OBJECT_PRICE_2 \
                    = False,False,0,0
            elif box_low <= current_price:
                logger.info(f"做空仓位 {position.price_open} 点，现在为{current_price}，is in box {box_low}点close条件，平仓")
                Mt5Lib.close_position(symbol, position.ticket, Mt5Lib.ORDER_TYPE_SELL, position.volume)
                FIVE_MIN_OPEN_FLAG,FIVE_MIN_VOLUME_FLAG,TARGET_OBJECT_PRICE_1,TARGET_OBJECT_PRICE_2 \
                    = False,False,0,0
            elif not FIVE_MIN_VOLUME_FLAG and FIVE_MIN_OPEN_FLAG and df5.iloc[-2]['low'] > df5.iloc[-3]['low'] :
                logger.info(f"做多仓位 {position.price_open} 点，现在为{current_price}，last m5 dose not high enough  close条件，平仓")
                Mt5Lib.close_position(symbol, position.ticket, Mt5Lib.ORDER_TYPE_BUY, position.volume)
                FIVE_MIN_OPEN_FLAG,FIVE_MIN_VOLUME_FLAG,TARGET_OBJECT_PRICE_1,TARGET_OBJECT_PRICE_2 \
                    = False,False,0,0
            elif m5_entity_max <= current_price:
                logger.info(f"做空仓位 {position.price_open} 点，现在为{current_price}，is more than m5 {m5_entity_max} close条件，平仓")
                Mt5Lib.close_position(symbol, position.ticket, Mt5Lib.ORDER_TYPE_SELL, position.volume)
                FIVE_MIN_OPEN_FLAG,FIVE_MIN_VOLUME_FLAG,TARGET_OBJECT_PRICE_1,TARGET_OBJECT_PRICE_2 \
                    = False,False,0,0
            elif TARGET_OBJECT_PRICE_1 >0 and current_price <= TARGET_OBJECT_PRICE_1:
                logger.info(f"做空仓位 {position.price_open} 点，现在为{current_price}，is less than TARGET_OBJECT_PRICE_1 {TARGET_OBJECT_PRICE_1} close条件，平仓")
                Mt5Lib.close_position(symbol, position.ticket, Mt5Lib.ORDER_TYPE_SELL, position.volume/2)
                FIVE_MIN_OPEN_FLAG,FIVE_MIN_VOLUME_FLAG,TARGET_OBJECT_PRICE_1,TARGET_OBJECT_PRICE_2 \
                    = False,False,0,0
            elif TARGET_OBJECT_PRICE_2 >0 and current_price <= TARGET_OBJECT_PRICE_2:
                logger.info(f"做空仓位 {position.price_open} 点，现在为{current_price}，is less than TARGET_OBJECT_PRICE_2 {TARGET_OBJECT_PRICE_2} close条件，平仓")
                Mt5Lib.close_position(symbol, position.ticket, Mt5Lib.ORDER_TYPE_SELL, position.volume)
                FIVE_MIN_OPEN_FLAG,FIVE_MIN_VOLUME_FLAG,TARGET_OBJECT_PRICE_1,TARGET_OBJECT_PRICE_2 \
                    = False,False,0,0
            elif (df1.iloc[-1]['close'] - df1.iloc[-1]['open'] < 0) and (df1.iloc[-2]['close'] - df1.iloc[-2]['open'] < 0) \
                and (df1.iloc[-3]['close'] - df1.iloc[-3]['open'] < 0):
                logger.info(f"做多仓位 {position.price_open} 点，现在为{current_price}，三根1m close条件，平仓")
                Mt5Lib.close_position(symbol, position.ticket, Mt5Lib.ORDER_TYPE_BUY, position.volume)
                FIVE_MIN_OPEN_FLAG,FIVE_MIN_VOLUME_FLAG,TARGET_OBJECT_PRICE_1,TARGET_OBJECT_PRICE_2 \
                    = False,False,0,0

def tagetPrice(symbol,current_price,POSITION_TYPE):
    df15 = Mt5Lib.get_historical_data(symbol, Mt5Lib.TIMEFRAME_M5, 200)
    if POSITION_TYPE == Mt5Lib.POSITION_TYPE_BUY:
        peaks = TradeUtils.find_high_peaks_with_2_point_window(df15, current_price)
        target_price_1, target_price_2 = TradeUtils.process_target_prices(peaks)
        return target_price_1, target_price_2
    elif POSITION_TYPE == Mt5Lib.POSITION_TYPE_SELL:
        troughs = TradeUtils.find_low_troughs_with_2_point_window(df15, current_price)
        target_price_1, target_price_2 = TradeUtils.process_target_prices(troughs)
        return target_price_1, target_price_2
    return 0, 0

           
def open_position_if_neccessary(symbol,current_price,box_high,box_low,volume):
    global FIVE_MIN_OPEN_FLAG, FIVE_MIN_VOLUME_FLAG,TARGET_OBJECT_PRICE_1,TARGET_OBJECT_PRICE_2
    df5 = Mt5Lib.get_historical_data(symbol, Mt5Lib.TIMEFRAME_M5, 4)
    m5_low = df5.iloc[-2]['low']
    logger.info(f'上一m5 low {m5_low}')
    m5_high = df5.iloc[-2]['high']
    logger.info(f'上一m5 high {m5_high}')
    if current_price > min(df5.iloc[-2]['close'],df5.iloc[-2]['high']) and current_price < max(df5.iloc[-2]['close'],df5.iloc[-2]['high']) :
        logger.info(f"价格在m5实体区间内，不做处理")
        return
    print(df5)
    df1 = Mt5Lib.get_historical_data(symbol, Mt5Lib.TIMEFRAME_M1, 3)
    current_price = df1.iloc[-1]['close']
    #5分钟量能关系
    now = datetime.now()
    minutes_in_interval = now.minute % 5
    seconds_in_interval = now.second
    weight = (minutes_in_interval*60 + seconds_in_interval)/300 + 0.05
    last_two_tick_volume_change =  df5.iloc[3]['tick_volume']/(weight) 
    first_two_tick_volume_change = (df5.iloc[1]['tick_volume'] + df5.iloc[2]['tick_volume'])/2 * 1.1 + 50
    FIVE_MIN_VOLUME_FLAG = last_two_tick_volume_change > first_two_tick_volume_change  
    logger.info(f'5分钟成交量first_two_tick_volume:{first_two_tick_volume_change}, last_two_tick_volume:{last_two_tick_volume_change},FIVE_MIN_VOLUME_FLAG:{FIVE_MIN_VOLUME_FLAG},weight:{weight}')
    # 突破上沿, 做多
    if  current_price > box_high and current_price > m5_high:
        if not FIVE_MIN_VOLUME_FLAG and df5.iloc[-2]['close'] > box_high and df5.iloc[-1]['high'] > df5.iloc[-2]['high'] and df5.iloc[-2]['high'] > df5.iloc[-3]['high'] \
            and df1.iloc[-2]['close'] > box_high  and df1.iloc[-1]['high'] > df1.iloc[-2]['high'] and df1.iloc[-2]['high'] > df1.iloc[-3]['high']:
            FIVE_MIN_OPEN_FLAG = True
            logger.info(f"价格突破箱体上沿 {box_high}, 发送买入订单")
            Mt5Lib.send_order(symbol, volume, Mt5Lib.ORDER_TYPE_BUY)
            TARGET_OBJECT_PRICE_1,TARGET_OBJECT_PRICE_2 = tagetPrice(symbol,current_price,Mt5Lib.ORDER_TYPE_BUY)
        elif FIVE_MIN_VOLUME_FLAG:
            logger.info(f"价格突破箱体上沿 {box_high}, 发送买入订单")
            Mt5Lib.send_order(symbol, volume, Mt5Lib.ORDER_TYPE_BUY)
            TARGET_OBJECT_PRICE_1,TARGET_OBJECT_PRICE_2 = tagetPrice(symbol,current_price,Mt5Lib.ORDER_TYPE_BUY)
    # 跌破下沿, 做空
    elif  current_price < box_low and current_price < m5_low:
        if not FIVE_MIN_VOLUME_FLAG and df5.iloc[-2]['close'] < box_low and  df5.iloc[-1]['low']<df5.iloc[-2]['low'] and df5.iloc[-2]['low'] < df5.iloc[-3]['low']\
            and df1.iloc[-2]['close'] < box_low and df1.iloc[-1]['low'] < df1.iloc[-2]['low'] and df1.iloc[-2]['low'] < df1.iloc[-3]['low']:
            logger.info(f"价格跌破箱体下沿 {box_low}, 发送卖出订单")
            Mt5Lib.send_order(symbol, volume, Mt5Lib.ORDER_TYPE_SELL)
            TARGET_OBJECT_PRICE_1,TARGET_OBJECT_PRICE_2 = tagetPrice(symbol,current_price,Mt5Lib.ORDER_TYPE_SELL)
        elif FIVE_MIN_VOLUME_FLAG:
            logger.info(f"价格跌破箱体下沿 {box_low}, 发送卖出订单")
            Mt5Lib.send_order(symbol, volume, Mt5Lib.ORDER_TYPE_SELL)
            TARGET_OBJECT_PRICE_1,TARGET_OBJECT_PRICE_2 = tagetPrice(symbol,current_price,Mt5Lib.ORDER_TYPE_SELL)
    logger.info(f"1目标价格:{TARGET_OBJECT_PRICE_1}，   2目标价格:{TARGET_OBJECT_PRICE_2}")
# 箱体突破策略主函数
def box_breakout_strategy(symbol, timeframe, volume, close_point):
    logger.info(f"开始运行箱体突破策略 - 品种: {symbol}, 周期: {timeframe}, 箱体周期: {context.GOBAL_BOX_PERIOD}")
    while True:
        box_high, box_low = 0,0
        hasPosition= False
        current_price = 0
        try:
            # 检查当前持仓
            positions = Mt5Lib.positions_get(symbol=symbol)
            hasPosition = positions is not None and len(positions) != 0
            
            # 获取历史数据
            df = Mt5Lib.get_historical_data(symbol, timeframe, context.GOBAL_BOX_PERIOD + 1)
            logger.info(df)
            
            if df is None or len(df) < context.GOBAL_BOX_PERIOD + 1:
                TradeUtils.wait_for_time(False,0)
                continue
            # 计算箱体区间
            box_high, box_low = TradeUtils.check_and_calculate_box(df, context.GOBAL_BOX_PERIOD)
            if box_high is None or box_low is None:
                logger.info(f"箱体区间不成立")
                TradeUtils.wait_for_time(False,0)
                continue
            # 获取最新价格
            current_price = df.iloc[-1]['close']
            current_time = df.iloc[-1]['time']
            # 打印当前状态
            logger.info(f"\n时间: {current_time},当前价格: {current_price},箱体区间: {box_low} - {box_high}")
            
            # 如果有持仓，检查是否need close
            if hasPosition:
                close_position_if_neccessary(symbol, positions,current_price, close_point,box_high, box_low)
            else:
                open_position_if_neccessary(symbol, current_price,box_high, box_low,volume)
        except Exception as e:
            logger.info(f"策略运行出错: {str(e)}")
        
        TradeUtils.wait_for_time(hasPosition, current_price, box_high, box_low)

# 主程序
if __name__ == "__main__":
    
    logger = logConfig.setup_logger()

    # 策略参数
    SYMBOL = "XAUUSD"  # 交易品种
    TIMEFRAME = Mt5Lib.TIMEFRAME_M15  # 时间周期 (15分钟)
    VOLUME = 0.1  # 交易量 (0.1手)
    CLOSE_POINTS = 4
    
    # 初始化MT5
    if Mt5Lib.initialize_mt5():
        try:
            # 运行策略
            box_breakout_strategy(SYMBOL, TIMEFRAME, VOLUME, CLOSE_POINTS)
        finally:
            # 断开MT5连接
            Mt5Lib.shutdown()
            logger.info("MT5连接已断开")
            
            
def operateStrage(symbol, timeframe, volume, close_point):
    box_breakout_strategy(symbol, timeframe, volume, close_point)
       
