# Copyright 2017 loblab
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#       http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import time
import random
from bitstring import *

class BitWave:

    def __init__(self, timestamp):
        self.timestamp = timestamp

    def showRaw(self):
        print self.timestamp

    def show(self):
        size = len(self.timestamp) - 1
        dur = self.timestamp[-1] - self.timestamp[0]
        print '%.1fms/%d:' % (dur * 1000, size),
        for i in range(0, size):
          print '%.2f' % ((self.timestamp[i + 1] - self.timestamp[i]) * 1000),
        print

    def rand(self, r=5e-5):
        self.timestamp = map(lambda x:x+random.random()*r, self.timestamp)
        
class Signal:

    def __init__(self, bits=BitArray(), duty=1, period=1e-3, start1=5e-3, start0=1e-3, stop0=1e-2):
        self.start1 = start1
        self.start0 = start0
        self.stop0 = stop0
        self.period = period
        self.bits = bits
        self.duty = duty

    def __str__(self):
        return "%.2f/%.2f/%.2f - %.3f x %.1f%% - %d: %s" % (
            self.start1 * 1000, self.start0 * 1000, self.stop0 * 1000, 
            self.period * 1000, self.duty * 100, len(self.bits), self.bits)

    def show(self):
        print self.__str__()

    def encodePWM(self, ts):
        t = 0
        ts.append(t)
        t += self.start1
        ts.append(t)
        t += self.start0
        ts.append(t)
        for i in range(0, self.bits.len):
            w = self.duty if self.bits[i] else 1 - self.duty
            ts.append(t + self.period * w)
            t += self.period
            ts.append(t)
        ts[-1] += self.stop0

    def encodeRaw(self, ts):
        t = 0
        ts.append(t)
        t += self.start1
        ts.append(t)
        t += self.start0
        b = False
        for i in range(0, self.bits.len):
            if self.bits[i] != b:
                ts.append(t)
                b = not b
            t += self.period
        if b:
            ts.append(t)
        t += self.stop0
        ts.append(t)

    def encode(self, ts):
        if self.duty < 1:
            self.encodePWM(ts)
        else:
            self.encodeRaw(ts)
            
    def decodePWM(self, ts):
        cbits = len(ts) - 5
        if (cbits < 20):
            return False
        #2 bit at least exclude start & stop 
        if (cbits % 2) > 0:
            return False
        self.start1 = ts[1] - ts[0]
        self.start0 = ts[2] - ts[1]
        self.bits = BitArray()
        csym = cbits / 2
        dur = ts[-3] - ts[2]
        self.period = dur / csym
        self.stop0 = ts[-1] - ts[-3] - self.period
        if self.stop0 < 0:
            return False
        sum1 = 0
        c1 = 0
        for i in range(2, len(ts) - 3):
            w = ts[i + 1] - ts[i]
            if w >= self.period:
                return False
            if w + w > self.period:
                sum1 += w
                c1 += 1
        if (c1 == 0):
            return False
        self.duty = sum1 / c1 / self.period
        if self.duty > 0.95:
            return False

        for i in range(2, len(ts) - 2, 2):
            w = ts[i + 1] - ts[i]
            b = '0b1' if  w + w > self.period else '0b0'
            self.bits.append(b)
        return True

    def decode(self, ts):
        ws = []
        for i in range(2, len(ts) - 3):
            ws.append(ts[i + 1] - ts[i])
        for w in ws:
            print "%.2f" % (w * 1000),
        print
        wsum = sum(ws)
        wmin = min(ws)
        wmax = max(ws)
        wavg = wsum / len(ws)
        print "avg/max/min: %.2f/%.2f/%.2f ms" % (wavg * 1000, wmax * 1000, wmin * 1000)


