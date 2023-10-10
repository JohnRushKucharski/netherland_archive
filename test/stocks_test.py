'''
Tests stocks.py
'''
#pylint: disable=line-too-long
import unittest

from src.constants import Constants
from src.stocks import Tag, biomass_init, factory

class TestBiomass(unittest.TestCase):
    '''Tests class implementing Stock protocol.'''
    def test_biomass_init_morris_constants_factory(self):
        '''Tests default construction of Biomass object.'''
        is_ok: bool = True
        const = Constants()
        test_obj = biomass_init(constants=const, deposition=const.du - const.db, biomass=const.ro)
        if not (round(test_obj.length, 4) == 1.3892 and
                round(test_obj.weight, 4) == 0.0998):
            is_ok = False
        self.assertTrue(is_ok)

class TestStock(unittest.TestCase):
    '''Tests class implementing Stock protocol.'''
    def test_biomass_default_morris_constants_factory(self):
        '''Tests default construction of Biomass object.'''
        is_ok: bool = True
        const = Constants()
        test_obj = biomass_init(constants=const, deposition=const.du - const.db, biomass=const.ro)
        if not (round(test_obj.length, 4) == 1.3892 and
                round(test_obj.weight, 4) == 0.0998):
            is_ok = False
        self.assertTrue(is_ok)

    def test_conservation_of_organic_mass_default_morris_constants_factories(self):
        '''Tests default construction of Refactory and Labile object.'''
        test_constants = Constants()
        biomass, deposition = test_constants.ro, test_constants.du - test_constants.db
        test_stocks = factory(constants=test_constants, deposition=deposition, biomass=biomass)
        actual_length = test_stocks[Tag.REFRACTORY].length + test_stocks[Tag.LABILE].length
        expected_length = (test_constants.du - test_constants.db) * test_constants.fo
        self.assertAlmostEqual(actual_length, expected_length)

    def test_conservation_of_mass_default_initial_sediment_factories(self):
        '''Test total sediment in bins equals total sediment.'''
        test_constants = Constants()
        biomass, deposition = test_constants.ro, test_constants.du - test_constants.db
        test_stocks = factory(constants=test_constants, deposition=deposition, biomass=biomass)
        actual_length = test_stocks[Tag.REFRACTORY].length + test_stocks[Tag.LABILE].length + test_stocks[Tag.INORGANIC].length
        # test_inorganic, test_ash = inorganic_factory(constants=test_constants), ash_factory(constants=test_constants)
        # test_refractory, test_labile = refractory_factory(constants=test_constants), labile_factory(constants=test_constants)
        # actual_length = test_refractory.length + test_labile.length + test_inorganic.length + test_ash.length
        expected_length = test_constants.du - test_constants.db
        self.assertAlmostEqual(actual_length, expected_length)
