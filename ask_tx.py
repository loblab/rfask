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
import argparse
import re
from bitstring import *
from ask_config import *
from ask_signal import *
from ask_device import *

def list_commands(debug=0):
    if debug == 0:
        print "Commands:",
    for cmd in sorted(ASK_DATA):
        if debug == 0:
            print cmd,
        elif debug >= 1:
            cmdcfg = ASK_DATA[cmd]
            sig = SignalAuto(cmdcfg)
            print "CMD %9s:" % cmd,
            sig.show()
    if debug == 0:
        print

def list_files(debug=0):
    i = 0
    while True:
        i += 1
        filename = DATA_FILE % i
        if not os.path.isfile(filename):
            break
        if debug >= 1:
            sig = SignalAuto()
            with open (filename, 'rb') as fp:
                sig.load(fp)
            print "FILE %6s:" % i,
            sig.show()
    if debug == 0:
        print "Files: 1~%d" % (i - 1)

def play_command(tx, cmd, repeat=3, debug=0):
    cmdcfg = ASK_DATA[cmd]
    sig = SignalAuto(cmdcfg)
    wave = sig.encode()
    print "CMD %9s:" % cmd,
    sig.show()
    if debug >= 1:
        wave.show()
    for i in range(repeat):
        if debug >= 2:
            print i + 1
        tx.send(wave)
    return True

def play_file(tx, index, repeat=3, debug=0):
    filename = DATA_FILE % index
    if not os.path.isfile(filename):
        return False
    sig = SignalAuto()
    with open (filename, 'rb') as fp:
        sig.load(fp)
    wave = sig.encode()
    print "FILE %d: " % index,
    sig.show()
    if debug >= 1:
        wave.show()
    for i in range(repeat):
        if debug >= 2:
            print i + 1
        tx.send(wave)
    return True

def main():
    parser = argparse.ArgumentParser(version=VERSION,
        description="Transmit ASK/OOK commands in ask_config.py or in saved files") 

    parser.add_argument('commands', metavar='command', type=str, nargs='*', 
        help="command name; file index (1~N); or time (e.g. 1.5s) to wait")
    parser.add_argument('-r', dest='repeat', type=int, default=5, 
        help="repeat count for each command. default 5")
    parser.add_argument('-c', dest='lscmd', action='store_true', 
        help="list available commands (in ask_config.py)")
    parser.add_argument('-f', dest='lsfile', action='store_true', 
        help="list available files (recorded by ask_rx.py)")
    parser.add_argument('-d', dest='debug', type=int, default=0, choices=range(3), 
        help="debug info level, greater for more. default 0")

    args = parser.parse_args()

    if len(sys.argv) == 1:
        return parser.print_help()

    if args.lscmd:
        list_commands(args.debug)

    if args.lsfile:
        list_files(args.debug)

    if len(args.commands) == 0:
        return 0

    re_wait = re.compile('(\d+\.?\d*)s')

    GPIO.setmode(GPIO.BCM) 

    tx = Transmitter(PIN_ASK_TX)

    for cmd in args.commands:
        print time.strftime('%H:%M:%S -', time.localtime(time.time())),
        if cmd == 'lock':
            print "Lock"
            tx.lock()
        elif cmd == 'unlock':
            print "Unlock"
            tx.unlock()
        else:
            m =  re_wait.match(cmd)
            if (m):
                wait = float(m.groups()[0])
                print "Wait %.1fs" % wait 
                time.sleep(wait)
            elif cmd.isdigit():
                play_file(tx, int(cmd), args.repeat, args.debug)
            else:
                play_command(tx, cmd, args.repeat, args.debug)

    GPIO.cleanup()
    return 0

if __name__ == "__main__":
    sys.exit(main())

