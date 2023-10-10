'''Tests for validators.py.'''
# pylint: disable=invalid-name
# pylint: disable=unnecessary-lambda
# pylint: disable=unnecessary-lambda-assignment
import unittest

from src.validators import positive, non_negative, ascending, descending

class TestPositive(unittest.TestCase):
    '''Tests positive validation decorator function.'''
    def test_positive_0_raises_value_error(self):
        '''0 raises ValueError.'''
        fx = lambda x: x
        with self.assertRaises(ValueError):
            positive(fx)(x=0)
    def test_is_positive_1_returns_function_result(self):
        '''1 returns 1.'''
        fx = lambda x: x
        self.assertEqual(positive(fx)(x=1), 1)
    def test_is_positive_multiple_positive_inputs_returns_function_result(self):
        '''1.0 returns 1.0.'''
        def fxyz(x: float, y: float, z: float) -> float:
            return x + y + z
        self.assertEqual(positive(fxyz)(x=1.0, y=2.0, z=3.0), 6.0)
    def test_is_positive_multiple_negative_inputs_raises_value_error(self):
        '''-1.0 raises ValueError.'''
        def fxyz(x: float, y: float, z: float) -> float:
            return x + y + z
        with self.assertRaises(ValueError):
            positive(fxyz)(x=-1.0, y=2.0, z=3.0)
    def test_is_positive_non_number_skipped(self):
        '''"1" does not raise error.'''
        fx = lambda x: x
        try:
            positive(fx)(x="1")
        except TypeError:
            self.fail("positive(fx)(x='1') raised TypeError unexpectedly!")
    def test_is_positive_as_decorator_0_raises_value_error(self):
        '''0 raises ValueError.'''
        @positive
        def fx(x: float) -> float:
            return x
        with self.assertRaises(ValueError):
            fx(x=0)
    def test_is_positive_as_decorator_1_returns_function_result(self):
        '''1 returns 1.'''
        @positive
        def fx(x: float) -> float:
            return x
        self.assertEqual(fx(x=1), 1)

class TestNonNegative(unittest.TestCase):
    '''Tests non-negative validation decorator function.'''
    def test_non_negative_0_returns_function_result(self):
        '''0 returns 0.'''
        fx = lambda x: x
        self.assertEqual(non_negative(fx)(x=0), 0)
    def test_non_negative_1_returns_function_result(self):
        '''1 returns 1.'''
        fx = lambda x: x
        self.assertEqual(non_negative(fx)(x=1), 1)
    def test_non_negative_non_number_skipped(self):
        '''"1" does not raise error.'''
        fx = lambda x: x
        self.assertEqual(non_negative(fx)(x="1"), "1")
    def test_non_negative_negative_raises_value_error(self):
        '''-1 raises ValueError.'''
        fx = lambda x: x
        with self.assertRaises(ValueError):
            non_negative(fx)(x=-1)

class TestAscending(unittest.TestCase):
    '''Tests ascending validation decorator function.'''
    def test_ascending_1_2_3_returns_function_result(self):
        '''1, 2, 3 returns 1, 2, 3.'''
        fx = lambda x: sum(x)
        self.assertEqual(ascending(fx)(x=[1, 2, 3]), 6)
    def test_ascending_1_3_2_raises_value_error(self):
        '''1, 3, 2 raises ValueError.'''
        fx = lambda x: sum(x)
        with self.assertRaises(ValueError):
            ascending(fx)(x=[1, 3, 2])
    def test_ascending_1_1_2_returns_function_result(self):
        '''1, 1, 2 raises ValueError.'''
        fx = lambda x: sum(x)
        self.assertEqual(ascending(fx)(x=[1, 1, 2]), 4)
    def test_ascending_1_2_1_raises_value_error(self):
        '''1, 2, 1 raises ValueError.'''
        fx = lambda x: sum(x)
        with self.assertRaises(ValueError):
            ascending(fx)(x=[1, 2, 1])
    def test_ascending_single_value_returns_function_result(self):
        '''1 returns 1.'''
        fx = lambda x: x
        self.assertEqual(ascending(fx)(x=[1]), [1])
    def test_ascending_non_number_list_skipped(self):
        '''"1", "2" does not raise error.'''
        fx = lambda x: x
        self.assertEqual(ascending(fx)(x=["1", "2"]), ["1", "2"])

class TestDescending(unittest.TestCase):
    '''Tests descending validation decorator function.'''
    def test_descending_3_2_1_returns_function_result(self):
        '''3, 2, 1 returns 3, 2, 1.'''
        fx = lambda x: sum(x)
        self.assertEqual(descending(fx)(x=[3, 2, 1]), 6)
    def test_descending_3_1_2_raises_value_error(self):
        '''3, 1, 2 raises ValueError.'''
        fx = lambda x: sum(x)
        with self.assertRaises(ValueError):
            descending(fx)(x=[3, 1, 2])
    def test_descending_2_2_1_returns_function_result(self):
        '''2, 2, 1 raises ValueError.'''
        fx = lambda x: sum(x)
        self.assertEqual(descending(fx)(x=[2, 2, 1]), 5)
    def test_descending_3_2_2_returns_function_result(self):
        '''3, 2, 2 raises ValueError.'''
        fx = lambda x: sum(x)
        self.assertEqual(descending(fx)(x=[3, 2, 2]), 7)
    def test_descending_single_value_returns_function_result(self):
        '''1 returns 1.'''
        fx = lambda x: x
        self.assertEqual(descending(fx)(x=[1]), [1])
    def test_descending_non_number_list_skipped(self):
        '''"1", "2" does not raise error.'''
        fx = lambda x: x
        self.assertEqual(descending(fx)(x=["1", "2"]), ["1", "2"])
