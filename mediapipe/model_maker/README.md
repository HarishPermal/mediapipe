# MediaPipe Model Maker (fork) dependency strategy

This fork keeps the base package lightweight and moves TensorFlow-heavy
dependencies into installable extras. This avoids pulling in fragile deps
like `tensorflow-text` unless you actually use text features, and lets you
choose between the classic TF Model Garden package or the newer `no-deps`
variant.

## Install patterns

Core package only (no TF stack):

```bash
pip install -e .
```

TF 2.10-2.15 path (Keras 2.x APIs):

```bash
pip install -e .[tf2,vision,garden]
```

TF 2.16+ path (Keras 3 default, use legacy Keras if needed):

```bash
pip install -e .[tf2_16,legacy-keras,vision,garden-no-deps]
export TF_USE_LEGACY_KERAS=1
```

Text features (BERT tokenizer):

```bash
pip install -e .[text]
```

Full installs:

```bash
pip install -e .[all]
pip install -e .[all-tf216]
```

## Extras reference

- `tf2`: TensorFlow 2.10-2.15 + core TF deps
- `tf2_16`: TensorFlow 2.16+ + core TF deps
- `legacy-keras`: `tf-keras` for Keras 2.x API compatibility on TF 2.16+
- `vision`: vision-specific deps (TF Addons, TF Model Optimization)
- `text`: text-specific deps (`tensorflow-text`, `tensorflow-hub`)
- `garden`: TF Model Garden (`tf-models-official`)
- `garden-no-deps`: TF Model Garden no-deps (`tf-models-no-deps`)
- `all`: TF 2.10-2.15 + vision + text + garden
- `all-tf216`: TF 2.16+ + legacy-keras + vision + text + garden-no-deps

## Notes

- Keras 3 can break legacy Model Maker APIs. If you see Keras-related errors,
  install `legacy-keras` and set `TF_USE_LEGACY_KERAS=1` as shown above.
- If you do not use text models, skip the `text` extra to avoid
  `tensorflow-text` and its platform-specific wheels.

## Smoke tests

Run these after installing the relevant extras to confirm imports resolve.

Core only:

```bash
python -c "import mediapipe_model_maker as mm; print(mm.__version__)"
```

Text (BERT tokenizer):

```bash
python -c "from mediapipe_model_maker.python.text.text_classifier import bert_tokenizer"
```

Object detection (Model Garden):

```bash
python -c "from mediapipe_model_maker.python.vision.object_detector import detection"
```

Vision stack:

```bash
python -c "import tensorflow_addons, tensorflow_model_optimization"
```
