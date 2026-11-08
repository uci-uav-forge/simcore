#!/bin/bash

LAT="${1}"; LON="${2}"
USE_JSBSIM="${USE_JSBSIM:-1}"
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname -- "$SCRIPT_DIR")"
PARAM_FILE="$SCRIPT_DIR/mav_0_1.parm"

# Check for required latitude and longitude arguments.
if [[ -z "$LAT" || -z "$LON" ]]; then
	echo "Error: latitude and longitude arguments are required." >&2
	echo "Usage: $0 <latitude> <longitude> [--headless]" >&2
	exit 1
fi

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

if [[ "$USE_JSBSIM" != "0" && "$USE_JSBSIM" != "1" ]]; then
	echo "Error: USE_JSBSIM must be 0 or 1." >&2
	exit 1
fi

SIM_VEHICLE="$(command -v sim_vehicle.py || true)"
if [[ -z "$SIM_VEHICLE" ]]; then
	echo "Error: sim_vehicle.py was not found. Install ArduPilot SITL first." >&2
	exit 1
fi
SIM_VEHICLE_PATH="$(readlink -f "$SIM_VEHICLE")"
ARDUPILOT_AUTOTEST_DIR="$(dirname "$SIM_VEHICLE_PATH")"
MODEL_NAME="uavf_4plus1"
MODEL_SOURCE="$REPO_ROOT/simcore/JSBSim/aircraft/$MODEL_NAME"
ENGINE_SOURCE="$REPO_ROOT/simcore/JSBSim/engine"

if [[ "$USE_JSBSIM" == "1" ]]; then
	if [[ ! -f "$MODEL_SOURCE/$MODEL_NAME.xml" || ! -d "$ENGINE_SOURCE" ]]; then
		echo "Error: the $MODEL_NAME JSBSim model is missing from $REPO_ROOT/simcore/JSBSim." >&2
		exit 1
	fi
	link_model_file() {
		local source="$1"
		local destination="$2"
		if [[ -e "$destination" && ! -L "$destination" ]]; then
			echo "Error: refusing to replace existing file or directory: $destination" >&2
			exit 1
		fi
		ln -sfn "$source" "$destination"
	}
	mkdir -p "$ARDUPILOT_AUTOTEST_DIR/aircraft" "$ARDUPILOT_AUTOTEST_DIR/engine"
	link_model_file "$MODEL_SOURCE" "$ARDUPILOT_AUTOTEST_DIR/aircraft/$MODEL_NAME"
	for engine_file in "$ENGINE_SOURCE"/*.xml; do
		link_model_file "$engine_file" "$ARDUPILOT_AUTOTEST_DIR/engine/$(basename "$engine_file")"
	done
	FRAME="jsbsim:$MODEL_NAME"
else
	echo "Using ArduPilot's built-in QuadPlane SITL model (JSBSim disabled)."
	FRAME="quadplane"
fi

if [[ ! -f "$PARAM_FILE" ]]; then
	echo "Error: QuadPlane parameter file not found: $PARAM_FILE" >&2
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

# Prevent stale launchers from competing for the same SITL MAVLink stream.
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
	sim_vehicle.py -j4 -v Plane -f "$FRAME" --no-mavproxy -w \
		--add-param-file="$PARAM_FILE" -l "${LAT},${LON},0,0" 2>&1
)
