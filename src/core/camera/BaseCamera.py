from typing import Tuple, Optional
from numpy.typing import NDArray

class BaseCamera:
    """Base class defining a unified interface for cameras."""

    def get_image(self) -> Tuple[Optional[NDArray], Optional[int]]:
        raise NotImplementedError

    def swap_objective(self, site: str) -> None:
        pass

    def close(self) -> None:
        pass