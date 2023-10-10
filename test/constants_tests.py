'''
Tests constants.py file items.
'''

import unittest
from pathlib import Path

import src.constants as const

#pylint: disable=invalid-name
class TestMorrisConstants(unittest.TestCase):
    '''Tests the path of the default constants file.'''
    def test_path_exists(self):
        '''Tests the path of the default constants file exists.'''
        path = Path(const.MORRIS_CONSTANTS)
        self.assertTrue(Path.exists(path))

class TestConstants(unittest.TestCase):
    '''Tests the Constants object.'''
    def test_default_attributes_initialized(self):
        '''Tests that the default objects attributes are initialized with appropriate types.'''
        is_ok:bool = True
        test_obj = const.Constants()
        for k, val in test_obj.__dict__.items():
            if k.startswith('__') or str(val).startswith('<function'):
                continue
            else:
                if k == 'file_path':
                    if not isinstance(val, str):
                        is_ok = False
                else:
                    if not isinstance(val, float):
                        is_ok = False
        self.assertTrue(is_ok)

    def test_conversion_g_to_cm(self):
        '''Test gram to cm conversion yields expected result.'''
        g, bi, sa = 1, 0.1, 1      # grams, g/cm3, cm2
        cm = g * (1/bi) * (1/sa)   # 10 cm
        self.assertAlmostEqual(cm, const.Constants().g_to_cm(1, organic=False))

    def test_conversion_cm_to_g(self):
        '''Test cm to g conversion yields expected result.'''
        cm, bi, sa = 10, 0.1, 1
        g = cm * (1 / ((1/bi) * (1/sa)))
        self.assertAlmostEqual(g, const.Constants().cm_to_g(cm=10, organic=False))
