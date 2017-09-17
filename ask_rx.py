#!/usr/bin/python
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
import sys
from bitstring import *
from ask_struct import *
from ask_device import *
from ask_config import PIN_ASK_EN, PIN_ASK_RX

def receive_loop(rx, timeout):
    start_time = time.time()
    total = 0
    sig = Signal()
    while ((time.time() - start_time < timeout) and (total < 500)): 
        ts = []
        if rx.receive(ts):
            if sig.decodePWM(ts):
                #bw = BitWave(ts)
                #bw.showRaw()
                #bw.show()
                sig.show()
                total += 1
    return total

def main(argv=None):
    if argv is None:
        argv = sys.argv
    timeout = 5
    if len(argv) > 1:
        timeout = float(argv[1])

    GPIO.setmode(GPIO.BCM) 
    rx = Receiver(PIN_ASK_RX, PIN_ASK_EN)
    total = receive_loop(rx, timeout)
    GPIO.cleanup()
    print "%d received." % total

if __name__ == "__main__":
    sys.exit(main())

