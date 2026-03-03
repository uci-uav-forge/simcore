import subprocess
import random
import numpy as np
from pathlib import Path
from pymap3d import geodetic2enu
from launch import LaunchDescription, LaunchService
from launch_ros.actions import Node as LaunchNode

def random_point_in_pca_rect(points):
    """
    Finds the best-fit oriented rectangle using PCA and samples a random point within it.
    """
    points = np.asarray(points)
    centroid = np.mean(points, axis=0)
    U, S, Vt = np.linalg.svd(points - centroid)
    axes = Vt.T
    proj_points = (points - centroid) @ axes
    min_proj, max_proj = proj_points.min(axis=0), proj_points.max(axis=0)
    rand_proj = np.random.uniform(min_proj, max_proj)
    return centroid + rand_proj @ axes.T

def delete_model(model_name: str):
    """
    Uses Gazebo transport service to remove a model by name.
    """
    subprocess.run([
        "gz", "service", "-s", "/world/map/remove", 
        "--reqtype", "gz.msgs.Entity", 
        "--req", f'type: MODEL; name: "{model_name}"', 
        "--reptype", "gz.msgs.Boolean"
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


class TargetManager:
    def __init__(self):
        
        base_path = Path(__file__).parent.parent.resolve()
        self.model_path = str(base_path / "ardu_ws/src/ardupilot_gazebo/models")
        
        self.canopy_targets = [
            f"{self.model_path}/canopy1",
            f"{self.model_path}/canopy2",
        ]
        self.human_targets = [
            f"{self.model_path}/human1",
            f"{self.model_path}/human2",
        ]
        self.noise = [ #TBD
            # f"{self.model_path}/stop_sign",
            # f"{self.model_path}/person_standing",
            # f"{self.model_path}/prius_hybrid",
            # f"{self.model_path}/robocup_3Dsim_ball",
            # f"{self.model_path}/motorcycle_0",
            # f"{self.model_path}/boat_0",
            # f"{self.model_path}/bat_0",
            # f"{self.model_path}/bed_0",
            # f"{self.model_path}/plane_0",
            # f"{self.model_path}/bus_0",
            # f"{self.model_path}/skis_0",
            # f"{self.model_path}/snowboard_0",
            # f"{self.model_path}/suitcase_0",
            # f"{self.model_path}/tennis_racket_0",
            # f"{self.model_path}/umbrella_0",
        ]

        self.active_targets = []
        self.target_radius = 5.0  # Used for checking spawn overlaps

    def _spawn_single_model(self, model_path, model_name, x, y, z=0.2):
        ld = LaunchDescription([
            LaunchNode(
                package="ros_gz_sim",
                executable="create",
                name="spawn_" + model_name,
                output="screen",
                arguments=[
                    "-file", model_path,
                    "-name", model_name,
                    "-x", str(x),
                    "-y", str(y),
                    "-z", str(z),
                    "--ros-args", "--log-level", "error",
                ],
            )
        ])
        ls = LaunchService()
        ls.include_launch_description(ld)
        ls.run()

    def respawn_targets(self, dropzone_gps_boundary, home_lat, home_lon, home_alt):
        """
        Clears old targets, calculates new ENU bounds, and randomly positions 
        the 2 guaranteed models + 2 randomly selected models.
        Returns a list of the 4 target (x, y) coordinate arrays.
        """
        for name in self.active_targets:
            delete_model(name)
        self.active_targets.clear()
        dropzone_local = [
            np.array(geodetic2enu(lat, lng, home_alt, home_lat, home_lon, home_alt))[:2]
            for lat, lng in dropzone_gps_boundary
        ]
        models_to_spawn = random.sample(self.canopy_targets, 1) + random.sample(self.human_targets, 1)
        models_to_spawn.extend(random.sample(self.noise, 2))
        random.shuffle(models_to_spawn)

        target_positions = []
        
        for i, model_path in enumerate(models_to_spawn):
            target_pos = None
            while target_pos is None or any(np.linalg.norm(target_pos - p) < 2 * self.target_radius for p in target_positions):
                target_pos = random_point_in_pca_rect(dropzone_local)
            
            target_positions.append(target_pos)
            model_name = f"target_{i}"
            
            self._spawn_single_model(model_path, model_name, target_pos[0], target_pos[1])
            self.active_targets.append(model_name)

        return target_positions