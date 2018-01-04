"""Image data classifier."""

from pathlib import Path
import numpy as np
import cv2
from keras.models import load_model


class Classifier:
    """Classifier class."""

    def __init__(self):
        """Classifier constructor."""
        model_def = str(Path.cwd().joinpath('static/CNN_two_convs_30122017.h5'))
        model = load_model(model_def)
        model.summary()

    def swap_axes(image):
        """Convert RGB axes to to BGR as required by Keras / Theano."""
        image_convert = np.swapaxes(np.swapaxes(image, 1, 2), 0, 1)
        return image_convert

    def classify(image):
        """Classify a provided image file."""
        image = cv2.resize(image, (224, 224))
        image = swap_axes(image)
        return model.predict(image)
