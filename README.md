# Radio frequency ASK/OOK decoder/encoder, transmitter/receiver

315/433MHz ASK/OOK transmitting/receving with cheap (RMB 5) transmitter/receiver modules, no HackRF needed.

- Features: supports PWM, Biphase(Manchester) code; dump to/load from files; compare signals, trigger actions
- Platform: Linux (Raspberry Pi)
- Ver: 0.6
- Updated: 9/30/2017
- Created: 8/7/2017
- Author: loblab

![ASK/OOK modules and Raspberry Pi](https://raw.githubusercontent.com/loblab/rfask/master/rfask.jpg)

## Hardware

- Raspberry Pi 2/3
- ASK/OOK transmitter/receiver

## Usage

Run programs with '-h' option to see details.

- ask_tx.py: Send ASK/OOK commands in ask_confg.py
- ask_rx.py: Receive ASK/OOK signals and auto decode, save to files, optionally trigger actions for specified signals

- test.py: self test cases. run without device. 

![ASK/OOK send and receive](https://raw.githubusercontent.com/loblab/rfask/master/screenshot.png)

## Setup

```bash
sudo apt-get install python-pip
sudo pip install bitstring
cp ask_config_sample.py ask_config.py
```

Connect transmitter/receiver to Pi's GND/VCC/GPIO, and modify ask_config.py for your RF devices.

## History

- 0.6 (9/27/2017): Reorganized main programs, OOP based; merged ask_monitor.py to ask_rx.py; more error checks & protections
- 0.5 (9/24/2017): Supports command line options; can transmit multiple commands/files and wait
- 0.4 (9/23/2017): Supports biphase(Manchester) decoding/encoding; Auto detect signal type; test scripts support multiple cases
- 0.3 (8/31/2017): Receiver supports signal without start high/low level, any gap can devide signals; added monitor & action
- 0.2 (8/11/2017): OOP; based on timestamp instead of sample count; don't use callback
- 0.1 (8/7/2017) : Initial version, support decode/encode, transmitter/receiver

