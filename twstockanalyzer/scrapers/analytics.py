#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Usage: strategy for filter out stock buy point
#

class Strategy:
    def __init__(self):
        pass

    # 月、週 呈高檔鈍化
    def high_end_stagnation_in_month_and_week(self):
        pass

    # 月線低檔爆量
    def high_volume_at_low_level_in_month(self):
        pass

    # 60m or 30m or 15m MACD 呈上升趨勢
    def is_buy_point_in_minute_macd(self):
        pass

    # 強勢股拉回(日)
    def is_pullback_in_a_uptrend_stock_day(self):
        pass

    # 月、週 呈向下趨勢股票
    def _is_downtrend_in_month_and_week(self):
        pass


class Analysis:
    def __init__(self):
        pass

    def moving_average(self):
        pass
    
    def macd_uptrend(self):
        pass