from dataclasses import dataclass
from multical.config.arguments import run_with
from multiprocessing import cpu_count
from typing import  Union


from multical.app.boards import Boards
from multical.app.calibrate import Calibrate
from multical.app.intrinsic import Intrinsic
from multical.app.vis import Vis


@dataclass
class Multical:
  """multical - multi camera calibration 
  - calibrate: multi-camera calibration
  - intrinsic: calibrate separate intrinsic parameters
  - boards: generate/visualize board images, test detections
  - vis: visualize results of a calibration 
  """ 
  command : Union[Calibrate, Intrinsic, Boards, Vis]
   
  def execute(self):
    return self.command.execute()


def cli():
  run_with(Multical)

if __name__ == '__main__':
  cli()

"""
Imports:

dataclass: Decorator to simplify the creation of classes that mainly store data.
run_with: Function to run a command with specific arguments.
cpu_count: Function to get the number of available CPU cores.
Union: Type hint for specifying that an object can be of multiple types.
Commands from different modules:
Boards: Command for generating/visualizing board images and testing detections.
Calibrate: Command for multi-camera calibration.
Intrinsic: Command for calibrating separate intrinsic parameters.
Vis: Command for visualizing results of a calibration.
Multical Class:

Decorated with @dataclass, this class represents the multi-camera calibration application.
Attributes:
command: An attribute that holds the command to execute, which can be one of Calibrate, Intrinsic, Boards, or Vis.
Method:
execute(self): Method to execute the specified command.
CLI Function:

cli(): Command-line interface function.
It creates an instance of the Multical class and runs it using the run_with() function.
Main Block:

If the script is executed as the main program, it calls the cli() function, starting the command-line interface for the multi-camera calibration application. 
"""