#!/bin/bash

echo -e "\nCleaning up..."
pkill mavproxy
pkill xterm
pkill 'bash <defunct>'
#pkill python3
rm -f eeprom.bin
rm -f mav.parm
rm -f mav.tlog
rm -f mav.tlog.raw
rm -f dump*
rm -rf terrain
rm -rf logs
rm -f *.BIN
pkill -9 -f "ardupilot"
echo -e "\nClean up complete. Exiting..."
