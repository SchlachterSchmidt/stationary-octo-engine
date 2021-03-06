"""Image data classifier."""

from pathlib import Path
import numpy as np
import cv2
from keras.models import load_model


class Classifier:
    """Classifier class."""

    def __init__(self):
        """Classifier constructor."""
        model_def = str(Path.cwd().joinpath(
            'app/static/CNN_two_convs_25022018_0900.h5'))
        self.model = load_model(model_def)
        self.model.summary()

    def classify(self, image_stream_data):
        """Classify image file stream."""
        # reading the image stream data as 8 bit binary data into ndarray
        np_data_arr = np.fromstring(image_stream_data, dtype='uint8')
        # decode ndarray to image with BGR channels (Inferred from data)
        raw_img = cv2.imdecode(np_data_arr, cv2.IMREAD_UNCHANGED)
        # resizing image to 224 *224 pixels
        np_image = cv2.resize(raw_img, (224, 224))
        # the classifier expected input format is:
        # (batch_size, channels, x_dims, y_dims). In this case, batch size = 1
        # performing two operations:
        # - add 4th dimension
        # - swap axes to put dimensions into right order
        # first, adding 4th dim:
        np_image_tensor = np.expand_dims(np_image, axis=0)
        # second converting to channels first ordering
        np_image_tensor = np.swapaxes(np.swapaxes(np_image_tensor, 1, 3), 2, 3)
        # making prediction on the image and returning probabilities
        # for each class as list (as ndarray are not jsonify-able)
        probabilities = self.model.predict(np_image_tensor).tolist()[0]
        prediction = np.asscalar(np.argmax(probabilities))
        # confidence is the probability associated with the predicted class
        confidence = probabilities[prediction]
        return probabilities, prediction, confidence
