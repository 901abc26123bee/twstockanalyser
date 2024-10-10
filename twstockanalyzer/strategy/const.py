#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Usage: common const
#

TWSE_STOCK_SUFFIX_TW = ".TW"  # 上市
TPEX_STOCK_SUFFIX_TWO = ".TWO"  # 上櫃
STOCK_DATA_FOLDER = "./web/stock_data/"
CSV_EXTENSION = ".csv"


# ---------------------------- base.py ----------------------------

# trend_closer_to_golden_cross
LINE_SRC_TREND_STRONG_CLOSING_TO_CROSSOVER = "src 強靠近 target"
LINE_SRC_TREND_WEEK_CLOSING_TO_CROSSOVER = "src 弱靠近 target"
LINE_SRC_TREND_STRONG_LEAVING_FROM_TARGET = "src 強遠離 target"
LINE_SRC_TREND_WEEK_LEAVING_FROM_TARGET = "src 弱遠離 target"
LINE_SRC_CROSSOVER_TARGET_UPWARD = "黃金交叉(src > target)"
LINE_SRC_CROSSOVER_TARGET = "交叉(多個cross over)"
LINE_SRC_CROSSOVER_TARGET_DOWNWARD = "死亡交叉(src < target)"
LINE_CLOSER_TREAD_UNKNOWN = "unknown"


LINE_TREND_UPWARD = "向上線型"
LINE_TREND_DOWNWARD = "向下線型"
LINE_TREND_UPWARD_UP = "向上開花(向上開花角度變大)"
LINE_TREND_DOWNWARD_DOWN = "向下開花(向下開花角度變大)"

LINE_TREND_POSITIVE_V = "正Ｖ向上反轉"
LINE_TREND_NEGATIVE_V = "反Ｖ向下反轉"

# 價格型態
PATTERN_BOTTOM_W = "W底"


# ---------------------------- macd.py ----------------------------

# check_osc_stick_heigh
OSC_RED_WEEK = "OSC 弱紅柱"
OSC_RED_STRONG = "OSC 強紅柱"
OSC_RED_CONSOLIDATION = "OSC 紅柱，趨勢不明"
OSC_RED_RANGE_LONG = "OSC 紅柱範圍長"

OSC_GREEN_WEEK = "OSC 弱綠柱"
OSC_GREEN_STRONG = "OSC 強綠柱"
OSC_GREEN_CONSOLIDATION = "OSC 綠柱，趨勢不明"
OSC_GREEN_RANGE_LONG = "OSC 綠柱範圍長"


# check_osc_stick_heigh_in_multi_period

# check_macd_trend
MACD_DO_NOT_TOUCH = "OSC 強綠柱 + OSC 綠柱範圍長 + macd零軸下 範圍長 + MACD 下降趨勢"

MACD_ABOVE_MIDDLE = "macd零軸上"
MACD_BELOW_MIDDLE = "macd零軸下"

MACD_SHOW_UP_TREND = "MACD 上升趨勢"
MACD_SHOW_DOWN_TREND = "MACD 下降趨勢"
MACD_SHOW_UP_UP_TREND = "MACD 上升加劇趨勢"
MACD_SHOW_DOWN_DOWN_TREND = "MACD 下降加劇趨勢"
MACD_BACKTEST_IN_UP_TREND = "MACD 上升趨勢的回測"
MACD_BACKTEST_IN_DOWN_TREND = "MACD 下降趨勢的回測"

MACD_CLOSING_MIDDLE_FROM_BOTTOM = "MACD 從下方靠近軸線"
MACD_CLOSING_MIDDLE_FROM_ABOVE = "MACD 從上方靠近軸線"

MACD_DUCK_UP_TREND = "MACD 向上鴨嘴"
MACD_DUCK_DOWN_TREND = "MACD 向下鴨嘴"
# MACD_ABOUT_TO_CROSS_MIDDLE = "MACD 即將穿過零軸線"
# MACD_BACKTEST_CROSS_MIDDLE = "MACD 穿過軸線的回測 N"

MACD_UNKNOWN = "macd trend unknown"


# check_macd_trend_in_multi_period

# ---------------------------- macd.py ----------------------------

# 40ma and 138ma
MA40_ABOVE_MA138 = "40 均線在 138 均線上"
MA40_BELOW_MA138 = "40 均線在 138 均線下"
MA40_ABOVE_LEAVING_MA138 = "40 均線在138均線上，開花向上"
MA40_CLOSING_TO_MA138_FROM_BOTTOM = "40 均線向上靠近 138 均線(未穿過)"
MA40_CLOSING_TO_MA138_FROM_ABOVE = "40 均線向下靠近 138 均線(未穿過)"
MA40_CROSS_OVER_MA138_UPWARD = "40 均線向上穿過 138 均線(黃金交叉)"
MA40_CROSS_OVER_MA138_DOWNWARD = "40 均線向下穿過 138 均線(死亡交叉)"

# 5ma and 138ma
MA5_ABOVE_MA138 = "5 均線在 138 均線上"
MA5_BELOW_MA138 = "5 均線在 138 均線下"
MA5_CLOSING_TO_MA138_FROM_BOTTOM = "5 均線向上靠近 138 均線(未穿過)"
MA5_CLOSING_TO_MA138_FROM_ABOVE = "5 均線向下靠近 138 均線(未穿過)"
MA5_CROSS_OVER_MA138_UPWARD = "5 均線向上穿過 138 均線(黃金交叉)"
MA5_CROSS_OVER_MA138_DOWNWARD = "5 均線向下穿過 138 均線(死亡交叉)"

# 5ma and 40ma
MA5_ABOVE_MA40 = "5 均線在 40 均線上"
MA5_BELOW_MA40 = "5 均線在 40 均線下"
MA5_ABOVE_LEAVING_MA40 = "40均線在40均線上，開花向上"
MA5_CLOSING_TO_MA40_FROM_BOTTOM = "5 均線向上靠近 40 均線(未穿過)"
MA5_CLOSING_TO_MA40_FROM_ABOVE = "5 均線向下靠近 40 均線(未穿過)"
MA5_CROSS_OVER_MA40_UPWARD = "5 均線向上穿過 40 均線(黃金交叉)"
MA5_CROSS_OVER_MA40_DOWNWARD = "5 均線向下穿過 40 均線(死亡交叉)"

# BACKTEST_CROSS_MA138 = "穿越138均線回測"


# ---------------------------- bband.py ----------------------------


# ---------------------------- pattern.py ----------------------------
