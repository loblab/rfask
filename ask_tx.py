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
from ask_config import *
from ask_struct import *
from ask_device import *

def list_command():
    for key in sorted(ASK_DATA):
        print key,
    print


def play_command(tx, cmd):
    cmdcfg = ASK_DATA[cmd]
    repeat = cmdcfg[0]
    sig = Signal(BitArray(cmdcfg[6]), cmdcfg[4], cmdcfg[5]*1e-3, cmdcfg[1]*1e-3, cmdcfg[2]*1e-3, cmdcfg[3]*1e-3)
    ts = []
    sig.encode(ts)
    BitWave(ts).show()
    for i in range(0, repeat):
        print i + 1
        tx.send(ts)

def main(argv=None):
    if argv is None:
        argv = sys.argv

    if len(argv) < 2:
        list_command()
        return 1

    cmd = argv[1]
    print cmd

    GPIO.setmode(GPIO.BCM) 

    tx = Transmitter(PIN_ASK_TX)

    if cmd == 'lock':
        tx.lock()
    elif cmd == 'unlock':
        tx.unlock()
    else:
        play_command(tx, cmd)

    GPIO.cleanup()

if __name__ == "__main__":
    sys.exit(main())

