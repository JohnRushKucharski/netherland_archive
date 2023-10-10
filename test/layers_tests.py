'''
Tests layers.py file items.
'''

import unittest

import src.layer as layer
import src.layers as layers
from src.constants import Constants

class TestLayers(unittest.TestCase):
    '''Tests the Layers object.'''
    def test_default_attributes(self):
        '''Tests the default attribute values.'''
        test_obj = layers.Layers()
        is_ok: bool = True
        if not (test_obj.surface_area == 1.0 and
                len(test_obj.layers) == 1):
            is_ok = False
        self.assertTrue(is_ok)

    def test_accretion_in_two_layers(self):
        '''Tests that a simple two layer sediment core has the proper depth.'''
        test_obj = layers.factory()
        test_obj.update(deposition=2, biomass=1)
        self.assertAlmostEqual(test_obj.depth, 32)

class TestLayer(unittest.TestCase):
    '''
    Tests the Layer object
    '''
    def test_layer_factory_from_morris_constants(self):
        '''
        Builds single layer. Tests top, bottom and length of stocks attributes. 
        '''
        constant = Constants()
        test_obj = layer.factory(constants=constant,
                                 top=constant.du, bottom=constant.db, biomass=constant.ro)
        is_ok: bool = True
        if not (test_obj.top == 0.0 and
                test_obj.bottom == -30.0 and
                len(test_obj.stocks) == 4):
            is_ok = False
        self.assertTrue(is_ok)

    def test_attributes_from_morris_constants(self):
        '''Tests the Layers() default bottom layer attribute values.'''
        test_obj = layers.Layers()
        is_ok: bool = True
        if not (test_obj.layers[0].top == 0 and
                test_obj.layers[0].bottom == -30.0):
            is_ok = False
        self.assertTrue(is_ok)

    def test_second_accretion_layer_has_correct_elevations(self):
        '''Tests that second layer in accertion core has proper top, bottom elevations.'''
        test_layers = layers.factory()
        test_layers.update(deposition=2, biomass=1)
        is_ok: bool = True
        if not (test_layers.layers[1].top == 2.0 and
                test_layers.layers[1].bottom == 0.0):
            is_ok = False
        self.assertTrue(is_ok)
