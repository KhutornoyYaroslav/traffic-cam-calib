import os
import json
import shutil
import base64
import cv2 as cv
from numpy.typing import ArrayLike
from typing import List, Dict, Tuple


EXPORT_LABELS_ORDER = [
    "fl wheel",
    "bl wheel",
    "br wheel",
    "fr wheel",
    "windshield tr",
    "windshield tl",
    "windshield bl",
    "windshield br",
    "rear window tl",
    "rear window tr",
    "rear window br",
    "rear window bl",
    "rearview mirror l",
    "rearview mirror r",
    "bottom of license fr",
    "bottom of license fl",
    "bottom of license bl",
    "bottom of license br",
    "headlight fr inner bottom",
    "headlight fr outer top",
    "headlight fl inner bottom",
    "headlight fl outer top",
    "headlight bl inner bottom",
    "headlight bl outer top",
    "headlight br inner bottom",
    "headlight br outer top",
    "bottom bumper fl",
    "bottom bumper bl",
    "bottom bumper br",
    "bottom bumper fr",
    "side window back l",
    "side window back r",
]

class DumpWriter():
    dump_frames_dir = "frames"
    frame_filename_template = "frame_%08d.json"

    def __init__(self, overwrite: bool = True):
        self._root_path = None
        self._frames_path = None
        self._overwrite = overwrite

    def init(self, output_root: str) -> bool:
        """
        Example:
            output_root = /home/dumps/sim1
        """
        if os.path.isdir(output_root) and not self._overwrite:
            print('Failed to create output dir. Already exists.')
            return False

        frames_dir = os.path.join(output_root, self.dump_frames_dir)
        shutil.rmtree(frames_dir, ignore_errors=True)
        os.makedirs(frames_dir, exist_ok=True)

        self._root_path = output_root
        self._frames_path = frames_dir

        return True
    
    def copy_config(self, simulation_cfg_path: str) -> bool:
        if self._root_path is None:
            print("Failed to copy config. Output directory was not created.")
            return False
        
        if not os.path.isfile(simulation_cfg_path):
            print(f"Failed to copy config. Simulation config doesn't exist: {simulation_cfg_path}")
            return False
        
        # copy simulation config
        filename = os.path.basename(simulation_cfg_path)
        shutil.copyfile(simulation_cfg_path, os.path.join(self._root_path, filename))

        # copy scene config
        scene_config_path = ""
        with open(simulation_cfg_path, 'r') as f:
            data = json.load(f)
            scene_config_path = data.get("scene_config_path", scene_config_path)

        if os.path.isfile(scene_config_path):
            filename = os.path.basename(scene_config_path)
            shutil.copyfile(scene_config_path, os.path.join(self._root_path, filename))

        return True

    def write_frame_data(self,
                         frame_idx: int,
                         frame_size: Tuple[int, int],
                         car_keypoints: List[Dict[str, ArrayLike]],
                         car_brects: List[Tuple[int, int, int, int]],
                         car_masks: List[ArrayLike],
                         car_model_names: List[str]) -> bool:
        if self._frames_path is None:
            print("Failed to write frame dump. Output directory was not created.")
            return False

        assert len(car_keypoints) == len(car_brects) == len(car_masks) == len(car_model_names)
        
        json_data = {}
        json_data["id"] = frame_idx
        json_data["framesize"] = list(frame_size)
        json_data["keypoints"] = []
        json_data["carmasks"] = []
        json_data["cars"] = []

        for points, brect, mask, model_name in zip(car_keypoints, car_brects, car_masks, car_model_names):
            if not len(points) or (brect is None) or (mask is None) or (model_name is None):
                continue

            # keypoints
            json_keypoints = []
            for label, point in points.items():
                label_idx = EXPORT_LABELS_ORDER.index(label)
                json_point = {
                    "klass": label_idx,
                    "point": point.tolist()
                }
                json_keypoints.append(json_point)
            json_data["keypoints"].extend(json_keypoints)

            # create base64 png mask
            success, mask_encoded = cv.imencode(".png", mask)
            if not success:
                print("Failed to encode mask (.png)")
                continue
            mask_base64 = base64.b64encode(mask_encoded)
            mask_base64_str = str(mask_base64)[2:-1]

            # carmasks
            json_carmask = {
                "klass": 3,
                "name": "car",
                "score": 1.0,
                "rect": brect,
                "mask": mask_base64_str
            }
            json_data["carmasks"].append(json_carmask)

            # cars
            json_car = {
                "carmask": json_carmask,
                "keypoints": json_keypoints,
                "model_name": model_name
            }
            json_data["cars"].append(json_car)


        filepath = os.path.join(self._frames_path, self.frame_filename_template % frame_idx)
        with open(filepath, 'w') as f:
            json.dump(json_data, f)

        return True
