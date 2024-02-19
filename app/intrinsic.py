from multical.io.export_calib import export_single
from multical.camera import calibrate_cameras
from multical.workspace import detect_boards_cached
from os import path
import pathlib
from multical.config.runtime import find_board_config, find_camera_images
from multical.image.detect import common_image_size
from multical.io.logging import setup_logging
from multical.io.logging import info

from structs.struct import  map_list, pformat_struct, split_dict
from multical import image

from structs.numpy import struct, shape

from multical.config.arguments import *

@dataclass
class Intrinsic:
  """Run separate intrinsic calibration for set of cameras"""
  paths     : PathOpts = PathOpts(name="intrinsic")
  camera    : CameraOpts = CameraOpts()
  runtime   : RuntimeOpts = RuntimeOpts()

  def execute(self):
      calibrate_intrinsic(self)


def setup_paths(paths):
  output_path = paths.image_path or paths.output_path 
  temp_folder = pathlib.Path(output_path).joinpath("." + paths.name)
  temp_folder.mkdir(exist_ok=True, parents=True)

  return struct(
    output = output_path,
    temp=str(temp_folder),

    calibration_file=path.join(output_path, f"{paths.name}.json"),
    log_file=str(temp_folder.joinpath("log.txt")),
    detections=str(temp_folder.joinpath("detections.pkl"))
  )


def calibrate_intrinsic(args):
    paths=setup_paths(args.paths)

    setup_logging(args.runtime.log_level, [], log_file=paths.log_file)
    info(pformat_struct(args)) 

    image_path = os.path.expanduser(args.paths.image_path)
    info(f"Finding images in {image_path}")

    camera_images = find_camera_images(image_path, 
      args.paths.cameras, args.paths.camera_pattern, matching=False)

    image_counts = {k:len(files) for k, files in zip(camera_images.cameras, camera_images.filenames)}
    info("Found camera directories with images {}".format(image_counts))

    board_names, boards = split_dict(find_board_config(image_path, args.paths.boards))

    info("Loading images..")
    images = image.detect.load_images(camera_images.filenames,  
      prefix=camera_images.image_path, j=args.runtime.num_threads)
    image_sizes = map_list(common_image_size, images)


    info({k:image_size for k, image_size in zip(camera_images.cameras, image_sizes)})
    cache_key = struct(boards=boards, image_sizes=image_sizes, filenames=camera_images.filenames)

    detected_points = detect_boards_cached(boards, images, 
        paths.detections, cache_key, j=args.runtime.num_threads)

    cameras, errs = calibrate_cameras(boards, detected_points, image_sizes,  
      model=args.camera.distortion_model, fix_aspect= args.camera.fix_aspect, max_images= args.camera.limit_intrinsic)
     
    for name, camera, err in zip(camera_images.cameras, cameras, errs):
        info(f"Calibrated {name}, with RMS={err:.2f}")
        info(camera)
        info("")

    info(f"Writing single calibrations to {paths.calibration_file}")
    export_single(paths.calibration_file, cameras, camera_images.cameras, camera_images.filenames)


if __name__ == '__main__':
  run_with(Intrinsic)


""" 
Imports:

export_single: Function to export the calibration results for a single camera.
calibrate_cameras: Function to perform camera calibration.
detect_boards_cached: Function to detect calibration boards in images.
pathlib: Module providing object-oriented filesystem paths.
find_board_config, find_camera_images: Functions to find configuration files for calibration boards and camera images.
common_image_size: Function to determine the common size of images.
setup_logging, info: Functions for logging information about the calibration process.
map_list, pformat_struct, split_dict: Utilities for working with structured data.
image: Module related to image processing.
struct, shape: Utilities for structured data.
PathOpts, CameraOpts, RuntimeOpts: Dataclasses defining options for paths, camera settings, and runtime parameters.
run_with: Function to run the intrinsic calibration.
Intrinsic Class:

Decorated with @dataclass, this class represents the intrinsic calibration process.
Attributes:
paths: Configuration options for file paths related to the calibration.
camera: Configuration options for the camera parameters.
runtime: Configuration options for runtime parameters.
Method:
execute(self): Method to execute the intrinsic calibration process. It calls the calibrate_intrinsic() function, passing itself as an argument.
Setup Paths Function:

setup_paths(paths): Function to set up paths for the calibration process. It creates temporary folders and defines file paths for calibration output, logs, and detections.
Calibrate Intrinsic Function:

calibrate_intrinsic(args): Function to perform intrinsic camera calibration.
It sets up logging for the calibration process.
It finds camera images and board configurations based on the specified paths.
It loads images and determines their sizes.
It detects calibration points on the boards in the images.
It calibrates the cameras using the detected points.
It exports the calibration results to a file.
Main Block:

If the script is executed as the main program, it runs the intrinsic calibration process by creating an instance of the Intrinsic class and calling its execute() method.
"""