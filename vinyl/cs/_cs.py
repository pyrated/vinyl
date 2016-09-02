import io
import os
from abc import ABC, abstractmethod
from copy import copy
from numbers import Integral
from typing import Callable, Optional, Generic, TypeVar


__all__ = [
    'StreamBase',
    'Location',
    'IOType',
    'IOWrapperStream',
    'StringStream'
]


class Location(object):
    @property
    def line(self) -> Integral:
        return self._line

    @property
    def column(self) -> Integral:
        return self._column

    def __init__(self, line: Integral=1, column: Integral=1):
        super().__init__()
        self._line = line
        self._column = column


class StreamBase(ABC):
    UntilMatcher = Callable[[Optional[str], str], bool]

    @abstractmethod
    def _read_raw(self, n: Integral=1) -> str:
        pass

    @abstractmethod
    def _set_offset(self, value: Integral=1):
        pass

    @property
    @abstractmethod
    def offset(self) -> Integral:
        return 0

    @property
    @abstractmethod
    def ended(self) -> bool:
        return True

    def read(self, n: Integral=1) -> str:
        s = self._read_raw(n)
        for c in s:
            if c == '\n':
                self._location._line += 1
                self._location._column = 1
            else:
                self._location._column += 1
        return s

    def read_until(self, until: UntilMatcher) -> str:
        offset = self.offset
        prev = None
        length = 0
        c = self.peek()
        while not self.ended and not until(prev, c):
            length += 1
            self._set_offset(offset + length)
            prev, c = c, self.peek()
        self._set_offset(offset)
        return self.read(length)

    def read_until_exactly(self, c: str) -> str:
        return self.read_until(lambda p, n: n == c)

    def peek(self, n: Integral=1) -> str:
        offset = self.offset
        s = self._read_raw(n)
        self._set_offset(offset)
        return s

    @property
    def line(self) -> Integral:
        return self._location._line

    @property
    def column(self) -> Integral:
        return self._location._column

    @property
    def location(self) -> Location:
        return copy(self._location)

    def __init__(self):
        super().__init__()
        self._location = Location()


IOType = TypeVar('IOType', io.RawIOBase, io.BufferedIOBase, io.TextIOBase)


class IOWrapperStream(StreamBase, Generic[IOType]):
    def _read_raw(self, n: Integral=1) -> str:
        return self._codeio.read(n)

    def _set_offset(self, value: Integral=1):
        self._codeio.seek(value)

    @property
    def offset(self) -> Integral:
        return self._codeio.tell()

    @property
    def ended(self) -> bool:
        try:
            fileno = self._codeio.fileno()
            offset = os.fstat(fileno).st_size
        except io.UnsupportedOperation:
            old_offset = self.offset
            self._codeio.seek(0, io.SEEK_END)
            offset = self._codeio.tell()
            self._codeio.seek(old_offset)
        return self.offset == offset

    def __init__(self, codeio: IOType):
        super().__init__()
        self._codeio = codeio


class StringStream(IOWrapperStream):
    def __init__(self, string: str):
        super().__init__(io.StringIO(string))
