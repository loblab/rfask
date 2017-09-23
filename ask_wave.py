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
import pickle

class BitWave:

    def __init__(self, timestamp=None, startbit=1):
        self.timestamp = timestamp if timestamp else []
        self.startbit = startbit

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return False

    def showRaw(self):
        print self.startbit
        print self.timestamp

    def show(self):
        size = len(self.timestamp) - 1
        dur = self.timestamp[-1] - self.timestamp[0]
        print '%.1fms/%d/%d:' % (dur * 1000, self.startbit, size),
        for i in range(0, size):
          print '%.2f' % ((self.timestamp[i + 1] - self.timestamp[i]) * 1000),
        print

    def dither(self, r=5e-5):
        self.timestamp = map(lambda x:x+random.random()*r, self.timestamp)

    def random(self, smin=10, smax=100, wmin=1e-4, wmax=2e-3):
        self.startbit = random.randint(0, 1)
        size = random.randint(smin, smax)
        t = 4e-3
        self.timestamp = [0, t]
        r = wmax - wmin
        for i in range(size):
            t += random.random() * r + wmin
            self.timestamp.append(t)
        t += 3e-3
        self.timestamp.append(t)

    def dump(self, fp):
        pickle.dump(self.timestamp, fp)
        pickle.dump(self.startbit, fp)

    def load(self, fp):
        self.timestamp = pickle.load(fp)
        self.startbit = pickle.load(fp)
        
