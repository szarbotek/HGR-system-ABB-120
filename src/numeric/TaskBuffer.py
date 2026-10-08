from collections import deque
from dataclasses import dataclass


@dataclass
class TimeCell:
    value: str
    duration: int  # ms

class TaskBuffer:
    """
        Represents a discrete stream of gestures as time-based segments,
        where consecutive identical gestures are combined into a single segment.
    """

    def __init__(self, data=None, max_cells=60, base_time_ms = 100):

        self.base_time_ms = base_time_ms
        self.max_cells = max_cells
        self._buffer = deque()
        self.whole_time = self.max_cells*self.base_time_ms

        if data is not None:
            self.extend(data)

    def get_first(self ) -> TimeCell:
        return self._buffer[-1]

    def get_last(self) -> TimeCell:
        return self._buffer[0]

    def push(self, value: str):
        """
            Adds a sample.

            If the last cell has the same value,
            increases its duration by base_time_ms.

            If the value is different, creates a new cell.
        """

        if self._buffer and self._buffer[-1].value == value:
            self._buffer[-1].duration += self.base_time_ms
        else:
            self._buffer.append(
                TimeCell(
                    value=value,
                    duration=self.base_time_ms
                )
            )

        if self.total_time > self.whole_time:
            # cells Limit
            last_cell = self._buffer[0]
            last_cell.duration -= self.base_time_ms

            if last_cell.duration <= 0:
                self._buffer.popleft()


    def extend(self, data):
        """
        Dodaje cały wektor.

        Przykład:
            ['A', 'A', 'A', 'B', 'C', 'C', 'A']
        """
        for value in data:
            self.push(value)

    # def pop_time(self, time_ms: int):
    #     """
    #     Usuwa czas od końca bufora
    #
    #     Zwraca liczbę ms, których nie udało się usunąć.
    #     """
    #
    #     if time_ms < 0:
    #         raise ValueError("time_ms must be >= 0")
    #
    #     remaining = time_ms
    #
    #     while remaining > 0 and self._buffer:
    #
    #         last = self._buffer[-1]
    #
    #         if last.duration <= remaining:
    #             remaining -= last.duration
    #             self._buffer.pop()
    #         else:
    #             last.duration -= remaining
    #             remaining = 0
    #
    #     return remaining

    def get(self):
        data = self._buffer.copy()
        data.reverse()
        return {
            index: {
                "value": cell.value,
                "duration": cell.duration
            }
            for index, cell in enumerate(data)
        }

    @property
    def total_time(self):
        return sum(cell.duration for cell in self._buffer)

    @property
    def is_empty(self):
        return not self._buffer

    def __len__(self):
        return len(self._buffer)

    def __repr__(self):
        return repr(self.get())


if __name__ == "__main__":
    tc = TaskBuffer()
    tc.extend( ['A', 'A', 'A', 'B', 'C', 'C', 'A'] )
    print(tc)