
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
import pickle
from bitstring import *
from ask_wave import *

class Signal:

    def show(self):
        print self.__str__()

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.bits == other.bits
        return False

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return self.bits != other.bits
        return True

class SignalRaw(Signal):

    def __init__(self, period=1e-3):
        self.period = period
        #self.bits = bits

    def __str__(self):
        return "[RAW] %.3f x %d: %s" % (
            self.period * 1000, len(self.bits), self.bits)

    def dump(self, fp):
        pickle.dump(self.period, fp)
        pickle.dump(str(self.bits), fp)

    def load(self, fp):
        self.period = pickle.load(fp)
        self.bits = BitArray(pickle.load(fp))

    def encode(self):
        wave = BitWave()
        ts = wave.timestamp
        t = 0
        ts.append(t)
        b = self.bits[0]
        wave.startbit = b
        for i in range(1, self.bits.len):
            t += self.period
            if self.bits[i] != b:
                ts.append(t)
                b = 1 - b
        t += self.period
        ts.append(t)
        return wave

    def decode(self, wave):
        ts = wave.timestamp
        b = wave.startbit
        bs = '0b1' if b else '0b0'
        self.bits = BitArray()
        for i in range(len(ts) - 1):
            w = ts[i + 1] - ts[i]
            c = int(w / self.period + 0.5)
            for j in range(c):
                self.bits.append(bs)
            b = 1 - b
            bs = '0b1' if b else '0b0'
        return True

class SignalPWM(Signal):

    def __init__(self, duty=0.75, period=1e-3, start1=5e-3, start0=1e-3, stop0=1e-2):
        self.duty = duty
        self.start1 = start1
        self.start0 = start0
        self.stop0 = stop0
        self.period = period
        #self.bits = bits

    def __str__(self):
        return "[PWM] %.2f/%.2f/%.2f - %.3f x %.1f%% - %d: %s" % (
            self.start1 * 1000, self.start0 * 1000, self.stop0 * 1000, 
            self.period * 1000, self.duty * 100, len(self.bits), self.bits)

    def dump(self, fp):
        pickle.dump(self.duty, fp)
        pickle.dump(self.period, fp)
        pickle.dump(self.start1, fp)
        pickle.dump(self.start0, fp)
        pickle.dump(self.stop0, fp)
        pickle.dump(str(self.bits), fp)

    def load(self, fp):
        self.duty = pickle.load(fp)
        self.period = pickle.load(fp)
        self.start1 = pickle.load(fp)
        self.start0 = pickle.load(fp)
        self.stop0 = pickle.load(fp)
        self.bits = BitArray(pickle.load(fp))

    def encode(self):
        wave = BitWave()
        ts = wave.timestamp
        t = 0
        ts.append(t)
        if self.start1 > 0:
            t += self.start1
            ts.append(t)
            wave.startbit = 1
        else:
            wave.startbit = 0
        t += self.start0
        ts.append(t)
        for i in range(self.bits.len):
            w = self.duty if self.bits[i] else 1 - self.duty
            ts.append(t + self.period * w)
            t += self.period
            ts.append(t)
        ts[-1] += self.stop0
        return wave

    def decode(self, wave):
        ts = wave.timestamp
        size = len(ts) - 1
        if size < 9:  # 4 bits at least
            return False
        if wave.startbit == 1:
            self.start1 = ts[1] - ts[0]
            i1 = 2
        else:
            self.start1 = 0
            i1 = 1
        self.start0 = ts[i1] - ts[i1 - 1]
        cbits = size - i1
        if (cbits % 2) > 0:
            return False
        self.bits = BitArray()
        csym = cbits / 2 - 1
        dur = ts[-3] - ts[i1]
        self.period = dur / csym
        self.stop0 = ts[-1] - ts[-3] - self.period
        if self.stop0 < 0:
            return False
        sum1 = 0
        c1 = 0
        for i in range(i1, size - 2):
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

        for i in range(i1, size - 1, 2):
            w = ts[i + 1] - ts[i]
            b = '0b1' if  w + w > self.period else '0b0'
            self.bits.append(b)
        return True


class SignalBP(Signal):

    def __init__(self, leading=20, period=1e-3, start0=5e-3, stop0=3e-3):
        self.start0 = start0
        self.stop0 = stop0
        self.leading = leading
        self.period = period
        #self.bits = bits

    def __str__(self):
        return "[BPS] %.2f/%.2f - %.3f x %3d - %d: %s" % (
            self.start0 * 1000, self.stop0 * 1000,
            self.period * 1000, self.leading,
            len(self.bits), self.bits)

    def dump(self, fp):
        pickle.dump(self.leading, fp)
        pickle.dump(self.period, fp)
        pickle.dump(self.start0, fp)
        pickle.dump(self.stop0, fp)
        pickle.dump(str(self.bits), fp)

    def load(self, fp):
        self.leading = pickle.load(fp)
        self.period = pickle.load(fp)
        self.start0 = pickle.load(fp)
        self.stop0 = pickle.load(fp)
        self.bits = BitArray(pickle.load(fp))

    def encode(self):
        wave = BitWave()
        wave.startbit = 0
        hp = self.period / 2
        dp = self.period * 2
        ts = wave.timestamp
        t = 0
        ts.append(t)
        t += self.start0
        ts.append(t)
        for i in range(self.leading):
            t += self.period
            ts.append(t)
        t += dp
        ts.append(t)
        t += dp
        ts.append(t)
        for i in range(self.bits.len):
            if self.bits[i] == 0:
                ts.append(t + hp)
            t += self.period
            ts.append(t)
        if len(ts) % 2 == 0:
            t += self.period
            ts.append(t)
        t += self.stop0
        ts.append(t)
        return wave

    def detectHead(self, ts):
        if len(ts) < 20:
            #print "SignalBP.detectHead: too short %d" % len(ts)
            return 0
        self.start0 = ts[1] - ts[0]
        count = 0
        wsum = 0.0
        wavg = 0.0
        wmax = 0.0
        wmin = 1.0
        b = 1
        for i in range(1, len(ts) - 2):
            w = ts[i + 1] - ts[i]
            if wmin > w:
                wmin = w
                if wmin < 1e-4:
                    #print "SignalBP.detectHead: too small wmin %f" % wmin
                    return 0
            if wmax < w:
                if count > 8:
                    wavg = wsum / count
                    wn = w / wavg
                    if wn > 1.6 and wn < 2.3 and b == 0:
                        i += 1
                        w = ts[i + 1] - ts[i]
                        wn = w / wavg
                        if wn > 1.6 and wn < 2.3:
                            self.leading = count
                            self.period = wavg
                            return i + 1
                        else:
                            #print "SignalBP.detectHead: invalid width %d (%.2f at %d), (should be 2)" % (wn, w * 1e3, i)
                            return 0
                wmax = w
            count += 1
            wsum += w
            b = 1 - b
        #print "SignalBP.detectHead: didn't find head"
        return 0

    def decode(self, wave):
        ts = wave.timestamp if wave.startbit == 0 else wave.timestamp[1:]
        start = self.detectHead(ts)
        if start <= 0:
            #print "SignalBP.decode: cannot find head"
            return False
        ws = []
        b = wave.startbit
        self.bits = BitArray()
        i = start
        stop = len(ts) - 3
        hp = self.period / 2
        while i < stop:
            w = ts[i + 1] - ts[i]
            c = int(w / hp + 0.5)
            if c < 1 or c > 2:
                #print "SignalBP.decode: invalid width %d (%.2fms at %d), should be 1 or 2" % (c, w * 1e3, i)
                return False
            ws.append(c)
            if c == 2:
                self.bits.append('0b1')
            else:
                i += 1
                w = ts[i + 1] - ts[i]
                c = int(w / hp + 0.5)
                if c != 1:
                    #print "SignalBP.decode: invalid width %d (%.2fms at %d), should be 1" % (c, w * 1e3, i)
                    return False
                ws.append(c)
                self.bits.append('0b0')
            b = 1 - b
            i += 1
        if len(self.bits) % 2:
            self.bits.append('0b1')
        self.stop0 = ts[-1] - ts[-2]
        return True


class SignalAuto(Signal):

    def __init__(self, params=None):
        if params is None:
            self.signal = None
            return
        typ = params[0]
        if typ == 'PWM':
            self.signal = SignalPWM(params[4], params[5]*1e-3, params[1]*1e-3, params[2]*1e-3, params[3]*1e-3)
            self.signal.bits = BitArray(params[6])
            return
        if typ == 'BPS':
            self.signal = SignalBP(params[3], params[4]*1e-3, params[1]*1e-3, params[2]*1e-3)
            self.signal.bits = BitArray(params[5])
            return
        self.signal = None

    def __str__(self):
        return self.signal.__str__()

    def dump(self, fp):
        pickle.dump(self.signal.__class__.__name__, fp)
        self.signal.dump(fp)

    def load(self, fp):
        clsname = pickle.load(fp)
        self.signal = globals()[clsname]()
        self.signal.load(fp)

    def encode(self):
        return self.signal.encode()

    def decode(self, wave):
        sig = SignalPWM()
        if sig.decode(wave):
            self.signal = sig
            return True
        sig = SignalBP()
        if sig.decode(wave):
            self.signal = sig
            return True
        return False

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.signal == other.signal
        return self.signal == other

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return self.signal != other.signal
        return self.signal != other

