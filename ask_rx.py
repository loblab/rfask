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

from ask_prog import *
import copy

class Program(ProgramBase):

    def init_arguments(self):
        self.argps.add_argument('-t', dest='timeout', type=int, default=900,
            help="run TIMEOUT seconds then quit the program. default 900")
        self.argps.add_argument('-s', dest='save', action='store_true',
            help="save received signals to files (DATA_FILE in ask_config.py)")
        self.argps.add_argument('-l', dest='log', action='store_true',
            help="log received signals to text log file (LOG_FILE in ask_config.py)")
        self.argps.add_argument('-a', dest='action', action='store_true',
            help="Take actions on specified signals (ASK_ACTION in ask_config.py)")
        self.argps.add_argument('-u', dest='unique', action='store_true',
            help="Ingore duplicated signals in 0.5 second")
        self.argps.add_argument('-m', dest='monitor', action='store_true',
            help="Monitor mode, log signals & take actions, same as -l -a -u -t %d" % 864000)
        self.argps.add_argument('-d', dest='debug', type=int, default=0, choices=range(4),
            help="debug info level, greater for more. default 0")
        self.argps.add_argument('-p', dest='period', type=float, default=SAMPLE_PERIOD,
            help="sample period in ms. default %.2f" % SAMPLE_PERIOD)

    def init_device(self):
        self.rx = Receiver(PIN_ASK_RX, PIN_ASK_EN, MAX_WAVE_LEN, self.args.period)

    def process(self):
        if self.args.monitor:
            self.args.log = True
            self.args.action = True
            self.args.unique = True
            self.args.timeout = 864000
        prev_sig = None
        prev_ts = 0
        total = 0
        findex = self.next_file_index()
        msg = "Receive signals for %d seconds... (Ctrl+C to quit)" % self.args.timeout
        print msg
        if self.args.log:
            self.log_msg(msg)
        start_time = time.time()
        sig = Signal()
        while (time.time() - start_time < self.args.timeout): 
            if self.quit_flag:
                break
            wave = self.rx.receive()
            if wave:
                if self.args.debug == 3:
                    print time.strftime('%H:%M:%S <=', time.localtime(time.time())),
                    wave.show()
                if sig.decode(wave):
                    ts = time.time()
                    print time.strftime('%H:%M:%S <=', time.localtime(ts)),
                    if self.args.unique:
                        if ts - prev_ts < 0.5 and sig == prev_sig:
                            prev_ts = ts
                            print "duplicated, ignored"
                            continue
                        else:
                            prev_ts = ts
                            prev_sig = copy.copy(sig)
                    total += 1
                    if self.args.save:
                        filename = DATA_FILE % findex
                        print "FILE %d: " % findex,
                        with open(filename, 'wb') as fp:
                            sig.dump(fp)
                        findex += 1
                    if self.args.action or self.args.log or self.args.debug > 0:
                        cmd = self.find_command(sig)
                        msg = "%-10s - %s" % (cmd, str(sig))
                    else:
                        msg = str(sig)
                    print msg
                    if self.args.debug == 2:
                        wave.show()
                    if self.args.log:
                        self.log_msg(msg)
                    if self.args.action:
                        self.run_action(cmd)
        msg = "%d signals received." % total
        print msg
        if self.args.log:
            self.log_msg(msg)
        return 0

if __name__ == "__main__":
    prog = Program("R<X", "Receive & decode ASK/OOK signals, save to files, take actions on specified signals")
    sys.exit(prog.main())

