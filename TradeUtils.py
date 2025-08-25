import time
import logging


logger = logging.getLogger('app')


def wait_for_time(hasVolumn, current_price, boder_hight = 0, boder_low = 0):
    
    if boder_hight == 0 and boder_low == 0:
        logger.info(f"boder未生效,休眠 60 秒")
        time.sleep(60)
        return
    if hasVolumn:
        logger.info(f"有仓位,休眠 5 秒")
        time.sleep(5)
        return
    if (current_price + 0.5 > boder_hight and current_price - 0.5) < boder_hight or (current_price + 0.5 > boder_low or current_price - 0.5 < boder_low):
        logger.info(f"价格在边界5个点内,休眠 10 秒")
        time.sleep(10)
        return
    logger.info(f"日常休眠 60 秒")
    time.sleep(60)
    
    
def find_high_peaks_with_2_point_window(df, current_price, n_peaks=2):
    """
    Find peaks in the 'high' column where each peak is higher than 2 points before and after it,
    with the first peak higher than current price and second peak higher than first peak by at least 1 point.
    df: DataFrame with 'high' column
    current_price: Current price to compare with first peak
    n_peaks: Number of peaks to find (default 2)
    Returns: List of peaks with their values, indices and times
    """
    if len(df) < 5:  # Need at least 5 points (2 before + 1 peak + 2 after)
        return []
    
    peaks = []
    
    # Iterate from back to front, but ensuring we have 2 points before and after
    # Start from index 2 and end at len(df) - 3 to ensure we have enough points
    for i in range(len(df) - 3, 1, -1):  # From len(df)-3 down to 2
        current_high = df.iloc[i]['high']
        is_peak = True
        
        # Check if current point is higher than 2 points before and after
        for j in range(i - 2, i + 3):  # Check 2 before, self, and 2 after
            if j != i and df.iloc[j]['high'] >= current_high:
                is_peak = False
                break
        
        # Additional conditions for specific peak requirements
        if is_peak:
            # For the first peak, it must be higher than current price
            if len(peaks) == 0 and current_high > current_price:
                peaks.append({
                    'value': current_high,
                    'index': i,
                    'time': df.iloc[i]['time']
                })
            # For the second peak, it must be higher than the first peak by at least 1 point
            elif len(peaks) == 1 and current_high > (peaks[0]['value'] + 1):
                peaks.append({
                    'value': current_high,
                    'index': i,
                    'time': df.iloc[i]['time']
                })
            
            # If we found the required number of peaks, break
            if len(peaks) == n_peaks:
                break
    
    return peaks

    
def find_low_troughs_with_2_point_window(df, current_price, n_troughs=2):
    """
    Find troughs in the 'low' column where each trough is lower than 2 points before and after it,
    with the first trough lower than current price and second trough lower than first trough by at least 1 point.
    df: DataFrame with 'low' column
    current_price: Current price to compare with first trough
    n_troughs: Number of troughs to find (default 2)
    Returns: List of troughs with their values, indices and times
    """
    if len(df) < 5:  # Need at least 5 points (2 before + 1 trough + 2 after)
        return []
    
    troughs = []
    
    # Iterate from back to front, but ensuring we have 2 points before and after
    # Start from index 2 and end at len(df) - 3 to ensure we have enough points
    for i in range(len(df) - 3, 1, -1):  # From len(df)-3 down to 2
        current_low = df.iloc[i]['low']
        is_trough = True
        
        # Check if current point is lower than 2 points before and after
        for j in range(i - 2, i + 3):  # Check 2 before, self, and 2 after
            if j != i and df.iloc[j]['low'] <= current_low:
                is_trough = False
                break
        
        # Additional conditions for specific trough requirements
        if is_trough:
            # For the first trough, it must be lower than current price
            if len(troughs) == 0 and current_low < current_price:
                troughs.append({
                    'value': current_low,
                    'index': i,
                    'time': df.iloc[i]['time']
                })
            # For the second trough, it must be lower than the first trough by at least 1 point
            elif len(troughs) == 1 and current_low < (troughs[0]['value'] - 1):
                troughs.append({
                    'value': current_low,
                    'index': i,
                    'time': df.iloc[i]['time']
                })
            
            # If we found the required number of troughs, break
            if len(troughs) == n_troughs:
                break
    
    return troughs

def process_target_prices(target_prices):
    """
    Process target prices according to the specified rules:
    - If target_prices is None, return (0, 0)
    - If target_prices has 1 element, return (first_value, 0)
    - If target_prices has 2 elements, return (first_value, second_value)
    
    Args:
        target_prices: List of price objects with 'value' attribute, or None
    
    Returns:
        tuple: (first_price, second_price)
    """
    # If target_prices is None, return (0, 0)
    if target_prices is None:
        return (0, 0)
    
    # If target_prices is empty, return (0, 0)
    if len(target_prices) == 0:
        return (0, 0)
    
    # If target_prices has 1 element, return (first_value, 0)
    if len(target_prices) == 1:
        return (target_prices[0]['value'], 0)
    
    # If target_prices has 2 or more elements, return (first_value, second_value)
    if len(target_prices) >= 2:
        return (target_prices[0]['value'], target_prices[1]['value'])
    
    # This shouldn't be reached, but just in case
    return (0, 0)


def calculate_box(df, box_period):
    """
    计算箱体的最高价和最低价（基于重叠最多的区间）
    df: K线数据DataFrame，包含open, high, low, close字段
    box_period: 箱体形成的周期数
    """
    if len(df) < box_period:
        return None, None
    
    # 取最近box_period根K线计算箱体
    box_data = df[:-1][:box_period]
    # 提取每根K线的上轨线区间[实体上沿, 最高价]
    upper_ranges = []
    # 提取每根K线的下轨线区间[最低价, 实体下沿]
    lower_ranges = []
    
    for i in range(len(box_data) - 1):
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

def check_and_calculate_box(df15, box_period):
    box_high, box_low = calculate_box(df15, box_period)
    box_data = df15[:-1][:box_period]
    print(box_data)
    max_value = max(box_data['close'].max(),box_data['open'].max())
    min_value = min(box_data['close'].min(),box_data['open'].min())
    
    if box_high is not None and  max_value > box_high + 1:
        pass
    else:
        max_value = box_high
    
    # Calculate min_value based on condition
    if box_low is not None and min_value < box_low - 1:
        pass
    else:
        min_value = box_low
    
    logger.info(f"箱体区间: {box_low} - {box_high}")
    logger.info(f"调整后区间: {min_value} - {max_value}")
    
    return (max_value, min_value)
    
    

    
    
    
    
    
    


