
import pathlib
from typing import Optional

import cv2
import numpy as np
from simple_parsing import choice

from multical.display import show_detections
from multical import board
from multical.image.display import display, display_stacked

import argparse
from os import path

from multical.image.detect import load_image
from multical.config import *


standard_sizes = dict(
  A4 = (210, 297),
  A3 = (297, 420),
  A2 = (420, 594),
  A1 = (594, 841),
  A0 = (841, 1189)
)


@dataclass 
class Boards:
  """ Generate boards and show/detect for configuration file """

  boards : str # Configuration file (YAML) for calibration boards
  
  detect : Optional[str] = None # Show detections from an example image
  write : Optional[str] = None # Directory to write board images

  pixels_mm : int = 1   # Pixels per mm of pattern
  margin_mm : int = 20  # Border width in mm

  paper_size_mm : Optional[str] = None # Paper size in mm WxH 
  paper_size : Optional[str] = choice(*standard_sizes.keys(), default=None)

  def execute(self):
    show_boards(self)



def show_boards(args):
  boards = board.load_config(args.boards)

  print("Using boards:")
  for name, b in boards.items():
    print(f"{name} {b}")

  assert args.paper_size_mm is None or args.paper_size is None, "specify --paper_size_mm or --paper_size (not both)"

  paper_size_mm = None
  if args.paper_size is not None:
    paper_size_mm = standard_sizes[args.paper_size]

  elif args.paper_size_mm is not None:
    paper_size_mm = [int(x) for x in args.paper_size_mm.split('x')]   
    assert len(paper_size_mm) == 2, f"expected WxH paper_size_mm e.g. 420x594 or name, one of {list(standard_sizes.keys())}"

  if paper_size_mm is not None:
    args.margin = 0

  def draw_board(board):
    board_image = board.draw(args.pixels_mm, args.margin_mm)
    board_size = board.size_mm

    if paper_size_mm is not None:
      w, h = paper_size_mm[0] * args.pixels_mm, paper_size_mm[1] * args.pixels_mm

      image = np.full((h, w), 255, dtype=np.uint8)
      dy, dx = [(a - b) // 2  for a, b in zip(image.shape, board_image.shape)]

      assert dx >= 0 and dy >= 0,\
        f"--paper_size ({paper_size_mm[0]}x{paper_size_mm[1]}mm) must be larger than board size ({board_size[0]}x{board_size[1]}mm)"

      image[dy:dy+board_image.shape[0], dx:dx + board_image.shape[1]] = board_image
      return image

    return board_image    

  images = {k:draw_board(board) for k, board in boards.items()}

  if args.detect is not None:
    image = load_image(args.detect)
    detections = [board.detect(image) for board in boards.values()]

    for k, d in zip(boards.keys(), detections):
      print(f"Board {k}: detected {d.ids.size} points")

    image = show_detections(image, detections, radius=10)
    display(image)

  elif args.write is not None:
    pathlib.Path(args.write).mkdir(parents=True, exist_ok=True)
    for k, board_image in images.items():
      filename = path.join(args.write, k + ".png")
      cv2.imwrite(filename, board_image)
      print(f"Wrote {filename}")
  else:
    display_stacked(list(images.values()))




if __name__ == '__main__':
    run_with(Boards)




""" 
--Imports:

-pathlib: Library for working with file paths.
-cv2: OpenCV library for computer vision tasks.
-numpy as np: Library for numerical computing in Python.
-choice from simple_parsing: Function for defining choices in command-line arguments.
Various modules from multical package: display, board, image.display, image.detect, and config.
Standard Sizes:

A dictionary standard_sizes containing standard paper sizes and their dimensions in millimeters.
--Boards Class:

A dataclass named Boards is defined, representing the configuration and functionalities related to calibration boards.
Attributes:
-boards: Configuration file (YAML) for calibration boards.
-detect: Optional parameter to specify an image for board detection.
-write: Optional directory to write board images.
-pixels_mm: Pixels per millimeter of the pattern.
-margin_mm: Border width in millimeters.
-paper_size_mm: Optional paper size in millimeters (WxH).
-paper_size: Optional choice of paper size, chosen from the keys of standard_sizes.
--Methods:
-execute(): Executes the process of showing and detecting calibration boards based on the provided arguments.
--Show Boards Function:

The show_boards() function is defined, responsible for displaying and detecting calibration boards.
It loads board configurations, prints them, and validates paper size arguments.
It draws each board, adjusting for paper size if specified.
If the detect argument is provided, it detects boards in the specified image.
If the write argument is provided, it writes board images to the specified directory.
Otherwise, it displays the drawn board images. 



general guideline on how you can create your own board:

Define the Pattern:

Decide on the pattern you want to use for your calibration board. It could be a grid of dots, circles, or any other distinct features that can be easily detected.
Design the pattern using image editing software like Adobe Photoshop or use existing patterns available online.
Create a Configuration File:

Create a YAML configuration file that describes the layout and characteristics of your calibration board. This file should specify the dimensions, spacing, and arrangement of the pattern.
You can define multiple boards with different configurations in the same file if needed.
Implement Drawing Function:

Write a function to draw the pattern based on the specifications provided in the configuration file.
Ensure that the function can adjust the size and layout of the pattern according to the desired paper size and margin.
Optional: Implement Detection Function:

If you want to perform automatic detection of the calibration board in images, you may need to implement a detection function.
This function should use computer vision techniques to locate the pattern within an image.
Testing and Validation:

Test your calibration board by drawing it on paper or generating images using the drawing function.
Validate the board by performing detection on sample images to ensure accurate detection and localization of the pattern.
Integration:

Integrate your custom calibration board into your multicamera calibration project by modifying the existing code to use your board's configuration file and drawing function. """

