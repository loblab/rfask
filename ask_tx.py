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
import os.path
from bitstring import *
from ask_config import *
from ask_signal import *
from ask_device import *

def list_command():
    for key in sorted(ASK_DATA):
        print key,
    print

def play_command(tx, cmd, repeat=3):
    cmdcfg = ASK_DATA[cmd]
    sig = SignalAuto(cmdcfg)
    wave = sig.encode()
    sig.show()
    wave.show()
    for i in range(repeat):
        print i + 1
        tx.send(wave)
    return True

def play_file(tx, index, repeat=3):
    filename = DATA_FILE % index
    if not os.path.isfile(filename):
        return False
    sig = SignalAuto()
    with open (filename, 'rb') as fp:
        sig.load(fp)
    wave = sig.encode()
    sig.show()
    wave.show()
    for i in range(repeat):
        print i + 1
        tx.send(wave)
    return True

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
    elif cmd.isdigit():
        play_file(tx, int(cmd))
    else:
        play_command(tx, cmd)

    GPIO.cleanup()

if __name__ == "__main__":
    sys.exit(main())

