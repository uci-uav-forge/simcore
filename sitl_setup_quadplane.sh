#!/bin/bash

LAT="${1}"; LON="${2}"
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"

if [[ -z "$LAT" || -z "$LON" ]]; then
	echo "Error: latitude and longitude arguments are required." >&2
	echo "Usage: $0 <latitude> <longitude> [--headless]" >&2
	exit 1
fi

cleanup() {
	echo -e "\nCleaning up..."
	pkill -TERM -f 'mavproxy.py --master=tcp:127.0.0.1:5760' 2>/dev/null || true
	if [[ -n "${SIM_VEHICLE:-}" ]]; then
		pkill -TERM -f "$SIM_VEHICLE" 2>/dev/null || true
	fi
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

SIM_VEHICLE="$(command -v sim_vehicle.py || true)"
if [[ -z "$SIM_VEHICLE" ]]; then
	echo "Error: sim_vehicle.py was not found. Set up the ArduPilot SITL environment." >&2
	exit 1
fi


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
		echo "Running with console..."
		PYTHONPATH="$MAVPROXY_PYTHONPATH" "$MAVPROXY" --master=tcp:127.0.0.1:5760 --map --console --out=127.0.0.1:14550 --out=127.0.0.1:14551 --streamrate=-1 &
	fi
  fi
done < <(
  PYTHONUNBUFFERED=1 stdbuf -oL -eL \
  "$SIM_VEHICLE" -j4 -v Plane -f quadplane --no-mavproxy -w -l "${LAT},${LON},0,0" 2>&1
)

