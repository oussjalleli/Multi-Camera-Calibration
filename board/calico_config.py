from os import path
from .charuco import CharucoBoard
from multical.io.logging import error


def read_pairs(filename):
  values = []
  with open(filename, 'rt') as file:
    for line in file:
      if len(line.strip()) > 0:
        line = [item.strip() for item in line.split()]
        assert len(line) == 2, f"expected form: key value on line {line}"

        values.append(line)
  return values


def take_keys(pairs, keys, dtype=int):
  values = []
  for expected in keys:
    k, v = pairs.pop(0)
    if k != expected:
      raise SyntaxError(f"expected {expected}, got {k}")
    values.append(dtype(v))

  return values


def load_mm_file(network_file, i):
  pairs = read_pairs(path.join(path.dirname(
      network_file), f"pattern_square_mm{i}.txt"))
  square_length, = take_keys(pairs, ["squareLength_mm"], dtype=float)
  return square_length


def load_calico(network_file):
  pairs = read_pairs(network_file)
  boards = {}
  offset = 0

  try:
    dict_id, number_boards = take_keys(pairs, ["aruco_dict", "number_boards"])
    for i in range(number_boards):

      fields = ["squaresX", "squaresY", "squareLength", "markerLength"]
      w, h, square_length_px, marker_length_px = take_keys(pairs, fields)
      square_length = load_mm_file(network_file, i)
      marker_length = square_length * (marker_length_px / square_length_px)

      board = CharucoBoard((w, h), square_length, marker_length,
                           aruco_dict=dict_id, aruco_offset=offset)

      boards[f"board{i}"] = board
      offset += len(board.board.ids)

  except (SyntaxError, IOError) as e:
    error(f"Failed to load calico network file {network_file}")
    error(e)

  return boards


"""
Import Statements:

The os.path module is imported to work with file paths.
The CharucoBoard class is imported from the charuco module.
The error function is imported from multical.io.logging module.
Function read_pairs(filename):

This function reads key-value pairs from a text file.
It opens the file specified by filename and iterates through each line.
Each line is split into key-value pairs and added to the values list.
The function returns the list of key-value pairs.
Function take_keys(pairs, keys, dtype=int):

This function extracts values associated with specific keys from a list of key-value pairs.
It iterates through the list of keys and extracts corresponding values from the pairs.
It checks if the extracted key matches the expected key and converts the value to the specified data type (dtype).
The function returns a list of extracted values.
Function load_mm_file(network_file, i):

This function loads the square length from a specific file related to the calibration network.
It constructs the file path using the network file's directory and a filename pattern.
It reads the key-value pairs from the file and extracts the square length value.
The square length value is returned.
Function load_calico(network_file):

This function loads calibration boards from a calibration network file.
It reads key-value pairs from the network file and extracts information for each calibration board.
It loops through the number of boards specified in the file and extracts parameters such as the number of squares, square length, and marker length.
For each board, it calculates the marker length in millimeters using a reference file.
It constructs a CharucoBoard object for each board using the extracted parameters and adds it to the boards dictionary.
If any errors occur during parsing, it logs an error message.
"""