from collections import deque
from typing import Generic, List, Optional, TypeVar, Iterable, overload, Union
from itertools import islice

# Definicja zmiennej typu dla generyka
T = TypeVar("T")


class CircularBuffer(Generic[T]):
    """Circular Buffer based on collections.deque.

    New elements are pushed to the left (index 0). When maximum capacity is
    reached, the oldest elements are automatically dropped from the right.
    """

    def __init__(self, max_length: int = 10) -> None:
        if max_length <= 0:
            raise ValueError("max_length must be greater than 0")

        self.max_len: int = max_length
        self.buffer: deque[T] = deque(maxlen=max_length)

    def put(self, element: T) -> None:
        """Pushes an element to the front (index 0)."""
        self.buffer.appendleft(element)

    def throw(self) -> T:
        """Removes and returns the oldest element (from the right side)."""
        if not self.buffer:
            raise IndexError("pop from an empty buffer")
        return self.buffer.pop()

    def pop(self, index: int = 0) -> T:
        """Removes and returns element at specified index."""
        if index == 0:
            return self.buffer.popleft()
        elif index == -1 or index == len(self.buffer) - 1:
            return self.buffer.pop()

        val = self.buffer[index]
        del self.buffer[index]
        return val

    def clear(self) -> None:
        """Clears the buffer."""
        self.buffer.clear()

    def extend(self, elements: Iterable[T]) -> None:
        """Pushes a sequence of elements to the buffer.

        Elements are inserted such that the last element in 'elements'
        ends up as the newest element at index 0.
        """
        data = [item for item in elements ]
        data.reverse()

        for item in data:
            self.put(item)

    @property
    def first(self) -> Optional[T]:
        """Returns the newest element (index 0) or None if empty."""
        return self.buffer[0] if self.buffer else None

    @property
    def last(self) -> Optional[T]:
        """Returns the oldest element or None if empty."""
        return self.buffer[-1] if self.buffer else None

    @property
    def is_full(self) -> bool:
        """Returns True if the buffer reached its maximum capacity."""
        return len(self.buffer) == self.max_len

    def get_buffer_index(self, index: int) -> Optional[T]:
        """Safely gets element at index, returning None if out of bounds."""
        try:
            return self.buffer[index]
        except IndexError:
            return None

    def get_list(self):
        return list(self.buffer)


    def get_buffer(self) -> List[T]:
        """Returns a copy of the buffer as a standard Python list (Newest ->
        Oldest)."""
        return list(self.buffer.copy())

    def get_reverse_buffer(self) -> List[T]:
        """Returns a copy of the buffer in reverse order (Oldest -> Newest)."""
        return list(reversed(self.buffer))

    def __len__(self) -> int:
        return len(self.buffer)

    def __iter__(self):
        return iter(self.buffer)

    def __getitem__(self, index: int) -> T:
        return self.buffer[index]

    def __str__(self) -> str:
        return str(list(self.buffer))

    def __list__(self) -> List[T]:
        return list(self.buffer.copy())

    @overload
    def __getitem__(self, item: int) -> T:
        ...

    @overload
    def __getitem__(self, item: slice) -> List[T]:
        ...

    def __getitem__(self, item: Union[int, slice]) -> Union[T, List[T]]:
        """Handles retrieving values by index `CB[0]` as well as slicing `CB[1:10]`."""
        if isinstance(item, slice):
            return list(islice(self.buffer, item.start, item.stop, item.step))
        return self.buffer[item]

    def __setitem__(self, key: int, value: T) -> None:
        """Allows modifying an element at a given index, e.g. CB[0] = 'new'."""
        self.buffer[key] = value

    def __delitem__(self, key: Union[int, slice]) -> None:
        """Allows deleting a single element or a slice, e.g. del CB[1:3]."""
        del self.buffer[key]

    def slice(
            self, start_index: int, finish_index: Optional[int] = None, step: int = 1
    ) -> List[T]:
        """Returns a sliced list from the buffer based on the provided indices."""
        buf_list = list(self.buffer)
        if finish_index is None:
            finish_index = start_index + 1
        return buf_list[start_index:finish_index:step]


