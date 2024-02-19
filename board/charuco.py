from multical.board.board import Board
from pprint import pformat
from cached_property import cached_property
import cv2
import numpy as np
from .common import *

from structs.struct import struct, choose, subset
from multical.optimization.parameters import Parameters

class CharucoBoard(Parameters, Board):
  def __init__(self, size, square_length, marker_length, min_rows=3, min_points=20, 
    adjusted_points=None, aruco_params=None, aruco_dict='4X4_100', aruco_offset=0):
    
    self.aruco_dict = aruco_dict
    self.aruco_offset = aruco_offset 

    self.size = tuple(size)

    self.marker_length = marker_length
    self.square_length = square_length

    self.adjusted_points = choose(adjusted_points, self.points) 
 
    self.aruco_params = aruco_params or {}
    self.min_rows = min_rows
    self.min_points = min_points


  @cached_property
  def board(self):
    aruco_dict = create_dict(self.aruco_dict, self.aruco_offset)
    width, height = self.size
    return cv2.aruco.CharucoBoard_create(width, height,
      self.square_length, self.marker_length, aruco_dict)

  @cached_property
  def aruco_config(self):
    return aruco_config(self.aruco_params)  

  def export(self):
    return struct(
      type='charuco',
      aruco_dict=self.aruco_dict,
      aruco_offset=self.aruco_offset,
      size = self.size,
      num_ids = len(self.board.ids),
      marker_length = self.marker_length,
      square_length = self.square_length,
      aruco_params = self.aruco_params
    )

  def __eq__(self, other):
    return self.export() == other.export()

  @property
  def points(self):
    return self.board.chessboardCorners
  
  @property
  def num_points(self):
    return len(self.points)

  @property 
  def ids(self):
    return np.arange(self.num_points)

  @cached_property
  def mesh(self):
    return grid_mesh(self.adjusted_points, self.size)

  @property
  def size_mm(self):
    square_length = int(self.square_length * 1000)
    return [dim * square_length for dim in self.size]


  def draw(self, pixels_mm=1, margin=20):
    square_length = int(self.square_length * 1000 * pixels_mm)

    image_size = [dim * square_length for dim in self.size]
    return self.board.draw(tuple(image_size), marginSize=margin)


  def __str__(self):
      d = self.export()
      return "CharucoBoard " + pformat(d)

  def __repr__(self):
      return self.__str__()      


  def detect(self, image):    
    corners, ids, _ = cv2.aruco.detectMarkers(image, 
      self.board.dictionary, parameters=aruco_config(self.aruco_params))     
    if ids is None: return empty_detection

    _, corners, ids = cv2.aruco.interpolateCornersCharuco(
        corners, ids, image, self.board)
    
    if ids is None: return empty_detection
    return struct(corners = corners.squeeze(1), ids = ids.squeeze(1))

  def has_min_detections(self, detections):
    return has_min_detections_grid(self.size, detections.ids, 
      min_points=self.min_points, min_rows=self.min_rows)

  def estimate_pose_points(self, camera, detections):
    return estimate_pose_points(self, camera, detections)


  @cached_property
  def params(self):
    return self.adjusted_points

  def with_params(self, params):
    return self.copy(adjusted_points = params)

  def copy(self, **k):
      d = self.__getstate__()
      d.update(k)
      return CharucoBoard(**d)

  def __getstate__(self):
    return subset(self.__dict__, ['size', 'adjusted_points', 'aruco_params', 
      'marker_length', 'square_length', 'min_rows', 'min_points',
      'aruco_dict', 'aruco_offset'
    ])




""" Import Statements:

The necessary modules and classes are imported, including Board from multical.board.board, pformat from pprint, cached_property from cached_property, cv2 from opencv, numpy as np, and functions from the common module.
Class CharucoBoard:

Inherits from Parameters and Board classes.
Initializes with parameters such as board size, square length, marker length, minimum rows, minimum points, adjusted points, ArUco parameters, ArUco dictionary, and ArUco offset.
Cached Properties:

board: Constructs the Charuco board using OpenCV's cv2.aruco.CharucoBoard_create function based on the provided parameters.
aruco_config: Generates ArUco configuration based on the provided ArUco parameters.
Methods:

export: Returns a struct containing information about the Charuco board.
points: Returns the corners of the Charuco board as chessboard corners.
num_points: Returns the number of points (corners) on the Charuco board.
ids: Returns an array of IDs corresponding to the points on the Charuco board.
mesh: Generates a mesh representing the Charuco board grid.
size_mm: Returns the size of the Charuco board in millimeters.
draw: Draws the Charuco board on an image.
detect: Detects Charuco board markers and interpolates corners.
has_min_detections: Checks if the detected Charuco board has the minimum required number of points.
estimate_pose_points: Estimates pose points for camera calibration.
params: Returns the adjusted points.
with_params: Returns a copy of the Charuco board with adjusted points.
copy: Copies the Charuco board with optional parameter updates.
__getstate__: Returns a subset of the Charuco board's attributes for serialization.
String Representation:

__str__ and __repr__ methods provide string representations of the Charuco board.
This class encapsulates the functionality related to Charuco boards, including board creation, parameter extraction, drawing, detection, and more, providing a convenient interface for working with Charuco boards in camera calibration applications."""