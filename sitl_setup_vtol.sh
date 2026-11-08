#!/bin/bash

LAT="${1}"; LON="${2}"
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname -- "$SCRIPT_DIR")"
PARAM_FILE="$SCRIPT_DIR/mav_0_1.parm"

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
. ~/.profile
source ~/.bashrc
source ~/.bash_aliases
shopt -s expand_aliases
sf

if [[ -x "$REPO_ROOT/venv/bin/mavproxy.py" ]]; then
	MAVPROXY="$REPO_ROOT/venv/bin/mavproxy.py"
else
	MAVPROXY="$(command -v mavproxy.py || true)"
fi
if [[ -z "$MAVPROXY" ]]; then
	echo "Error: mavproxy.py was not found. Install MAVProxy in the project venv." >&2
	exit 1
fi
MAVPROXY_PYTHONPATH="/usr/lib/python3/dist-packages"
if [[ -n "${PYTHONPATH:-}" ]]; then
	MAVPROXY_PYTHONPATH="$MAVPROXY_PYTHONPATH:$PYTHONPATH"
fi

pkill -f 'mavproxy.py --master=tcp:127.0.0.1:5760' 2>/dev/null || true


started=0
MARKER="SIM_VEHICLE: Waiting for SITL to exit"

while IFS= read -r line; do
  printf '%s\n' "$line"
  if [[ $started -eq 0 && "$line" == *"$MARKER"* ]]; then
  	started=1
	if [[ "$*" == *"--headless"* ]]; then
		echo "Running headless mode..."
		PYTHONPATH="$MAVPROXY_PYTHONPATH" "$MAVPROXY" --master=tcp:127.0.0.1:5760 --daemon --out=127.0.0.1:14550 --out=127.0.0.1:14551 --streamrate=-1 >/dev/null &
	else
		echo "Running with console and map..."
		PYTHONPATH="$MAVPROXY_PYTHONPATH" "$MAVPROXY" --master=tcp:127.0.0.1:5760 --map --console --out=127.0.0.1:14550 --out=127.0.0.1:14551 --streamrate=-1 &
	fi
  fi
done < <(
  PYTHONUNBUFFERED=1 stdbuf -oL -eL \
  sim_vehicle.py -j4 -v Plane -f quadplane --no-mavproxy -w \
    --add-param-file="$PARAM_FILE" -l "${LAT},${LON},0,0" 2>&1
)

