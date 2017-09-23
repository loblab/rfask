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
import os
from bitstring import *
from ask_signal import *
from ask_device import *
from ask_config import *

LOG_FILE = '/var/loblab/ask_monitor.log'
Buttons = {}

def log_msg(msg):
    f = open(LOG_FILE, 'a')
    f.write(time.strftime('%Y/%m/%d %H:%M:%S - ', time.localtime(time.time())))
    f.write("%s\r\n" % msg)
    f.close()

def load_buttons():
    for key in ASK_DATA:
        cfg = ASK_DATA[key]
        Buttons[key] = SignalAuto(cfg)

def get_button(signal):
    for key in Buttons:
        if signal == Buttons[key]:
            return key
    return 'Unknown'

def ask_action(signal):
    key = get_button(signal)
    log_msg("%-10s - %s" % (key, str(signal)))
    if key == 'pc-wol':
        os.system("pcon")

def receive_loop(rx, timeout):
    start_time = time.time()
    sig = SignalAuto()
    while time.time() - start_time < timeout: 
        wave = rx.receive()
        if wave:
            if sig.decode(wave):
                #sig.show()
                ask_action(sig)
    return True

def main(argv=None):
    if argv is None:
        argv = sys.argv
    timeout = 5
    if len(argv) > 1:
        timeout = float(argv[1])

    load_buttons()
    GPIO.setmode(GPIO.BCM) 
    rx = Receiver(PIN_ASK_RX, PIN_ASK_EN)
    total = receive_loop(rx, timeout)
    GPIO.cleanup()

if __name__ == "__main__":
    sys.exit(main())

