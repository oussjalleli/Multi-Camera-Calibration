
from multical.io.logging import setup_logging
from .vis import visualize_ws

from structs.struct import struct, map_none, to_structs
import numpy as np

from multical.config import *
from dataclasses import dataclass

@dataclass
class Calibrate:
    """Run camera calibration"""
    paths  : PathOpts 
    camera  : CameraOpts
    runtime    : RuntimeOpts
    optimizer  : OptimizerOpts 
    vis : bool = False        # Visualize result after calibration

    def execute(self):
        calibrate(self)


def calibrate(args): 
  np.set_printoptions(precision=4, suppress=True)

  # Use image path if not explicity specified
  output_path = args.paths.image_path or args.paths.output_path 

  ws = workspace.Workspace(output_path, args.paths.name)
  setup_logging(args.runtime.log_level, [ws.log_handler], log_file=path.join(output_path, f"{args.paths.name}.txt"))

  boards = find_board_config(args.paths.image_path, board_file=args.paths.boards)
  camera_images = find_camera_images(args.paths.image_path, 
    args.paths.cameras, args.paths.camera_pattern, limit=args.paths.limit_images)

  initialise_with_images(ws, boards, camera_images, args.camera, args.runtime)
  optimize(ws, args.optimizer)

  ws.export()
  ws.dump()

  if args.vis:
    visualize_ws(ws)



if __name__ == '__main__':
  run_with(Calibrate)


""" Imports:

setup_logging: Function to set up logging for the calibration process.
visualize_ws from .vis: Function to visualize the calibration results.
struct, map_none, to_structs from structs.struct: Utilities for working with structured data.
numpy as np: Numerical computing library.
Various modules from multical.config: Configuration settings for the calibration process.
dataclass from dataclasses: Decorator to automatically generate special methods for a class.


Calibrate Class:

Decorated with @dataclass, this class represents the calibration process.
Attributes:
paths: Configuration options for file paths related to the calibration.
camera: Configuration options for the camera parameters.
runtime: Configuration options for runtime parameters.
optimizer: Configuration options for optimization parameters.
vis: Boolean flag indicating whether to visualize the calibration results.
Method:
execute(self): Method to execute the calibration process. It calls the calibrate() function, passing itself as an argument.

Calibrate Function:

This function performs the actual calibration process.
It sets up logging for the process.
It initializes a workspace (ws) with the output path and name specified in the configuration.
It loads board configurations and camera images based on the specified paths.
It initializes the workspace with the loaded configurations and images.
It optimizes the calibration parameters using the specified optimizer.
It exports the calibration results and dumps them into a file.
If the visualization flag (vis) is set to True, it visualizes the calibration results using the visualize_ws function.
Main Block:

If the script is executed as the main program, it runs the calibration process by creating an instance of the Calibrate class and calling its execute() method. """
