# Radio frequency ASK/OOK decoder/encoder, transmitter/receiver

315/433MHz ASK/OOK transmitting/receving with cheap (RMB 5) transmitter/receiver modules, no HackRF needed.

- Platform: Linux (Raspberry Pi)
- Ver: 0.3
- Updated: 9/17/2017
- Created: 8/7/2017
- Author: loblab

## Hardware

- Raspberry Pi 2/3
- ASK/OOK transmitter/receiver

## Usage

- ask_tx.py: Send ASK/OOK commands in ask_confg.py
- ask_tx.py: Receive ASK/OOK signals and auto decode
- ask_monitor.py: Receive/decode ASK/OOK signals & compare with ommands in ask_config.py, then save to log file, and take action optionally.

## Setup

```bash
sudo apt-get install python-pip
sudo pip install bitstring
cp ask_config_sample.py ask_config.py
```

Connect transmitter/receiver to Pi's GND/VCC/GPIO, and modify ask_config.py

## History

- 0.3 (8/31/2017): Receiver supports signal without start high/low level, any gap can devide signals; added monitor & action
- 0.2 (8/11/2017): OOP; based on timestamp instead of sample count; don't use callback
- 0.1 (8/7/2017) : Initial version, support decode/encode, transmitter/receiver

