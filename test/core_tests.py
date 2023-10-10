'''
Test cases for core.py
'''
# pylint: disable=line-too-long
import unittest

from src.live import BiomassTools
from src.constants import Constants
from src.core import Layer, factory, Core

class TestLayer(unittest.TestCase):
    '''
    Tests for layer object.
    '''
    @classmethod
    def setUpClass(cls):
        cls.default = factory(constants=Constants()).layers[0]

    def test_depth_returns_positive_value(self):
        '''
        Tests depth function.
        '''
        self.assertGreaterEqual(self.default.depth(), 0.0)

class TestFactory(unittest.TestCase):
    '''
    Tests for factory function.
    '''
    def test_first_layer_elevations_descending(self):
        '''
        Tests first layer elevations are descending.
        '''
        elevations = factory(constants=Constants()).layers[0].elevations
        self.assertTrue(elevations[0] > elevations[1])

    def test_first_layer_elevations_expected_values_from_constants(self):
        '''
        Tests first layer elevations come from constants du, rd.
        '''
        self.assertEqual(factory(constants=Constants()).layers[0].elevations, (Constants().du, Constants().db))

    def test_first_layer_depth_lt_rd_raises_error(self):
        '''
        Tests first layer depth < rd raises error.
        '''
        constants = Constants()
        constants.rd = constants.du - constants.db + 1.0
        with self.assertRaises(AttributeError):
            factory(constants=constants)

class TestCore(unittest.TestCase):
    '''
    Tests for core object.
    '''
    @classmethod
    def setUpClass(cls):
        cls.default: Core = factory(constants=Constants())

    def test_layers_returns_list(self):
        '''
        Tests layers returns list.
        '''
        self.assertIsInstance(self.default.layers, list)
    def test_layers_returns_list_of_layers(self):
        '''
        Tests layers returns list of layers.
        '''
        self.assertIsInstance(self.default.layers[0], Layer)
    def test_layers_returns_list_of_layers_descending(self):
        '''
        Tests layers returns list of layers descending.
        '''
        self.assertTrue(self.default.layers[0].elevations[0] > self.default.layers[0].elevations[1])
    def test_layers_returns_list_of_layers_expected_values_from_constants(self):
        '''
        Tests layers returns list of layers with expected values from constants.
        '''
        constants = Constants()
        constants.rd = constants.du - constants.db
        self.assertEqual(factory(constants=constants).layers[0].elevations, (constants.du, constants.db))
    def test_layers_raises_attribute_error_for_layer_depth_lt_rd(self):
        '''
        Tests layers raises attribute error for layer depth < rd.
        '''
        constants = Constants()
        constants.rd = constants.du - constants.db + 1.0
        with self.assertRaises(AttributeError):
            factory(constants=constants)

    def test_transition_raises_error_for_negative_depth_delta(self):
        '''
        Tests transition raises error for negative depth delta.
        '''
        with self.assertRaises(ValueError):
            self.default.transition(depth_delta=-1.0)
    def test_transition_raises_error_for_negative_years(self):
        '''
        Tests transition raises error for negative years.
        '''
        with self.assertRaises(ValueError):
            self.default.transition(depth_delta=1.0, years=-1.0)
    def test_transition_raises_error_for_zero_years(self):
        '''
        Tests transition raises error for zero years.
        '''
        with self.assertRaises(ValueError):
            self.default.transition(depth_delta=1.0, years=0.0)
    def test_transition_raises_error_for_depth_delta_gt_rd(self):
        '''
        Tests transition raises error for depth delta > rd.
        '''
        constants = Constants()
        constants.rd = constants.du - constants.db + 1.0
        with self.assertRaises(AttributeError):
            factory(constants=constants).transition(depth_delta=constants.rd+1.0)
