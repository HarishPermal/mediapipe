# Copyright 2023 The MediaPipe Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Custom Detection export module for Object Detection."""

from typing import Any, Mapping

try:
  from official.vision.serving import detection
except ImportError as exc:
  detection = None
  _TF_MODELS_IMPORT_ERROR = exc


class DetectionModule(detection.DetectionModule):
  """A serving detection module for exporting the model.

  This module overrides the tensorflow_models DetectionModule by only outputting
    the pre-nms detection_boxes and detection_scores.
  """

  def serve(self, images) -> Mapping[str, Any]:
    if detection is None:
      raise ImportError(
          "tensorflow-models is required for object detection serving. Install "
          "with `pip install mediapipe-model-maker[garden]` or "
          "`pip install mediapipe-model-maker[garden-no-deps]`."
      ) from _TF_MODELS_IMPORT_ERROR
    result = super().serve(images)
    final_outputs = {
        'detection_boxes': result['detection_boxes'],
        'detection_scores': result['detection_scores'],
    }
    return final_outputs
