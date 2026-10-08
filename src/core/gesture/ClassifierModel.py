import keras
import src.Config as Config
import numpy as np

class ClassifierModel:
    def __init__(self, model_path):
        self.model = keras.models.load_model(model_path)

    def predict(self, landmark: np.ndarray) -> np.ndarray:
        """
            Runs model inference on the input landmark array.

            :param landmark: Input array of shape
            :return: Array of predicted probabilities for each class
        """
        return self.model.predict(landmark.reshape(1, 63), verbose=0) # [0., 0., 0., 0., 0., 0., 1., 0., 0., 0., 0., 0., 0.]

    @staticmethod
    def class_id(probabilities: np.ndarray) -> int:
        """
            Interpret the probabilities for each class ID.
        :param probabilities:
        :return:
        """
        if probabilities.ndim == 1:
            return int(np.argmax(probabilities))
        else:
            return int(np.argmax(probabilities, axis=1)[0]) # class ID = 7

    def predict_class_id(self, landmark: np.ndarray) -> int:
        """
            Runs inference and returns the numerical class index with the highest probability.

            :param landmark: Input array
            :return: Integer class ID
        """
        probabilities = self.predict(landmark.reshape(1, 63))
        return self.class_id(probabilities)

    def predict_batch_class_ids(self, landmarks: list[np.ndarray]) -> list[int]:
        """Runs inference on multiple landmark arrays at once (batching).

        :param landmarks: List of landmark arrays, each reshaped to (1, 63) or (63,)
        :return: List of predicted class IDs
        """

        batch = np.vstack([lm.reshape(1, 63) for lm in landmarks])
        predictions = self.model.predict(batch, verbose=0)
        class_ids = np.argmax(predictions, axis=1)

        return [int(cid) for cid in class_ids]