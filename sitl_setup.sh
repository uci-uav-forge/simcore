#!/bin/bash

LAT="${1}"; LON="${2}"

cleanup() {
	echo -e "\nCleaning up..."
	pkill -9 mavproxy
	pkill xterm
	pkill 'bash <defunct>'
	pkill python3
	rm -f eeprom.bin
	rm -f mav.parm
	rm -f mav.tlog
	rm -f mav.tlog.raw
	rm -rf terrain
	rm -f *.BIN
	echo -e "\nClean up complete. Exiting..."
}
trap cleanup SIGINT

echo "Starting sim..."
source ~/.bashrc
. ~/.profile

started=0
MARKER="SIM_VEHICLE: Waiting for SITL to exit"

while IFS= read -r line; do
  printf '%s\n' "$line"
  if [[ $started -eq 0 && "$line" == *"$MARKER"* ]]; then
  	started=1
	break
  fi
done < <(
  PYTHONUNBUFFERED=1 stdbuf -oL -eL \
  sim_vehicle.py -v copter --no-mavproxy -w -l "${LAT},${LON},0,0" 2>&1
)

if [[ "$*" == *"--headless"* ]]; then
	echo "Running headless mode..."
	mavproxy.py --master=tcp:127.0.0.1:5760 --daemon --out=127.0.0.1:14550 --out=127.0.0.1:14551 >/dev/null &
else
	echo "Running with console..."
	mavproxy.py --master=tcp:127.0.0.1:5760 --map --console --out=127.0.0.1:14550 --out=127.0.0.1:14551
	
fi

