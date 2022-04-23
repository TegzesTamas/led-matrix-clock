from abc import abstractmethod, ABC
from common import Effect


class Drawer(ABC):
    @abstractmethod
    def draw(self, canvas, effect: Effect, brightness: int, color: dict):
        pass
