from sklearn.preprocessing import LabelEncoder
import numpy as np
import src.Config as Config

class GestureLabelEncoder:
    """
        Wrapper class for scikit-learn's LabelEncoder used for gesture class encoding/decoding.
    """

    def __init__(self, label_interpretation_path):
        self.encoder = LabelEncoder()
        self.encoder.classes_ = np.load( str(label_interpretation_path), allow_pickle=True)

    def encode(self, data) -> np.array:
        """
            Transforms text gesture labels into numerical class IDs.
        """

        return self.encoder.transform(data)

    def decode(self, class_ids: list | np.ndarray) -> list[str]:
        """
            Transforms numerical class IDs back to text gesture labels.
        """
        return list(self.encoder.inverse_transform(class_ids))

    def decode_single(self, class_id: int) -> str:
        """
            Transforms a single numerical class ID to a text gesture label with safety checks.

            :param class_id: Integer class index from model prediction
            :return: Text gesture label or Config.NONE_LABEL if out of bounds
        """
        try:
            if 0 <= class_id < len(self.encoder.classes_):
                return str(self.encoder.inverse_transform([class_id])[0]) # class ID = 7 -> one
            return Config.NONE_LABEL
        except Exception:
            return Config.NONE_LABEL