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

import RPi.GPIO as GPIO 
import time 
from ask_wave import *

class Transmitter:

    def __init__(self, pin_tx):
        GPIO.setup(pin_tx, GPIO.OUT) 
        self.pin_tx = pin_tx

    def lock(self):
        GPIO.output(self.pin_tx, 1)

    def unlock(self):
        GPIO.output(self.pin_tx, 0)

    def send(self, wave):
        b = wave.startbit
        ts = wave.timestamp
        t1 = time.time()
        GPIO.output(self.pin_tx, b)
        t1 -= ts[0]
        for t in ts[1:-1]:
            b = 1 - b
            wait = t1 + t - time.time()
            if wait > 0:
                time.sleep(wait)
            GPIO.output(self.pin_tx, b)
        wait = t1 + ts[-1] - time.time()
        if wait > 0:
            time.sleep(wait)


class Receiver:

    def __init__(self, pin_rx, pin_en, sample_period=0.05, min_gap=3, max_gap=10):
        GPIO.setup(pin_en, GPIO.OUT) 
        # Don't enable GPIO.PUD_DOWN nor GPIO.PUD_UP due to the small receiver current
        GPIO.setup(pin_rx, GPIO.IN)
        GPIO.output(pin_en, GPIO.HIGH)
        self.pin_rx = pin_rx
        self.pin_en = pin_en
        self.sample_period = 1e-3 * sample_period
        self.min_gap = min_gap
        self.max_gap = max_gap

    def getSample(self):
        self.sample_time += self.sample_period
        now = time.time()
        wait = self.sample_time - now
        if wait > 0:
          time.sleep(wait)
        b = GPIO.input(self.pin_rx)
        now = time.time()
        return (b, now)

    def receive(self):
        wave = BitWave()
        ts = wave.timestamp
        b = GPIO.input(self.pin_rx)
        now = time.time()
        ch = GPIO.wait_for_edge(self.pin_rx, GPIO.BOTH, timeout=self.min_gap)
        if ch is not None:
            return None 
        b0 = b
        t0 = now
        ts.append(t0)
        ch = GPIO.wait_for_edge(self.pin_rx, GPIO.BOTH, timeout=self.max_gap-self.min_gap)
        b = GPIO.input(self.pin_rx)
        now = time.time()
        if ch is None:
            return None
        if b == b0:
            return None
        wave.startbit = b0
        self.bit = b
        self.sample_time = now
        self.edge_time = now
        ts.append(now)
        min_gap = 1e-3 * self.min_gap
        while True:
            (b, now) = self.getSample()
            if b == self.bit:
                if now - self.edge_time > min_gap:
                    if b == 0:
                        ts.append(now)
                    return wave
            else:
                ts.append(now)
                self.edge_time = now
                self.bit = b
        return wave

