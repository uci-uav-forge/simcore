# SimCore

Launch ArduPilot's built-in software-in-the-loop (SITL) simulation for Copter or
QuadPlane. This branch contains the two launchers, `cleanup`, this README, and
`.env`. The executables are Python files using
`#!/usr/bin/env python3`, so no `python3` prefix is needed. The VTOL launcher
reuses the main launcher with QuadPlane settings.

## Checkout layout

The launchers find ArduPilot relative to their own location, so they work from
any working directory:

```text
uavf2027/
├── ardupilot/
│   └── Tools/autotest/sim_vehicle.py
└── simcore/
    ├── .env
    ├── README.md
    ├── cleanup
    ├── sitl_setup
    └── sitl_setup_vtol
```

From the `uavf2027` root, initialize the required repositories and ArduPilot's
build dependencies:

```bash
git submodule update --init ardupilot simcore
git -C ardupilot submodule update --init --recursive
```

## Install prerequisites

Before running either launcher, install Git, Bash, Python 3, a native C/C++
compiler and build tools, and ArduPilot's Python dependencies (including
`pymavlink`, `MAVProxy`, and `pexpect`). Use ArduPilot's prerequisite installer
for your platform to install the complete dependency set.

The `uavf2027` installer will already do this for you.

The cleanup executable also requires `psutil` in the active Python environment:

```bash
python3 -m pip install psutil
```

### Check the active environment

The Python environment used by `python3` must contain ArduPilot's dependencies,
and `mavproxy.py` must be on `PATH`:

```bash
python3 -c 'import pymavlink, MAVProxy, pexpect'
command -v mavproxy.py
```

If either check fails, activate the environment used by the prerequisite
installer. The launchers do not source personal shell startup files or require
aliases.

## Run a simulation

From the `uavf2027` root:

```bash
# Copter with MAVProxy map and console
./simcore/sitl_setup 33.6405 -117.8443

# QuadPlane (VTOL) with MAVProxy map and console
./simcore/sitl_setup_vtol 33.6405 -117.8443

# No graphical windows or interactive MAVProxy prompt
./simcore/sitl_setup 33.6405 -117.8443 --headless
./simcore/sitl_setup_vtol 33.6405 -117.8443 --headless
```

Both launchers build SITL on startup, set the supplied latitude and longitude
with altitude and heading set to zero, and reset simulated parameters (`-w`).
MAVProxy connects to SITL over TCP port 5760 and forwards MAVLink to local UDP
ports 14550 and 14551 for the GCS and autonomy clients.

Headless mode stays in the foreground; use Ctrl-C to stop either mode.
ArduPilot manages simulation process cleanup. Run one simulation at a time
because both launchers use the same ports. Runtime state and logs are written
under a temporary directory, printed at startup. SITL process output appears
in the launcher terminal.

## Stop simulation processes

From any working directory, execute the cleanup file using its path. From the
`uavf2027` root:

```bash
./simcore/cleanup
```

## Override the ArduPilot path

The default is `../ardupilot` relative to `simcore/`. The `.env` file
sets `ARDUPILOT_PATH` (quote paths containing spaces); the super-repo installer can update this entry for the
current checkout. An exported environment variable takes precedence:

```bash
ARDUPILOT_PATH=/path/to/ardupilot ./simcore/sitl_setup 33.6405 -117.8443 --headless
```

Relative overrides are resolved from `simcore/`. `.env` values are parsed as
data; shell commands and variable expansion are not evaluated.
