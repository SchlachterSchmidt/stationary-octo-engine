"""Image data classifier."""

from pathlib import Path
from keras.models import load_model


model_def = str(Path.cwd().joinpath('static/CNN_two_convs_30122017.h5'))
model = load_model(model_def)
model.summary()
