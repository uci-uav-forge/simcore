import random
import subprocess
import numpy as np
from pymap3d import geodetic2enu
from shapely.geometry import Polygon, Point
from launch import LaunchDescription, LaunchService
from launch_ros.actions import Node as LaunchNode

from .target_model import TargetModel
from .modify_sdf import generate_modified_sdf

from .targets import CANOPY1, CANOPY2, HUMAN1, HUMAN2, STOP_SIGN

def random_point_in_polygon(polygon: Polygon) -> np.ndarray:
    """Finds a random coordinate strictly inside the given Shapely polygon."""
    minx, miny, maxx, maxy = polygon.bounds
    while True:
        p = Point(random.uniform(minx, maxx), random.uniform(miny, maxy))
        if polygon.contains(p):
            return np.array([p.x, p.y])

def delete_model(model_name: str):
    """Uses Gazebo transport service to remove a model by name."""
    subprocess.run([
        "gz", "service", "-s", "/world/map/remove", 
        "--reqtype", "gz.msgs.Entity", 
        "--req", f'type: MODEL; name: "{model_name}"', 
        "--reptype", "gz.msgs.Boolean"
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


class TargetManager:
    def __init__(self):

        self.canopy_targets = [
            CANOPY1,
            CANOPY2,
        ]
        self.human_targets = [
            HUMAN1,
            HUMAN2,
        ]
        self.noise = [
            #TODO: add more noise targets
        ]
        self.active_targets = []
        self.target_radius = 5.0

    def _spawn_single_model(self, model: TargetModel, spawn_name: str, x: float, y: float, z: float = 0.2):
        roll, pitch, yaw = model.get_orient()
        scale = model.get_scale()
        hsv = model.get_HSV()

        # Generate the dynamic SDF string from the template
        sdf_filepath = f"{model.get_path()}/model.sdf"
        sdf_string = generate_modified_sdf(sdf_filepath, scale, hsv)

        ld = LaunchDescription([
            LaunchNode(
                package="ros_gz_sim",
                executable="create",
                name="spawn_" + spawn_name,
                output="screen",
                arguments=[
                    "-string", sdf_string,
                    "-name", spawn_name,
                    "-x", str(x),
                    "-y", str(y),
                    "-z", str(z),
                    "-R", str(roll),
                    "-P", str(pitch),
                    "-Y", str(yaw),
                    "--ros-args", "--log-level", "error",
                ],
            )
        ])
        ls = LaunchService()
        ls.include_launch_description(ld)
        ls.run()

    def delete_all_targets(self):
        for name in self.active_targets:
            delete_model(name)
        self.active_targets.clear()

    def respawn_targets(self, dropzone_gps_boundary, home_lat, home_lon):
        self.delete_all_targets()

        # Convert GPS bounds to ENU Cartesian polygon
        dropzone_local = [
            np.array(geodetic2enu(lat, lng, 0.0, home_lat, home_lon, 0.0))[:2]
            for lat, lng in dropzone_gps_boundary
        ]
        dropzone_polygon = Polygon(dropzone_local)

        models_to_spawn = random.sample(self.canopy_targets, 1) + random.sample(self.human_targets, 1)
        if len(self.noise) >= 2:
            models_to_spawn.extend(random.sample(self.noise, 2))

        random.shuffle(models_to_spawn)
        target_positions = []

        max_attempts = 200 
        for i, model in enumerate(models_to_spawn):
            target_pos = None
            attempts = 0
            
            while attempts < max_attempts:
                candidate_pos = random_point_in_polygon(dropzone_polygon)
                if not any(np.linalg.norm(candidate_pos - p) < 2 * self.target_radius for p in target_positions):
                    target_pos = candidate_pos
                    break
                attempts += 1
            
            if target_pos is None:
                print(f"Error: Could not find valid location for {model.name}. Skipping.")
                continue 
                
            target_positions.append(target_pos)
            spawn_name = f"target_{i}"
            
            self._spawn_single_model(model, spawn_name, target_pos[0], target_pos[1])
            self.active_targets.append(spawn_name)

        return target_positions