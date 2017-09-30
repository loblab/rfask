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

import re
from ask_prog import *

class Program(ProgramBase):

    def init_arguments(self):
        self.argps.add_argument('commands', metavar='command', type=str, nargs='*',
            help="command name; file index (1~N); or time (e.g. 1.5s) to wait")
        self.argps.add_argument('-r', dest='repeat', type=int, default=5,
            help="repeat count for each command. default 5")
        self.argps.add_argument('-c', dest='lscmd', action='store_true',
            help="list available commands (in ask_config.py)")
        self.argps.add_argument('-f', dest='lsfile', action='store_true',
            help="list available files (recorded by ask_rx.py)")
        self.argps.add_argument('-l', dest='log', action='store_true',
            help="log messages to text log file (LOG_FILE in ask_config.py)")
        self.argps.add_argument('-d', dest='debug', type=int, default=0, choices=range(3),
            help="debug info level, greater for more. default 0")

    def init_device(self):
        self.tx = Transmitter(PIN_ASK_TX)

    def play_command(self, cmd):
        sig = self.commands.get(cmd)
        if sig is None:
            print "Warning: unknown command '%s'" % cmd
            return False
        wave = sig.encode()
        msg = "CMD %9s: %s" % (cmd, sig)
        print msg
        if self.args.log:
            self.log_msg(msg)
        if self.args.debug >= 1:
            wave.show()
        for i in range(self.args.repeat):
            if self.args.debug >= 2:
                print i + 1
            self.tx.send(wave)
        return True

    def play_file(self, index):
        filename = DATA_FILE % index
        if not os.path.isfile(filename):
            print "Warning: file %d does not exist" % index
            return False
        sig = Signal()
        with open (filename, 'rb') as fp:
            sig.load(fp)
        wave = sig.encode()
        msg = "FILE %d: %s" % (index, sig),
        print msg
        if self.args.log:
            self.log_msg(msg)
        if self.args.debug >= 1:
            wave.show()
        for i in range(self.args.repeat):
            if self.args.debug >= 2:
                print i + 1
            tx.send(wave)
        return True

    def play_list(self):
        re_wait = re.compile('(\d+\.?\d*)s')
        for cmd in self.args.commands:
            if self.quit_flag:
                break
            print time.strftime('%H:%M:%S =>', time.localtime(time.time())),
            if cmd == 'lock':
                print "Lock"
                self.tx.lock()
            elif cmd == 'unlock':
                print "Unlock"
                self.tx.unlock()
            else:
                m =  re_wait.match(cmd)
                if (m):
                    wait = float(m.groups()[0])
                    print "Wait %.1fs" % wait
                    time.sleep(wait)
                elif cmd.isdigit():
                    if not self.play_file(int(cmd)):
                        return False
                else:
                    if not self.play_command(cmd):
                        return False
        return True

    def process(self):
        if len(sys.argv) == 1:
            return self.list_commands(1)
        if self.args.lscmd:
            self.list_commands(self.args.debug)
        if self.args.lsfile:
            self.list_files(self.args.debug)
        if len(self.args.commands) == 0:
            return 1

        if not self.play_list():
            return -1

        return 0

if __name__ == "__main__":
    prog = Program("T>X", "Transmit ASK/OOK commands in ask_config.py or in saved files")
    sys.exit(prog.main())

