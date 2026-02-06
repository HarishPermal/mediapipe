# README2 — Delta Summary (master → harish_model_maker2)

This document summarizes the **functional source changes** made on top of
`master` to support newer Python/TF/Keras environments, reduce dependency
conflicts, and make Model Maker usable without `mediapipe.tasks.cc` native
bindings (while still allowing optional metadata export when available).

> Note: The working tree also contains **generated artifacts** (e.g., `build/`,
> `pip_src/`, `dist/*.whl`, `wheelhouse/*.whl`, `.egg-info`, `.pyc`). These are
> **not** source changes and should be excluded from the PR.

---

## 1) MediaPipe import robustness (no `tasks.cc` required)

### `mediapipe/__init__.py`
- Made imports **safe and optional**.
- Tasks and solutions imports are now guarded; failures emit warnings instead
  of crashing the import.

Why:
- Newer pip wheels do not ship `mediapipe.tasks.cc`. The previous eager imports
  caused immediate `ImportError` on import.

### `mediapipe/tasks/python/__init__.py`
- Reworked into **safe, lazy imports** with warning on failure.
- `BaseOptions` only set if `core` loads.

Why:
- Avoid failures in unrelated modules (e.g., audio) blocking import of text or
  vision tasks.

### `mediapipe/tasks/python/metadata/metadata.py`
- Guarded `_pywrap_metadata_version` import and raise a **clear RuntimeError**
  only when metadata population is invoked.

Why:
- `mediapipe.tasks.cc` is absent in the public wheel, so metadata export must
  degrade gracefully.

---

## 2) Build and packaging fixes (MediaPipe wheel)

### `mediapipe/setup.py`
- Reads version from `mediapipe/version.bzl` (instead of `dev`).
- Avoids appending extra imports to `mediapipe/__init__.py` during build.

Why:
- Prevents the wheel from reintroducing the old eager import behavior and fixes
  invalid version errors during build.

---

## 3) Model Maker: Keras 3 / TF 2.20 compatibility

### `mediapipe/model_maker/python/core/utils/model_util.py`
- Replaced removed `ModelCheckpoint(period=...)` with a Keras 3–compatible
  implementation and proper `.weights.h5` naming.
- Added a lightweight periodic checkpoint callback when frequency > 1.

Why:
- Keras 3 removed `period` and requires `.weights.h5` when
  `save_weights_only=True`.

### TF Hub + Keras mode alignment
- `mediapipe/model_maker/python/vision/image_classifier/image_classifier.py`
- `mediapipe/model_maker/python/core/utils/hub_loader.py`
- `mediapipe/model_maker/python/text/text_classifier/text_classifier.py`
- `mediapipe/model_maker/python/text/text_classifier/preprocessor.py`

These now set `TFHUB_USE_KERAS_3=1` **before** importing `tensorflow_hub`,
ensuring TF Hub creates Keras 3–compatible layers when using TF 2.20+.

Why:
- Avoids `KerasLayer` being a legacy `tf_keras.Layer` that Keras 3 rejects.

---

## 4) Model Maker: deterministic data loading

### `mediapipe/model_maker/python/vision/gesture_recognizer/dataset.py`
- Sorts `tf.io.gfile.glob(...)` results before shuffle.

Why:
- `glob()` order is nondeterministic; sorting fixes reproducibility and
  prevents subtle dataset ordering differences across runs.

---

## 5) Model Maker: export without metadata (when `tasks.cc` missing)

The following export methods now accept `include_metadata: bool = True`:

### Vision
- `mediapipe/model_maker/python/vision/image_classifier/image_classifier.py`
- `mediapipe/model_maker/python/vision/object_detector/object_detector.py`
- `mediapipe/model_maker/python/vision/gesture_recognizer/gesture_recognizer.py`

### Text
- `mediapipe/model_maker/python/text/text_classifier/text_classifier.py`
  (both the base export path and the BERT-specific override)

Behavior:
- `include_metadata=False` writes a valid `.tflite` or `.task` without embedding
  metadata. This avoids the `mediapipe.tasks.cc` dependency.
- If metadata is requested and native bindings are missing, a clear error is
  raised explaining the required dependency.

Gesture recognizer:
- When metadata is skipped, the code still builds the `.task` bundle by
  packaging raw model assets directly (no metadata population step).

Why:
- The public wheel does not ship `mediapipe.tasks.cc`, so metadata population
  cannot run without a custom build.

---

## 6) Model Maker: dependency simplifications and splits

### New/updated model maker setup files
- `mediapipe/model_maker/setup_vision.py`
- `mediapipe/model_maker/setup_text.py`
- `mediapipe/model_maker/requirements_vision.txt`
- `mediapipe/model_maker/requirements_text.txt`

Why:
- Allow installing vision-only or text-only Model Maker to avoid TF/TF-Text
  dependency conflicts.

---

## 7) Core utils replacements

### `mediapipe/model_maker/python/core/utils/distribute_utils.py`
- Local helper added to avoid depending on TF Model Garden (`tf-models-official`).

### `mediapipe/model_maker/python/core/utils/loss_functions.py`
- Removed dependency on `official.modeling.tf_utils` and replaced with local
  safe-mean logic.

Why:
- `tf-models-official` pulls incompatible TensorFlow pinning in modern stacks.

---

## 8) Known non-source changes (ignore in PR)

The following are build outputs and should not be committed:

- `mediapipe/model_maker/build/**`
- `mediapipe/model_maker/pip_src/**`
- `mediapipe/model_maker/dist/*.whl`
- `wheelhouse/*.whl`
- `.egg-info`, `.pyc`, and other generated artifacts

---

## Impact Summary

✅ **Model Maker now runs on modern TF/Keras stacks** (Keras 3 mode supported).  
✅ **Exports can succeed without native metadata bindings** (`include_metadata=False`).  
✅ **Imports are robust** even when `mediapipe.tasks.cc` is missing.  
✅ **Deterministic dataset loading** for gesture recognizer.  
✅ **Reduced dependency conflicts** via split installs and removal of model garden deps.

If you want metadata embedded in exported models, you still need a MediaPipe
wheel that ships `mediapipe.tasks.cc` (native bindings).
