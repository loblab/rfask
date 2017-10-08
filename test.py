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

# Self test scripts

import time 
import sys
import random
import os.path
from bitstring import *
from ask_signal import *
from ask_config import *

DITHER = 0.0

def setDither20():
    global DITHER
    DITHER = 0.2
    return True

def setDither40():
    global DITHER
    DITHER = 0.4
    return True

def setDither60():
    global DITHER
    DITHER = 0.6
    return True

def testBitWave():
    wave = BitWave()
    wave.random()
    wave.show()
    return True

def testCodec(sig1, sig2, dither=0.0):
    global DITHER
    size = random.randint(13, 32)
    val = random.randint(257, 2**size)
    sig1.bits = BitArray('0x%x' % val)
    sig1.show()
    t1 = time.time()
    wave = sig1.encode()
    t2 = time.time()
    print "Encode time: %.2fms" % ((t2 - t1) * 1000)
    wave.dither(sig1.period * DITHER)
    wave.show()
    t1 = time.time()
    if sig2.decode(wave):
        t2 = time.time()
        print "Decode time: %.2fms" % ((t2 - t1) * 1000)
        sig2.show()
        return sig2 == sig1
    return False

def testCodecRaw():
    sig1 = SignalRaw()
    sig2 = SignalRaw()
    return testCodec(sig1, sig2)

def testCodecPWM75():
    sig1 = SignalPWM(0.75)
    sig2 = SignalPWM()
    return testCodec(sig1, sig2)

def testCodecPWM75Low():
    sig1 = SignalPWM(0.75, start1=0, start0=5e-3)
    sig2 = SignalPWM()
    return testCodec(sig1, sig2)

def testCodecBP():
    sig1 = SignalBP(39)
    sig2 = SignalBP()
    return testCodec(sig1, sig2)

def testAutoDecode():
    sig1 = SignalPWM(0.75)
    sig2 = Signal()
    b1 = testCodec(sig1, sig2)
    sig1 = SignalBP(39)
    b2 = testCodec(sig1, sig2)
    return b1 and b2

def testAutoInit():
    for key in ASK_CMD:
        cfg = ASK_CMD[key]
        sig = Signal(cfg)
        print key, 
        sig.show()
        wave = sig.encode()
        sig2 = Signal()
        if not sig2.decode(wave):
            print "testAutoInit: failed to decode"
            return False
        sig2.show()
        if sig2 != sig:
            print "testAutoInit: error in compare"
            return False
    return True

def testDump(filename, obj):
    obj.show()
    t1 = time.time()
    with open (filename, 'wb') as fp:
        obj.dump(fp)
    t2 = time.time()
    print "Dump time: %.2fms" % ((t2 - t1) * 1000)

def testLoad(filename, obj):
    t1 = time.time()
    with open (filename, 'rb') as fp:
      obj.load(fp)
    t2 = time.time()
    print "Load time: %.2fms" % ((t2 - t1) * 1000)
    obj.show()

def testStoreWave():
    tmpfile='/tmp/wave.dat'
    wave1 = BitWave()
    wave1.random()
    wave2 = BitWave()
    testDump(tmpfile, wave1)
    testLoad(tmpfile, wave2)
    return wave1 == wave2

def testStoreSignal(sig1, sig2):
    tmpfile='/tmp/signal.dat'
    size = random.randint(13, 32)
    val = random.randint(257, 2**size)
    sig1.bits = BitArray('0x%x' % val)
    testDump(tmpfile, sig1)
    testLoad(tmpfile, sig2)
    return sig1 == sig2

def testStoreRaw():
    sig1 = SignalRaw()
    sig2 = SignalRaw()
    return testStoreSignal(sig1, sig2)

def testStorePWM():
    sig1 = SignalPWM(0.75)
    sig2 = SignalPWM()
    return testStoreSignal(sig1, sig2)

def testStoreBP():
    sig1 = SignalBP(39)
    sig2 = SignalBP()
    return testStoreSignal(sig1, sig2)

def testLoadFiles():
    i = 0
    while True:
        i += 1
        filename = DATA_FILE % i
        if not os.path.isfile(filename):
            break
        #print i
        #print filename
        sig = Signal()
        with open (filename, 'rb') as fp:
            sig.load(fp)
        print "%3d:" % i,
        sig.show()
    return True

TEST_CASES = [
    [testBitWave, "testBitWave"],
    [testCodecRaw, "testCodecRaw"],
    [testCodecPWM75, "testCodecPWM 75%"],
    [testCodecPWM75Low, "testCodecPWM 75%, Low level start"],
    [testCodecBP, "testCodecBP(Biphase)"],
    [testAutoDecode, "testAutoDecode"],
    [testAutoInit, "testAutoInit"],
    [testStoreWave, "testStoreWave"],
    [testStoreRaw, "testStoreRaw"],
    [testStorePWM, "testStorePWM"],
    [testStoreBP, "testStoreBP"],
    [testLoadFiles, "testLoadFiles"],
    [setDither20, "setDither 20%"],
    [setDither40, "setDither 40%"],
    [setDither40, "setDither 60%"],
]

def list_cases():
    for i in range(len(TEST_CASES)):
        print "%2d: %s" % (i + 1, TEST_CASES[i][1])

def run_case(index):
    case = TEST_CASES[index - 1]
    print
    print "Case %d: %s" % (index, case[1])
    print '========================================='
    t1 = time.time()
    rc = case[0]()
    t2 = time.time()
    print '----------------------'
    print "%s. %.2f ms" % ('PASS' if rc else 'FAIL', (t2 - t1) * 1000)
    return rc
     
def run_cases(cases):
    passed = 0
    failed = 0
    t1 = time.time()
    for case in cases:
        rc = run_case(int(case))
        if rc:
            passed += 1
        else:
            failed += 1
    t2 = time.time()
    total = passed + failed
    if total > 1:
        print
        print '#########################################'
        print "%d/%d FAIL. %.2f ms" % (failed, total, (t2 - t1) * 1000)


def main(argv=None):
    if argv is None:
        argv = sys.argv
    if len(argv) < 2:
        list_cases()
        return 1
    if argv[1] == 'all':
        cases = range(1, len(TEST_CASES) + 1)
    else:
        cases = argv[1:]
    run_cases(cases)

if __name__ == "__main__":
    sys.exit(main())

