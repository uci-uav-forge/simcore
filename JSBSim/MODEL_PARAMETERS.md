# UAVF 4+1 VTOL JSBSim Model

`uavf_4plus1.xml` is a baseline model for a fixed-wing aircraft with four vertical lift motors in a square and one forward-facing cruise motor. JSBSim uses body axes of +X forward, +Y right, and +Z down; the lift motor pitch of 90 degrees rotates thrust upward.

## Aircraft XML parameters

| XML section / value | Parameter | Value | Unit | Calibration source or note |
| --- | --- | ---: | --- | --- |
| `metrics/wingarea` | Wing reference area | 0.72 | m^2 | CAD planform area |
| `metrics/wingspan` | Wing span | 2.40 | m | CAD |
| `metrics/chord` | Mean aerodynamic chord | 0.30 | m | CAD / area-span check |
| `metrics/htailarea` | Horizontal tail area | 0.12 | m^2 | CAD |
| `metrics/htailarm` | Horizontal tail arm | 0.92 | m | CG to tail aerodynamic center |
| `metrics/vtailarea` | Vertical tail area | 0.08 | m^2 | CAD |
| `metrics/vtailarm` | Vertical tail arm | 0.92 | m | CG to tail aerodynamic center |
| `metrics/AERORP` | Aerodynamic reference point | (0, 0, 0) | m | Set from aerodynamic mesh / wind-tunnel reference |
| `mass_balance/emptywt` | Empty mass | 3.80 | kg | Weigh the assembled aircraft |
| `mass_balance/CG` | Center of gravity | (0, 0, -0.04) | m | Balance with flight battery and payload installed |
| `mass_balance/ixx, iyy, izz` | Principal inertias | 0.42, 0.29, 0.62 | kg m^2 | Measure or calculate from CAD mass properties |
| `mass_balance/ixy, ixz, iyz` | Product inertias | 0, 0, 0 | kg m^2 | Replace if CG axes are not principal axes |
| `ground_reactions/*/location` | Contact points | left/right main and nose | m | Measure wheel locations and loaded gear height |
| `ground_reactions/*/static_friction` | Static tire friction | 0.80 | ratio | Tire and runway test |
| `ground_reactions/*/dynamic_friction` | Dynamic tire friction | 0.50 | ratio | Tire and runway test |
| `ground_reactions/*/rolling_friction` | Rolling friction | 0.02 | ratio | Tire test |
| `ground_reactions/*/spring_coeff` | Gear spring rate | 1800 / 1200 | N/m | Landing-gear compression test |
| `ground_reactions/*/damping_coeff` | Gear damping | 220 / 180 | N/m/s | Drop test |
| `flight_control/*/range` | Elevator, aileron, rudder limits | +/-0.35 | rad | Servo geometry and measured travel |
| `aerodynamics/CD0` | Zero-lift drag coefficient | 0.035 | coefficient | Glide test or wind tunnel |
| `aerodynamics/CDi` | Induced-drag factor | 0.045 | coefficient | Lift-drag polar |
| `aerodynamics/CLalpha` | Lift curve | -0.75, 0.25, 1.15, 0.75 | coefficient | Wind tunnel or flight-test polar |
| `aerodynamics/CLde` | Elevator lift derivative | 0.30 | 1/rad | Control derivative test |
| `aerodynamics/CYb` | Side-force beta derivative | -0.85 | 1/rad | Wind tunnel or sideslip test |
| `aerodynamics/Clb, Clp, Clda` | Roll derivatives | -0.10, -0.45, 0.16 | 1/rad | Roll-rate and aileron tests |
| `aerodynamics/Cmalpha, Cmde, Cmq` | Pitch derivatives | -0.55, -0.85, -8.0 | 1/rad | Trim and pitch-rate tests |
| `aerodynamics/Cnb, Cnr, Cndr` | Yaw derivatives | 0.12, -0.18, -0.08 | 1/rad | Yaw-rate and rudder tests |

## Propulsion parameters

| XML file / value | Parameter | Value | Unit | Calibration source or note |
| --- | --- | ---: | --- | --- |
| `uavf_lift_motor.xml/power` | Lift motor mechanical power limit | 1200 | W each | Motor dynamometer; total nominal 4.8 kW |
| `uavf_cruise_motor.xml/power` | Cruise motor mechanical power limit | 1500 | W | Motor dynamometer |
| `uavf_lift_prop.xml/diameter` | Lift propeller diameter | 12 | in | Installed propeller |
| `uavf_cruise_prop.xml/diameter` | Cruise propeller diameter | 14 | in | Installed propeller |
| `*/numblades` | Propeller blade count | 2 | blades | Installed propeller |
| `*/gearratio` | Motor-to-propeller ratio | 1.0 | ratio | Measure gearing; update for reduction drives |
| `*/ixx` | Propeller rotational inertia | 0.00008 / 0.00012 | kg m^2 | CAD or spin-up test |
| `*/C_THRUST` | Thrust coefficient table | see XML | coefficient | Replace with static and forward-flight prop data |
| `*/C_POWER` | Power coefficient table | see XML | coefficient | Replace with dynamometer data |
| engine order | Cruise then Quad-X motors 1–4 | cruise, front-right, rear-right, rear-left, front-left | — | The JSBSim bridge maps engine 0 to fixed-wing throttle and motors 1–4 to outputs 5–8 |
| four lift locations | Motor square arms | x +/-0.42, y +/-0.55 | m | Motor shaft locations from CG |
| four lift orientations | Vertical thrust direction | pitch 90 | deg | Verify sign in a hover test |
| four lift `sense` values | Quad-X motor 1–4 rotation | +, -, +, - | sign | Match ArduPilot motor order and verify prop rotation |
| cruise location | Forward motor shaft | (0.86, 0, 0) | m | Measure from CG |
| cruise orientation | Forward thrust direction | pitch 0 | deg | Verify +X thrust direction |

## Required calibration sequence

1. Replace mass, CG, inertia, motor power, propeller tables, and contact points with measured values.
2. Verify each motor's thrust direction and `sense` at low throttle in JSBSim.
3. Tune the lift-prop thrust and power tables from a static thrust stand, then validate at forward airspeeds.
4. Tune `CL`, `CD`, and control derivatives from glide, trim, and frequency-response flight tests.
5. Add the aircraft directory to the ArduPilot JSBSim aircraft search path before selecting it with `sim_vehicle.py`.
