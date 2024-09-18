#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Usage:
#


class Stock():
    def __init__(self, code: str, data: any):
        self.code = code
        self.data = data

    def _calculate_ma(self, header: str, window: int):
        self.data[header] = self.data['Close'].rolling(window=window).mean()

    @property
    def date(self):
        return [d.date for d in self.data]

    @property
    def high(self):
        return [d.high for d in self.data]

    @property
    def low(self):
        return [d.low for d in self.data]

    @property
    def open(self):
        return [d.open for d in self.data]

    @property
    def close(self):
        return [d.close for d in self.data]

    @property
    def volume(self):
        return [d.volume for d in self.data]

    @property
    def volume(self):
        return [d.volume for d in self.data]
