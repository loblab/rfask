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

# ASK configuration data sample
# Copy this file to ask_config.py, add your own config data,
# Don't commit your config data since it is security!

# pin number in GPIO.BCM mode
PIN_ASK_TX = 14 
PIN_ASK_EN = 15
PIN_ASK_RX = 18

SAMPLE_PERIOD = 0.05

# Make sure the folders existed, and writable
LOG_FILE = '/var/loblab/rfask.log'
DATA_FILE = "/home/loblab/data/%06d.dat"

ASK_CMD = {
#       name: 'PWM', start-high, start-low, stop-low, duty, period, bits
#       name: 'BPS', , stop-low, leading, period, bits
     'hello': ['PWM', 5.0, 0.5, 1.0, 0.75, 1.0, '0x68656c6c6f0'],
     'world': ['BPS', 5.0, 3.0, 31, 0.5, '0x68656c6c6f0'],
     'test1': ['PWM', 5.0, 1.0, 8.0, 0.75, 1.0, '0x68656c6c6f'],
     'test2': ['PWM', 5.0, 1.0, 8.0, 0.75, 1.0, '0x68656c6c6f, 0b1'],
     'test3': ['PWM', 5.0, 1.0, 8.0, 0.75, 1.0, '0x68656c6c6f, 0b01'],
     'test4': ['BPS', 5.0, 1.0, 39, 1.0, '0x68656c6c6f'],
}

ASK_ACTION = {
    #command: script
    'hello': 'echo Hello world!',
    'world': 'echo World is great!',
    'pc-wol': 'pcon',
}

