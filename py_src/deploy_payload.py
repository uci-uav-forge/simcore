import subprocess
import threading
import json
import numpy as np
from pathlib import Path
from launch import LaunchDescription, LaunchService
from launch_ros.actions import Node as LaunchNode

from .spawn_targets import delete_model

class GzPositionProvider:
    def __init__(self, topic: str = "/world/map/model/iris/joint_state"):
        self.topic = topic
        self.position = np.zeros(3)
        self.running = True
        self.process = None
        self.thread = threading.Thread(target=self._run_process, daemon=True)
        self.thread.start()

    def _parse_json_output(self, json_line):
        try:
            data = json.loads(json_line)
            pos = data.get("pose", {}).get("position", {})
            self.position = np.array([pos.get("x", 0.0), pos.get("y", 0.0), pos.get("z", 0.0)])
        except json.JSONDecodeError:
            pass

    def _run_process(self):
        command = ["gz", "topic", "--echo", "--json-output", "--topic", self.topic]
        self.process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        while self.running:
            line = self.process.stdout.readline()
            if line.strip():
                self._parse_json_output(line)
        self.process.terminate()

    def stop(self):
        self.running = False
        self.thread.join()

    def get_position(self):
        return self.position

class PayloadDropper:
    def __init__(self, log_func):
        self.tracker = GzPositionProvider(topic="/world/map/model/iris/joint_state")
        base_path = Path(__file__).parent.parent.resolve()
        model_path = str(base_path / "ardu_ws/src/ardupilot_gazebo/models")
        self.beacon_path = model_path + "/beacon"
        self.waterbottle_path = model_path + "/waterbottle"
        self.drop_count = 0
        self.log_func = log_func
        self.active_models = []

    def reset(self):
        for name in self.active_models:
            delete_model(name)
            self.log_func(f"Cleared {name}")
        self.active_models.clear()

    def drop_payload(self, item : str = "beacon"):
        """
        Grabs the current drone position, spawns the payload ("beacon" or "waterbottle") <br> 0.5m below it, 
        and returns the (x, y, z) coordinates of the drop. <br>
        #TODO: If parachute with model, adjust so drop x y z is final pos not drop pos.
        """
        drone_pos = self.tracker.get_position()
        drop_x, drop_y, drop_z = drone_pos[0], drone_pos[1], drone_pos[2] - 0.5
        model_name = f"dropped_payload_{item}_{self.drop_count}"
        self.drop_count += 1
        payload_path = self.beacon_path if item == "beacon" else self.waterbottle_path
        ld = LaunchDescription([
            LaunchNode(
                package="ros_gz_sim",
                executable="create",
                name="spawn_" + model_name,
                arguments=[
                    "-file", payload_path,
                    "-name", model_name,
                    "-x", str(drop_x), "-y", str(drop_y), "-z", str(drop_z),
                    "--ros-args", "--log-level", "error",
                ],
            )
        ])
        
        ls = LaunchService()
        ls.include_launch_description(ld)
        ls.run()
        drop_pos = np.array([drop_x, drop_y, drop_z])
        self.active_models.append(model_name)
        self.log_func(f"Dropped {item} at: {drop_pos}")
        return drop_pos