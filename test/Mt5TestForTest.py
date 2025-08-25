import MetaTrader5 as mt5
import pandas as pd
import time
from datetime import datetime, timedelta
import Mt5Lib



def calculate_box(df, box_period):
    """
    计算箱体的最高价和最低价（基于重叠最多的区间）
    df: K线数据DataFrame，包含open, high, low, close字段
    box_period: 箱体形成的周期数
    """
    if len(df) < box_period:
        return None, None
    
    # 取最近box_period根K线计算箱体
    box_data = df[-box_period:]
    
    # 提取每根K线的上轨线区间[实体上沿, 最高价]
    upper_ranges = []
    # 提取每根K线的下轨线区间[最低价, 实体下沿]
    lower_ranges = []
    
    for i in range(len(box_data)):
        row = box_data.iloc[i]
        open_price = row['open']
        close_price = row['close']
        high_price = row['high']
        low_price = row['low']
        
        # 实体上沿（开盘价和收盘价中的较高者）
        entity_top = max(open_price, close_price)
        # 实体下沿（开盘价和收盘价中的较低者）
        entity_bottom = min(open_price, close_price)
        
        # 上轨线区间 [实体上沿, 最高价]
        upper_ranges.append((entity_top, high_price))
        # 下轨线区间 [最低价, 实体下沿]
        lower_ranges.append((low_price, entity_bottom))
    
    # 找出上轨线之间的重合点
    upper_overlapping_points = set()
    
    # 两两比较上轨线区间
    for i in range(len(upper_ranges)):
        for j in range(i + 1, len(upper_ranges)):
            range1 = upper_ranges[i]
            range2 = upper_ranges[j]
            
            # 找到两个区间的重合部分
            overlap_start = max(range1[0], range2[0])
            overlap_end = min(range1[1], range2[1])
            
            # 如果有重合
            if overlap_start <= overlap_end:
                # 在重合区间内添加所有可能的重合点（这里简化为添加端点）
                upper_overlapping_points.add(overlap_start)
                upper_overlapping_points.add(overlap_end)
    
    # 找出下轨线之间的重合点
    lower_overlapping_points = set()
    
    # 两两比较下轨线区间
    for i in range(len(lower_ranges)):
        for j in range(i + 1, len(lower_ranges)):
            range1 = lower_ranges[i]
            range2 = lower_ranges[j]
            
            # 找到两个区间的重合部分
            overlap_start = max(range1[0], range2[0])
            overlap_end = min(range1[1], range2[1])
            
            # 如果有重合
            if overlap_start <= overlap_end:
                # 在重合区间内添加所有可能的重合点（这里简化为添加端点）
                lower_overlapping_points.add(overlap_start)
                lower_overlapping_points.add(overlap_end)
    
    # 如果没有重合点，返回None
    if not upper_overlapping_points or not lower_overlapping_points:
        return None, None
    
    # 上轨线之间重叠两个点的集合的最高点
    box_high = max(upper_overlapping_points)
    
    # 下轨线之间重叠两个点的集合的最低点
    box_low = min(lower_overlapping_points)
    
    return box_high, box_low
    
# 主程序
if __name__ == "__main__":
    # 策略参数
    SYMBOL = "XAUUSD"  # 交易品种
    TIMEFRAME = mt5.TIMEFRAME_M15  # 时间周期 (15分钟)
    BOX_PERIOD =10  # 箱体周期 (10根K线)
    VOLUME = 0.1  # 交易量 (0.1手)
    
    # 初始化MT5
    if Mt5Lib.initialize_mt5():
        try:
            # 计算箱体区间
            df = Mt5Lib.get_historical_data(SYMBOL, TIMEFRAME, BOX_PERIOD + 1)
            print(df)
            box_high, box_low = calculate_box(df, BOX_PERIOD)
            # 获取最新价格
            current_price = df.iloc[-1]['close']
            current_time = df.iloc[-1]['time']
            # 打印当前状态
            print(f"\n时间: {current_time}")
            print(f"当前价格: {current_price}")
            print(f"箱体区间: {box_low} - {box_high}")
            

        finally:
            # 断开MT5连接
            mt5.shutdown()
            print("MT5连接已断开")