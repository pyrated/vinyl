from abc import ABC, abstractmethod
from vinyl.lex import Location, StreamBase, StringStream

from ..patch import unittest


class TestLocation(unittest.TestCase):
    def test_default_location(self):
        location = Location()
        self.assertEqual(location.line, 1)
        self.assertEqual(location.column, 1)


class TestStreamBase(ABC, unittest.TestCase):
    @property
    def istream(self) -> StreamBase:
        return self._istream

    @staticmethod
    @abstractmethod
    def create_istream() -> StreamBase:
        return StreamBase()

    def setUp(self):
        self._istream = self.create_istream()

    def test_initial_stream_state(self):
        self.assertEqual(self.istream.line, 1)
        self.assertEqual(self.istream.column, 1)
        self.assertEqual(self.istream.offset, 0)
        self.assertFalse(self.istream.ended)

    def test_read_repeated(self):
        for index, c in enumerate('hello world'):
            self.assertEqual(self.istream.offset, index)
            self.assertEqual(self.istream.column, index + 1)
            self.assertEqual(c, self.istream.read())
            self.assertEqual(self.istream.offset, index + 1)
            self.assertEqual(self.istream.column, index + 2)
            self.assertEqual(self.istream.line, 1)
            self.assertFalse(self.istream.ended)
        self.assertEqual(self.istream.peek(), '\n')

    def test_read_past_new_line(self):
        s = self.istream.read_until_exactly('\n')
        self.assertEqual(s, 'hello world')
        self.assertEqual(self.istream.read(), '\n')
        self.assertEqual(self.istream.peek(), 't')
        self.assertEqual(self.istream.column, 1)
        self.assertEqual(self.istream.line, 2)
        self.assertFalse(self.istream.ended)

    def test_read_past_end(self):
        self.istream.read_until_exactly('!')
        c = self.istream.read(2)
        self.assertTrue(self.istream.ended)
        self.assertEqual(len(c), 1)

    def test_peek_past_end(self):
        self.istream.read_until_exactly('!')
        c = self.istream.peek(2)
        self.assertFalse(self.istream.ended)
        self.assertEqual(len(c), 1)


class TestStringStream(TestStreamBase):
    @staticmethod
    def create_istream() -> StreamBase:
        return StringStream('hello world\nthis is a test!')
