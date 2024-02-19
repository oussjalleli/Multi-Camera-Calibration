from os import path
import numpy as np

from multical.workspace import Workspace

from multical.io.logging import error
from multical.io.logging import setup_logging

from multical.config.arguments import *


@dataclass
class Vis:
    workspace_file : str 

    def execute(self):
      visualize(self)


def fix_qt():
  # work around Qt in OpenCV 
  for k, v in os.environ.items():
      if k.startswith("QT_") and "cv2" in v:
          del os.environ[k]


def visualize_ws(ws):
    try:
      fix_qt()
      
      from multical.interface import visualizer
      visualizer.visualize(ws)

    except ImportError as err:     
      error(err)
      error("qtpy and pyvista are necessary to run the visualizer, install with 'pip install qtpy pyvista-qt'")


def visualize(args): 
    np.set_printoptions(precision=4, suppress=True)

    filename = args.workspace_file
    if path.isdir(filename):
      filename = path.join(filename, "calibration.pkl")
      
    ws = Workspace.load(filename)
    setup_logging('INFO', [ws.log_handler])
    ws._load_images()

    visualize_ws(ws)

if __name__ == '__main__':
    run_with(Vis)


""" 
Imports:

path from os: Module for manipulating file paths.
numpy as np: NumPy library for numerical computations.
Workspace from multical.workspace: Class representing a workspace for storing calibration data.
error and setup_logging from multical.io.logging: Functions for logging errors and setting up logging configurations.
run_with from multical.config.arguments: Function for running a command with specific arguments.
Dataclass:

Vis: A dataclass representing the visualization command.
Attributes:
workspace_file: Path to the workspace file containing calibration data.
Helper Functions:

fix_qt(): A function to work around Qt issues in OpenCV by removing certain environment variables related to Qt.
visualize_ws(ws): A function to visualize the workspace using the multical.interface.visualizer module. It first tries to fix any Qt-related issues and then proceeds to visualize the workspace. If importing necessary modules fails, it logs an error.
visualize(args): A function to load the workspace file specified in the arguments, set up logging configurations, load images into the workspace, and then visualize the workspace using visualize_ws(ws).
Main Block:

If the script is executed as the main program (__name__ == '__main__'), it runs the visualization command (Vis) using the run_with function, which executes the execute() method of the Vis class.
"""