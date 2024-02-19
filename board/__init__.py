from dataclasses import dataclass
from os import path
from .charuco import CharucoBoard
from .aprilgrid import AprilGrid
from .calico_config import load_calico


from typing import Tuple

from omegaconf.omegaconf import OmegaConf, MISSING
from structs.struct import struct

from multical.io.logging import debug, info, error

@dataclass 
class CharucoConfig:
  _type_: str = "charuco"
  size : Tuple[int, int] = MISSING

  square_length : float = MISSING
  marker_length : float = MISSING
  
  aruco_dict : str = MISSING
  aruco_offset : int = 0
  min_rows : int = 3
  min_points : int = 10



@dataclass 
class AprilConfig:
  _type_: str = "aprilgrid"
  size : Tuple[int, int] = MISSING

  start_id   : int = 0
  tag_family : str = "t36h11"
  tag_length : float = 0.06
  tag_spacing: float = 0.3

  min_rows : int = 2
  min_points : int = 12


@dataclass 
class CheckerboardConfig:
  _type_: str = "checkerboard"
  size : Tuple[int, int] = MISSING
  square_length : float = MISSING



def merge_schema(config, schema):
    merged = OmegaConf.merge(schema, config)
    return struct(**merged)._without('_type_')



def load_config(yaml_file):
  config = OmegaConf.load(yaml_file)
  aruco_params = config.get('aruco_params', {})
  
  boards = {k:OmegaConf.merge(config.common, board) for k, board in config.boards.items()} if 'common' in config\
    else config.boards

  def instantiate_board(config):
    if config._type_ == "charuco":
      schema = OmegaConf.structured(CharucoConfig)
      return CharucoBoard(aruco_params=aruco_params, **merge_schema(config, schema))
    elif config._type_ == "aprilgrid":
      schema = OmegaConf.structured(AprilConfig)
      return AprilGrid(**merge_schema(config, schema))
    else:
      assert False, f"unknown board type: {config._type_}, options are (charuco | aprilgrid | checkerboard)"

  return {k:instantiate_board(board) for k, board in boards.items()}


""" 
Imports:

dataclass: Decorator for declaring data classes.
path from os: Module for manipulating file paths.
CharucoBoard and AprilGrid from .charuco and .aprilgrid modules respectively: Classes representing Charuco and AprilGrid calibration boards.
load_calico from .calico_config: Function for loading Calico configurations.
Tuple from typing: Type hint for a tuple.
OmegaConf and MISSING from omegaconf.omegaconf: Classes for handling hierarchical configurations and representing missing values.
struct from structs.struct: Function for creating struct-like objects.
debug, info, error from multical.io.logging: Functions for logging debug, info, and error messages.
Dataclasses:

CharucoConfig: Dataclass representing configuration parameters for Charuco boards.
AprilConfig: Dataclass representing configuration parameters for AprilGrid boards.
CheckerboardConfig: Dataclass representing configuration parameters for Checkerboard boards.
Helper Functions:

merge_schema(config, schema): Function for merging the provided configuration with the schema, creating a new struct without the _type_ attribute.
load_config Function:

This function takes a YAML file path as input and loads the board configurations from the YAML file.
It loads the YAML file using OmegaConf.
If the YAML file contains common configurations, it merges them with individual board configurations.
It defines an instantiate_board function to create board objects based on their types specified in the configurations.
It returns a dictionary of instantiated board objects.
"""