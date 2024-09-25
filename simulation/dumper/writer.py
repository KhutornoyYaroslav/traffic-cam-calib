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
    # max_subfolder_index = 9999 # max count of subfolders with frames
    # max_subfolder_items_count = 10000 # max count of frames in one subfolder
    dump_frames_dir = "frames" # _suffix
    frame_filename_template = "frame_%08d.json"

    def __init__(self, overwrite: bool = True):
        self._frames_path = None
        self._overwrite = overwrite

    def create_output_dir(self, root: str) -> bool:
        """
        Example:
            root = /home/dumps/sim1
        """
        # root = os.path.dirname(os.path.abspath(filepath))
        # basename, ext = os.path.splitext(os.path.basename(filepath))
        # if ext != ".json":
        #     print("Bad file extension. Must be .json")
        # print(root, basename, ext)

        if os.path.isdir(root) and not self._overwrite:
            print('Failed to create output dir. Already exists.')
            return False

        frames_dir = os.path.join(root, self.dump_frames_dir)
        shutil.rmtree(frames_dir, ignore_errors=True)
        os.makedirs(frames_dir, exist_ok=True)
        self._frames_path = frames_dir

    def write_frame_data(self,
                         frame_idx: int,
                         frame_size: Tuple[int, int],
                         car_keypoints: List[Dict[str, ArrayLike]],
                         car_brects: List[Tuple[int, int, int, int]],
                         car_masks: List[ArrayLike]):
        if self._frames_path is None:
            print("Failed to write frame dump. Output directory was not created.")
            return

        assert len(car_keypoints) == len(car_brects) == len(car_masks)
        
        json_data = {}
        json_data["id"] = frame_idx
        json_data["framesize"] = list(frame_size)
        json_data["keypoints"] = []
        json_data["carmasks"] = []
        json_data["cars"] = []

        for points, brect, mask in zip(car_keypoints, car_brects, car_masks):
            if not len(points) or (brect is None) or (mask is None):
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
                "rect": brect,
                "mask": mask_base64_str,
                "keypoints": json_keypoints
            }
            json_data["cars"].append(json_car)


        filepath = os.path.join(self._frames_path, self.frame_filename_template % frame_idx)
        with open(filepath, 'w') as f:
            json.dump(json_data, f) # , indent=2)
