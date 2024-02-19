from apriltags_eth import make_default_detector
from collections import namedtuple

DetectionResult = namedtuple(
    'DetectionResult', ['success', 'image_points', 'target_points', 'ids'])


class AprilGridDetector(object):
  """
  https://github.com/safijari/apriltags2_ethz/blob/master/aprilgrid/__init__.py
  Modification to support AprilGrid start_id so that we can use multiple
  board

  Just like the source, this only works with tagCodes36h11 because the python
  binding of make_default_detector() doesn't accept any parameter
  """
  def __init__(self, rows, columns, size, spacing, start_id=0):
    assert size != 0.0
    assert spacing != 0.0
    self.rows = rows
    self.columns = columns
    self.size = size
    self.spacing = spacing
    self.start_id = start_id
    self.detector = make_default_detector()

  def is_detection_valid(self, detection, image):
    d = detection
    h, w = image.shape[0:2]
    for cx, cy in d.corners:
      if cx < 0 or cx > w:
        return False
      if cy < 0 or cy > h:
        return False
    if not d.good:
      return False
    if d.id < self.start_id:
      return False
    if d.id >= self.rows * self.columns + self.start_id:
      return False

    return True

  def get_tag_corners_for_id(self, tag_id):
    # order is lower left, lower right, upper right, upper left
    # Note: tag_id of lower left tag is 0, not 1
    a = self.size
    b = self.spacing * a
    tag_row = (tag_id) // self.columns
    tag_col = (tag_id) % self.columns
    left = bottom = lambda i: i * (a + b)
    right = top = lambda i: (i + 1) * a + (i) * b
    return [(left(tag_col), bottom(tag_row)),
            (right(tag_col), bottom(tag_row)),
            (right(tag_col), top(tag_row)), (left(tag_col), top(tag_row))]

  def compute_observation(self, image):
    # return imagepoints and the coordinates of the corners
    # 1. remove non good tags
    detections = self.detector.extract_tags(image)

    # Duplicate ID search
    ids = {}
    for d in detections:
      if d.id in ids:
        raise Exception("There may be two physical instances of the same tag in the image")
      ids[d] = True

    filtered = [d for d in detections if self.is_detection_valid(d, image)]

    image_points = []
    target_points = []
    ids = []

    filtered.sort(key=lambda x: x.id)

    # TODO: subpix refinement?
    for f in filtered:
      # new id starting from 0 to not break anything else in the codebase
      id = f.id - self.start_id
      target_points.extend(self.get_tag_corners_for_id(id))
      image_points.extend(f.corners)
      ids.extend([id, id, id, id])

    success = True if len(filtered) > 0 else False

    return DetectionResult(success, image_points, target_points, ids)

    """
    The get_tag_corners_for_id method computes the coordinates of the corners of a tag based on its ID. It uses the size and spacing parameters to determine the distance between the corners.
The compute_observation method extracts AprilTags from the image and filters out non-valid detections based on criteria like tag ID and goodness. It then computes the image points (coordinates of the detected corners) and target points (expected coordinates of corners based on the AprilGrid configuration). These points are essential for subsequent calibration steps.
The DetectionResult named tuple encapsulates the result of the detection process, including whether the detection was successful (success), the detected corners in the image (image_points), the expected corners based on the AprilGrid configuration (target_points), and the IDs of the detected tags (ids).

Imports:

make_default_detector from apriltags_eth: Function to create an AprilTags detector with default parameters.
namedtuple from collections: Factory function for creating tuple subclasses with named fields.
Named Tuple:

DetectionResult: Named tuple representing the result of the AprilGrid detection. It contains fields for success (whether the detection was successful), image_points (coordinates of detected corners in the image), target_points (expected coordinates of corners based on the AprilGrid configuration), and ids (IDs of the detected tags).
AprilGridDetector Class:

__init__ method: Initializes the AprilGrid detector with the specified parameters such as rows, columns, size, spacing, and start_id. It also creates an AprilTags detector using make_default_detector().
is_detection_valid method: Checks if a detected tag is valid based on its corners, goodness, ID, and start ID.
get_tag_corners_for_id method: Computes the coordinates of the corners of a tag based on its ID.
compute_observation method: Performs AprilGrid detection on the input image. It first extracts AprilTags using the detector, then filters out non-valid detections, and finally computes the image points (detected corners), target points (expected corners), and tag IDs for valid detections.
"""
