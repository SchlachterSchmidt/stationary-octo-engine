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
        self.model = load_model(model_def)
        self.model.summary()


    def classify(self, image):
        """Classify a provided image file."""
        x = np.fromstring(image, dtype='uint8')
        print(x.shape)
        img = cv2.imdecode(x, cv2.IMREAD_UNCHANGED)
        np_image = cv2.resize(img, (224, 224))
        print(np_image.shape)
        np_image = np.expand_dims(np_image, axis=0)
        print(np_image.shape)
        np_image = np.swapaxes(np_image, 1, 3)
       	print(np_image.shape) 
        cv2.imwrite('filename.jpg', np_image)
        return self.model.predict(np_image).tolist()
