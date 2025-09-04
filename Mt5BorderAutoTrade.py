import pandas as pd
from datetime import datetime
import Mt5Lib
import TradeUtils
import logConfig
from multiConfigManager import Config
import context

class TradeBot:
    
    def __init__(self, symbol : str = '', confg: Config = None):
        self.confg = confg
        self.symbol = symbol
    

    '''
        平仓逻辑，以平多头为例
        1. 亏损40个点离场，平仓
        2. 突破后箱，给了新箱体线，前一根五分钟没占上去，且前一根1分钟最高点没占上去，平仓
        3. 如果不是动能产生的突破，前一根五分钟最高点没有比前前一根高，平仓
        4. 当前价格低于前一根5分钟线实体最低点，平仓
        5. 达到第一目标位，平仓一半
        6. 达到第二目标位，平仓
        7. 三根 1m 阴线，平仓 
    '''
    def close_position_if_neccessary(self, positions, current_price, box_high, box_low,df5):
        m5_entity_min = min(df5.iloc[-2]['close'],df5.iloc[-2]['open'])
        logger.info(f'上一m5 least {m5_entity_min}')
        m5_entity_max = max(df5.iloc[-2]['close'],df5.iloc[-2]['open'])
        logger.info(f'上一m5 most {m5_entity_max}')
        df1 = Mt5Lib.get_historical_data(self.symbol, Mt5Lib.TIMEFRAME_M1, 4)
        print(df1)
        for position in positions:
            # 对于买单，如果当前价格低于开仓价格4点则平仓
            if position.volume != self.confg.OPEN_VOLUM:
                break
            if position.type == Mt5Lib.POSITION_TYPE_BUY:
                # 平仓判断
                loss_points = position.price_open - current_price
                if loss_points >= self.confg.CLOSE_POINTS:
                    logger.info(f"做多仓位 {position.price_open} 点，现在为{current_price}，达到{self.confg.CLOSE_POINTS}点close条件，平仓")
                    Mt5Lib.close_position(self.symbol, position.ticket, Mt5Lib.ORDER_TYPE_BUY, position.volume)
                    context.config_manager.add_config(self.symbol, config.reinit())   
                elif box_high >= current_price and box_high >= df5.iloc[-2]['close'] and  box_high >= df1.iloc[-2]['high']:
                    logger.info(f"做多仓位 {position.price_open} 点，现在为{current_price}， is in box {box_high} close条件，平仓")   
                    Mt5Lib.close_position(self.symbol, position.ticket, Mt5Lib.ORDER_TYPE_BUY, position.volume)
                    context.config_manager.add_config(self.symbol, config.reinit())   
                elif not self.confg.FIVE_MIN_VOLUME_FLAG and self.confg.FIVE_MIN_OPEN_FLAG and df5.iloc[-2]['high'] <= df5.iloc[-3]['high'] :
                    logger.info(f"做多仓位 {position.price_open} 点，现在为{current_price}，last m5 dose not high enough  close条件，平仓")
                    Mt5Lib.close_position(self.symbol, position.ticket, Mt5Lib.ORDER_TYPE_BUY, position.volume)
                    context.config_manager.add_config(self.symbol, config.reinit())   
                elif m5_entity_min >= current_price:
                    logger.info(f"做多仓位 {position.price_open} 点，现在为{current_price}，is less than m5 {m5_entity_min} close条件，平仓")
                    Mt5Lib.close_position(self.symbol, position.ticket, Mt5Lib.ORDER_TYPE_BUY, position.volume)
                    context.config_manager.add_config(self.symbol, config.reinit())   
                elif self.confg.TARGET_OBJECT_PRICE_1 > 0 and current_price >= self.confg.TARGET_OBJECT_PRICE_1:
                    logger.info(f"做空仓位 {position.price_open} 点，现在为{current_price}，is more than TARGET_OBJECT_PRICE_1 {self.confg.TARGET_OBJECT_PRICE_1} close条件，平仓")
                    Mt5Lib.close_position(self.symbol, position.ticket, Mt5Lib.ORDER_TYPE_BUY, position.volume/2)
                    context.config_manager.add_config(self.symbol, config.reinit())   
                elif self.confg.TARGET_OBJECT_PRICE_2 > 0 and current_price >= self.confg.TARGET_OBJECT_PRICE_2:
                    logger.info(f"做空仓位 {position.price_open} 点，现在为{current_price}，is more than TARGET_OBJECT_PRICE_1 {self.confg.TARGET_OBJECT_PRICE_2} close条件，平仓")
                    Mt5Lib.close_position(self.symbol, position.ticket, Mt5Lib.ORDER_TYPE_BUY, position.volume)
                    context.config_manager.add_config(self.symbol, config.reinit())   
                elif (df1.iloc[-1]['close'] - df1.iloc[-1]['open'] <= 0) and (df1.iloc[-2]['close'] - df1.iloc[-2]['open'] <= 0) \
                    and (df1.iloc[-3]['close'] - df1.iloc[-3]['open'] <= 0):
                    logger.info(f"做空仓位 {position.price_open} 点，现在为{current_price}， 三根1m close条件，平仓")
                    Mt5Lib.close_position(self.symbol, position.ticket, Mt5Lib.ORDER_TYPE_BUY, position.volume)
                    context.config_manager.add_config(self.symbol, config.reinit())   
                                        
            # 对于卖单，如果当前价格高于开仓价格4点则平仓
            elif position.type == Mt5Lib.POSITION_TYPE_SELL:
                # 平仓判断
                loss_points = current_price - position.price_open
                if loss_points >= self.confg.CLOSE_POINTS:
                    logger.info(f"做空仓位 {position.price_open} 点，现在为{current_price}，达到{self.confg.CLOSE_POINTS}点close条件，平仓")
                    Mt5Lib.close_position(self.symbol, position.ticket, Mt5Lib.ORDER_TYPE_SELL, position.volume)
                    context.config_manager.add_config(self.symbol, config.reinit())   
                elif box_low <= current_price and box_low <= df5.iloc[-2]['close'] and  box_low <= df1.iloc[-2]['low']:
                    logger.info(f"做空仓位 {position.price_open} 点，现在为{current_price}，is in box {box_low}点close条件，平仓")
                    Mt5Lib.close_position(self.symbol, position.ticket, Mt5Lib.ORDER_TYPE_SELL, position.volume)
                    context.config_manager.add_config(self.symbol, config.reinit())   
                elif not self.confg.FIVE_MIN_VOLUME_FLAG and self.confg.FIVE_MIN_OPEN_FLAG and df5.iloc[-2]['low'] > df5.iloc[-3]['low'] :
                    logger.info(f"做多仓位 {position.price_open} 点，现在为{current_price}，last m5 dose not high enough  close条件，平仓")
                    Mt5Lib.close_position(self.symbol, position.ticket, Mt5Lib.ORDER_TYPE_SELL, position.volume)
                    context.config_manager.add_config(self.symbol, config.reinit())   
                elif m5_entity_max <= current_price:
                    logger.info(f"做空仓位 {position.price_open} 点，现在为{current_price}，is more than m5 {m5_entity_max} close条件，平仓")
                    Mt5Lib.close_position(self.symbol, position.ticket, Mt5Lib.ORDER_TYPE_SELL, position.volume)
                    context.config_manager.add_config(self.symbol, config.reinit())   
                elif self.confg.TARGET_OBJECT_PRICE_1 >0 and current_price <= self.confg.TARGET_OBJECT_PRICE_1:
                    logger.info(f"做空仓位 {position.price_open} 点，现在为{current_price}，is less than TARGET_OBJECT_PRICE_1 {self.confg.TARGET_OBJECT_PRICE_1} close条件，平仓")
                    Mt5Lib.close_position(self.symbol, position.ticket, Mt5Lib.ORDER_TYPE_SELL, position.volume/2)
                    context.config_manager.add_config(self.symbol, config.reinit())   

                elif self.confg.TARGET_OBJECT_PRICE_2 >0 and current_price <= self.confg.TARGET_OBJECT_PRICE_2:
                    logger.info(f"做空仓位 {position.price_open} 点，现在为{current_price}，is less than TARGET_OBJECT_PRICE_2 {self.confg.TARGET_OBJECT_PRICE_2} close条件，平仓")
                    Mt5Lib.close_position(self.symbol, position.ticket, Mt5Lib.ORDER_TYPE_SELL, position.volume)
                    context.config_manager.add_config(self.symbol, config.reinit())   

                elif (df1.iloc[-1]['close'] - df1.iloc[-1]['open'] >= 0) and (df1.iloc[-2]['close'] - df1.iloc[-2]['open'] >= 0) \
                    and (df1.iloc[-3]['close'] - df1.iloc[-3]['open'] >= 0):
                    logger.info(f"做多仓位 {position.price_open} 点，现在为{current_price}，三根1m close条件，平仓")
                    Mt5Lib.close_position(self.symbol, position.ticket, Mt5Lib.ORDER_TYPE_SELL, position.volume)
                    context.config_manager.add_config(self.symbol, config.reinit())   


    def tagetPrice(self, current_price, POSITION_TYPE):
        df15 = Mt5Lib.get_historical_data(self.symbol, Mt5Lib.TIMEFRAME_M5, 200)
        if POSITION_TYPE == Mt5Lib.POSITION_TYPE_BUY:
            peaks = TradeUtils.find_high_peaks_with_2_point_window(df15, current_price)
            target_price_1, target_price_2 = TradeUtils.process_target_prices(peaks)
            return target_price_1, target_price_2
        elif POSITION_TYPE == Mt5Lib.POSITION_TYPE_SELL:
            troughs = TradeUtils.find_low_troughs_with_2_point_window(df15, current_price)
            target_price_1, target_price_2 = TradeUtils.process_target_prices(troughs)
            return target_price_1, target_price_2
        return 0, 0


    '''
        开仓逻辑，以多头为例
        1. 当前价格突破箱体上沿，且比上一五分钟最高要高，继续多头探索
        2. 若五分钟量能突然放大，（通过比前一个根的ticket_volumn），开多仓 
        3. 若量能没有探索出来，前一根5分钟最高比前前一根5分钟最高要高，前一根1分钟线收在箱体上,前一根1分钟线比前前1根收线高，前一根1分钟线最高比前前1根要高，则开多仓
    '''
    def open_position_if_neccessary(self,current_price,box_high,box_low, df5):
        m5_low = df5.iloc[-2]['low']
        logger.info(f'上一m5 low {m5_low}')
        m5_high = df5.iloc[-2]['high']
        logger.info(f'上一m5 high {m5_high}')
        if current_price > min(df5.iloc[-2]['close'],df5.iloc[-2]['high']) and current_price < max(df5.iloc[-2]['close'],df5.iloc[-2]['high']) :
            logger.info(f"价格在m5实体区间内，不做处理")
            return
        df1 = Mt5Lib.get_historical_data(self.symbol, Mt5Lib.TIMEFRAME_M1, 3)
        current_price = df1.iloc[-1]['close']
        #5分钟量能关系
        now = datetime.now()
        minutes_in_interval = now.minute % 5
        seconds_in_interval = now.second
        weight = (minutes_in_interval*60 + seconds_in_interval)/300 + 0.05
        last_two_tick_volume_change =  df5.iloc[-1]['tick_volume']/(weight) 
        first_two_tick_volume_change = (df5.iloc[-2]['tick_volume'] + df5.iloc[-3]['tick_volume'])/2 * 1.1 + 10
        self.confg.FIVE_MIN_VOLUME_FLAG = last_two_tick_volume_change > first_two_tick_volume_change
        five_min_open_flag = False
        target_price_1,target_price_2 = 0,0
        # 突破上沿, 做多
        if  current_price > box_high and current_price > m5_high:
            if not self.confg.FIVE_MIN_VOLUME_FLAG \
                and df5.iloc[-3]['close'] >= df5.iloc[-4]['close'] and df5.iloc[-4]['close'] > df5.iloc[-2]['open'] \
                and (df5.iloc[-2]['high'] > df5.iloc[-3]['high'] or df5.iloc[-2]['close'] > df5.iloc[-3]['close']) \
                and df1.iloc[-2]['close'] > box_high  and df1.iloc[-1]['high'] > df1.iloc[-2]['high'] \
                and df1.iloc[-2]['close'] > df1.iloc[-3]['close'] and df1.iloc[-2]['high'] > df1.iloc[-3]['high']:
                five_min_open_flag = True
                logger.info(f"价格突破箱体上沿 {box_high}, 形态好，发送买入订单")
                Mt5Lib.send_order(self.symbol, self.confg.OPEN_VOLUM, Mt5Lib.ORDER_TYPE_BUY)
                target_price_1,target_price_2 = self.tagetPrice(current_price,Mt5Lib.ORDER_TYPE_BUY)
            elif self.confg.FIVE_MIN_VOLUME_FLAG:
                logger.info(f"价格突破箱体上沿 {box_high},动能好, 发送买入订单")
                Mt5Lib.send_order(self.symbol, self.confg.OPEN_VOLUM, Mt5Lib.ORDER_TYPE_BUY)
                target_price_1,target_price_2 = self.tagetPrice(current_price,Mt5Lib.ORDER_TYPE_BUY)
        # 跌破下沿, 做空
        elif  current_price < box_low and current_price < m5_low:
            if not self.confg.FIVE_MIN_VOLUME_FLAG \
                and df5.iloc[-3]['close'] <= df5.iloc[-4]['close'] and df5.iloc[-4]['close'] < df5.iloc[-2]['open'] \
                and (df5.iloc[-2]['close'] < df5.iloc[-3]['close'] or  df5.iloc[-2]['low']<df5.iloc[-3]['low']) \
                and df1.iloc[-2]['close'] < box_low and df1.iloc[-1]['low'] < df1.iloc[-2]['low'] \
                and df1.iloc[-2]['close'] < df1.iloc[-3]['close'] and df1.iloc[-2]['low'] < df1.iloc[-3]['low']:
                logger.info(f"价格跌破箱体下沿 {box_low}, 形态好，发送卖出订单")
                Mt5Lib.send_order(self.symbol, self.confg.OPEN_VOLUM, Mt5Lib.ORDER_TYPE_SELL)
                target_price_1,target_price_2 = self.tagetPrice(current_price,Mt5Lib.ORDER_TYPE_SELL)
            elif self.confg.FIVE_MIN_VOLUME_FLAG:
                logger.info(f"价格跌破箱体下沿 {box_low},动能好, 发送卖出订单")
                Mt5Lib.send_order(self.symbol, self.confg.OPEN_VOLUM, Mt5Lib.ORDER_TYPE_SELL)
                target_price_1,target_price_2 = self.tagetPrice(current_price,Mt5Lib.ORDER_TYPE_SELL)
        self.confg.TARGET_OBJECT_PRICE_1,self.confg.TARGET_OBJECT_PRICE_2 = target_price_1,target_price_2
        self.confg.FIVE_MIN_OPEN_FLAG = five_min_open_flag
        context.config_manager.add_config(self.symbol, self.confg)
        logger.info(f'5分钟成交量first_two_tick_volume:{first_two_tick_volume_change}, last_two_tick_volume:{last_two_tick_volume_change},FIVE_MIN_VOLUME_FLAG:{five_min_open_flag},weight:{weight}')
        logger.info(f"1目标价格:{target_price_1}，   2目标价格:{target_price_2}")
    # 箱体突破策略主函数
    def box_breakout_strategy(self):
        timeframe = Mt5Lib.TIMEFRAME_M15
        logger.info(f"开始运行箱体突破策略 - 品种: {self.symbol}, 周期: {timeframe}, 箱体周期: {self.confg.GOBAL_BOX_PERIOD}")
        while True:
            self.confg = context.config_manager.get_configFromFile(self.symbol)
            box_high, box_low = 0,0
            hasPosition= False
            current_price = 0
            try:
                # 检查当前持仓
                positions = Mt5Lib.positions_get(symbol=self.symbol)
                hasPosition = positions is not None and len(positions) != 0
                
                # 获取历史数据
                df5 = Mt5Lib.get_historical_data(self.symbol, Mt5Lib.TIMEFRAME_M5, self.confg.GOBAL_BOX_PERIOD * 3 + 1 )
                if df5 is None or len(df5) < (self.confg.GOBAL_BOX_PERIOD * 3 + 1):
                    TradeUtils.wait_for_time(False,0)
                    continue
                # 计算箱体区间
                box_high, box_low = TradeUtils.check_and_calculate_box(df5, self.confg.GOBAL_BOX_PERIOD * 3 + 1, self.confg.MIN_BOX_SIZE)
                if box_high is None or box_low is None:
                    logger.info(f"箱体区间不成立")
                    TradeUtils.wait_for_time(False,0)
                    continue
                # 获取最新价格
                current_price = df5.iloc[-1]['close']
                current_time = df5.iloc[-1]['time']
                # 打印当前状态
                logger.info(f"\n时间: {current_time},当前价格: {current_price},箱体区间: {box_low} - {box_high}")
                
                # 如果有持仓，检查是否need close
                if hasPosition:
                    self.close_position_if_neccessary(positions,current_price,box_high, box_low, df5)
                else:
                    self.open_position_if_neccessary(current_price,box_high, box_low, df5)
            except Exception as e:
                logger.info(f"策略运行出错: {str(e)}")
            
            TradeUtils.wait_for_time(hasPosition, current_price, box_high, box_low)
    def operateStrage(self):
        self.box_breakout_strategy()

# 主程序
if __name__ == "__main__":
    
    logger = logConfig.setup_logger()
    # 策略参数
    SYMBOL = "XAUUSD"  # 交易品种
    TIMEFRAME = Mt5Lib.TIMEFRAME_M15  # 时间周期 (15分钟)
    OPEN_VOLUME = 0.1  # 交易量 (0.1手)
    CLOSE_POINTS = 4
    
    # 初始化MT5
    if Mt5Lib.initialize_mt5():
        try:
            # 运行策略
            config = Config(True,True,0,0,8,0,0,OPEN_VOLUME,CLOSE_POINTS)
            context.config_manager.add_config(SYMBOL, config)
            tradeBot = TradeBot(SYMBOL,config)
            tradeBot.operateStrage()
        finally:
            # 断开MT5连接
            Mt5Lib.shutdown()
            logger.info("MT5连接已断开")
            
            

       
