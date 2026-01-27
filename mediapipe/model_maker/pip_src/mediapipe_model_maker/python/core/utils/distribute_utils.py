# Copyright 2026 The MediaPipe Authors.
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
"""Minimal distribution strategy helpers to avoid tf-models-official."""

from __future__ import annotations

import tensorflow as tf


def get_distribution_strategy(
    distribution_strategy: str,
    num_gpus: int = 0,
    tpu_address: str = "",
) -> tf.distribute.Strategy:
  """Returns a tf.distribute.Strategy based on a simple string selector.

  Supported values: 'off', 'one_device', 'mirrored', 'tpu'.
  """
  strategy_key = (distribution_strategy or "off").lower()

  if strategy_key in ("off", "none", ""):
    return tf.distribute.get_strategy()

  if strategy_key == "one_device":
    device = "/gpu:0" if num_gpus and num_gpus > 0 else "/cpu:0"
    return tf.distribute.OneDeviceStrategy(device)

  if strategy_key == "mirrored":
    if num_gpus and num_gpus > 0:
      devices = [f"/gpu:{i}" for i in range(num_gpus)]
      return tf.distribute.MirroredStrategy(devices=devices)
    return tf.distribute.MirroredStrategy()

  if strategy_key == "tpu":
    resolver = tf.distribute.cluster_resolver.TPUClusterResolver(
        tpu_address or None
    )
    tf.config.experimental_connect_to_cluster(resolver)
    tf.tpu.experimental.initialize_tpu_system(resolver)
    return tf.distribute.TPUStrategy(resolver)

  raise ValueError(
      "Unsupported distribution_strategy. Supported values are "
      "'off', 'one_device', 'mirrored', and 'tpu'."
  )
