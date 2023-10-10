'''Tests the utilities module.'''

import unittest

from src.utilities import elevations_to_depth

class TestElevationsToDepth(unittest.TestCase):
    '''Tests elevations_to_depth function.'''
    def test_elevations_to_depth_elevations_in_reverse_order_raises_value_error(self):
        '''Elevations in reverse order raises ValueError.'''
        with self.assertRaises(ValueError):
            elevations_to_depth(elevations=(0.0, 1.0))
    def test_elevations_to_depth_elevation_not_number_raises_value_error(self):
        '''Elevation not number raises TypeError.'''
        with self.assertRaises(TypeError):
            elevations_to_depth(elevations=(0.0, "1.0"))
    def test_elevations_to_depth_elevations_tuple_length_1_value_error(self):
        '''Elevations not tuple length 2 raises ValueError.'''
        with self.assertRaises(ValueError):
            elevations_to_depth(elevations=(0.0,))
    def test_elevations_to_depth_elevations_tuple_length_3_value_error(self):
        '''Elevations not tuple length 2 raises ValueError.'''
        with self.assertRaises(ValueError):
            elevations_to_depth(elevations=(0.0, 1.0, 2.0))
    def test_elevations_to_depth_elevations_eq_0_returns_depth_0(self):
        '''Elevations equal to 0 returns depth 0.'''
        self.assertAlmostEqual(elevations_to_depth(elevations=(0.0, 0.0)), 0.0)
    def test_elevations_to_depth_elevations_1_0_returns_1(self):
        '''Elevations equal to 1 returns depth 1.'''
        self.assertAlmostEqual(elevations_to_depth(elevations=(1.0, 0.0)), 1.0)
    def test_elevations_to_depth_elevations_0_neg1_returns_1(self):
        '''Elevations equal to 1 returns depth 0.'''
        self.assertAlmostEqual(elevations_to_depth(elevations=(0.0, -1.0)), 1.0)
    def test_elevations_to_depth_elevations_neg1_neg2_returns_3(self):
        '''Elevations equal to 1 returns depth 2.'''
        self.assertAlmostEqual(elevations_to_depth(elevations=(1.0, -2.0)), 3.0)
