import numpy as np
import time


class MissionScorer:
    def __init__(self, target_radius=5.0):
        self.target_radius = target_radius
        self.run_name = time.strftime("%H-%M-%S")

    def evaluate_drops(self, target_positions_2d, drop_positions_3d):
        """
        Takes the (x, y) list of targets and the (x, y, z) list of drops.
        Calculates hits and saves the final score.
        """
        hit_counts = np.zeros(len(target_positions_2d))

        for drop in drop_positions_3d:
            drop_2d = drop[:2]  # ignore altitude for hit detection
            for i, target in enumerate(target_positions_2d):
                if np.linalg.norm(drop_2d - target) < self.target_radius:
                    hit_counts[i] += 1

        # 100 points for first hit (30+70), 70 for subsequent hits
        score = sum(min(x, 1) * 30 + 70 * x for x in hit_counts)

        print(f"--- Mission Complete ---")
        print(f"Hits per target: {hit_counts}")
        print(f"Total Score: {score}")

        with open(f"mission_score_{self.run_name}.txt", "w+") as f:
            f.write(f"Hit Counts: {list(hit_counts)}\n")
            f.write(f"Final Score: {score}\n")

        return score
