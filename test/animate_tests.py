'''
This file contains tests for the biomass module.
'''
# pylint: disable=invalid-name
# pylint: disable=line-too-long
import unittest

from src.constants import Constants
from src.live import biomass_at_depth, biomass_between_depths, turnover, BiomassTools, Measurement, Biomass, Depths

class TestBiomassAtDepth(unittest.TestCase):
    '''
    Tests biomass_at_depth function.
    '''
    def test_biomass_at_depth_depth_less_than_0_raises_value_error(self):
        '''
        Depth less than 0 raises ValueError.
        '''
        f = biomass_at_depth(constants=Constants())
        with self.assertRaises(ValueError):
            f(biomass_at_top=1.0, depth=-1.0)  # type: ignore
    def test_biomass_at_depth_depth_equal_to_rd_returns_0(self):
        '''
        Depth equal to root depth returns 0.
        '''
        f = biomass_at_depth(constants=Constants())
        self.assertAlmostEqual(f(biomass_at_top=1.0, depth=Constants().rd), 0.04978706836786395)  # type: ignore
    def test_biomass_at_depths_depth_eq_rd_plus_1_returns_0(self):
        '''
        Depth equal to root depth plus 1 returns 0.
        '''
        f = biomass_at_depth(constants=Constants())
        self.assertAlmostEqual(f(biomass_at_top=1.0, depth=Constants().rd+1), 0.0)  # type: ignore
    def test_biomass_at_depth_no_biomass_returns_0_at_0_depth(self):
        '''
        No biomass at surface returns 0 at surface.
        '''
        f = biomass_at_depth(constants=Constants())
        self.assertAlmostEqual(f(biomass_at_top=0.0, depth=0.0), 0.0)  # type: ignore
    def test_biomass_at_depth_no_biomass_returns_0_at_1_depth(self):
        '''
        No biomass at surface returns 0 at 1 depth.
        '''
        f = biomass_at_depth(constants=Constants())
        self.assertAlmostEqual(f(biomass_at_top=0.0, depth=1.0), 0.0)  # type: ignore
    def test_biomass_at_depth_1_biomass_returns_1_at_0_depth(self):
        '''
        1 biomass at surface returns 1 at surface.
        '''
        f = biomass_at_depth(constants=Constants())
        self.assertAlmostEqual(f(biomass_at_top=1.0, depth=0.0), 1.0)  # type: ignore
    def test_biomass_at_depth_1_biomass_returns_approx_0_9_at_1_depth(self):
        '''
        1 biomass at surface returns 0.9 at 1 depth, with k1=0.1.
        '''
        f = biomass_at_depth(constants=Constants())
        self.assertAlmostEqual(f(biomass_at_top=1.0, depth=1.0), 0.9, places=2)  # type: ignore

class TestBiomassBetweenDepths(unittest.TestCase):
    '''
    Tests biomass_between_depths function.
    '''
    def test_biomass_between_depths_inverted_range_raises_value_error(self):
        '''
        Depth range inverted raises ValueError.
        '''
        f = biomass_between_depths(constants=Constants())
        with self.assertRaises(ValueError):
            f(biomass_at_top=1.0, depths=(0.0, -1.0))  # type: ignore
    def test_biomass_between_depths_range_eq_0_returns_biomass_0(self):
        '''
        Depth range equal to 0 returns 0.
        '''
        f = biomass_between_depths(constants=Constants())
        self.assertEqual(f(biomass_at_top=1.0, depths=(1.0, 1.0)), 0.0)  # type: ignore
    def test_biomass_between_depths_returns_positive_value(self):
        '''
        Returns positive value.
        '''
        f = biomass_between_depths(constants=Constants())
        self.assertGreater(f(biomass_at_top=1.0, depths=(0.0, 1.0)), 0.0)  # type: ignore

class TestBiomassTools(unittest.TestCase):
    '''
    Tests biomass functions.
    '''
    def test_biomasstools_biomass_at_depth_returns_callable(self):
        '''
        Biomass at depth returns callable.
        '''
        self.assertTrue(callable(BiomassTools().distribution))

    def test_biomasstools_default_max_root_depth_is_rd(self):
        '''
        Default max root depth is rd.
        '''
        self.assertEqual(BiomassTools().max_root_depth, Constants().rd)

    def test_layer_depths_0_0_returns_0_0_0(self):
        '''
        Layer depths (0.0, 0.0) returns (0.0, 0.0, 0.0) layer depths.
        '''
        self.assertEqual(BiomassTools().biomass_depths(depths=(0.0, 0.0)), (0.0, 0.0, 0.0))
    def test_layer_depths_0_1_returns_0_1_1(self):
        '''
        Layer depths (0.0, 1.0) returns (0.0, 1.0, 1.0) layer depths.
        '''
        self.assertEqual(BiomassTools().biomass_depths(depths=(0.0, 1.0)), (0.0, 1.0, 1.0))
    def test_layer_depths_1_1_returns_1_1_1(self):
        '''
        Layer depths (1.0, 1.0) returns (1.0, 1.0, 1.0) layer depths.
        '''
        self.assertEqual(BiomassTools().biomass_depths(depths=(1.0, 1.0)), (1.0, 1.0, 1.0))
    def test_layer_depths_0_rd_returns_0_rd_rd(self):
        '''
        Layer depths (0.0, rd) returns (0.0, rd, rd) layer depths.
        '''
        self.assertEqual(BiomassTools().biomass_depths(depths=(0.0, Constants().rd)), (0.0, Constants().rd, Constants().rd))
    def test_layer_depths_0_rd_plus_1_returns_0_rd_rd_plus_1(self):
        '''
        Layer depths (0.0, rd+1) returns (0.0, rd, rd+1) layer depths.
        '''
        self.assertEqual(BiomassTools().biomass_depths(depths=(0.0, Constants().rd+1)), (0.0, Constants().rd, Constants().rd+1))
    def test_layer_depths_rd_rd_plus_1_returns_rd_rd_rd_plus_1(self):
        '''
        Layer depths (rd, rd+1) returns (rd, rd, rd+1) layer depths.
        '''
        self.assertEqual(BiomassTools().biomass_depths(depths=(Constants().rd, Constants().rd+1)), (Constants().rd, Constants().rd, Constants().rd+1))
    def test_layer_depths_rd_plus_1_rd_plus_2_returns_rd_plus_1_rd_rd_plus_2(self):
        '''
        Layer depths (rd+1, rd+2) returns (rd+1, rd, rd+2) layer depths.
        '''
        self.assertEqual(BiomassTools().biomass_depths(depths=(Constants().rd+1, Constants().rd+2)), (Constants().rd+1, Constants().rd, Constants().rd+2))

    def test_layer_measurement_biomass_eq_1_depths_rd_plus_1_rd_plus_2_raises_AttributeError(self):
        '''
        Biomass eq 1 depths (rd+1, rd+2) raises AttributeError.
        '''
        with self.assertRaises(AttributeError):
            BiomassTools().measurements(biomass_at_top=1.0, depths=BiomassTools().biomass_depths(depths=(Constants().rd+1, Constants().rd+2)))
    def test_layer_measurements_biomass_eq_0_depths_0_rd_returns_0_0_0(self):
        '''
        Biomass at top eq 0 layer depths (0.0, rd) returns (0.0, 0.0, 0.0) layer measurements.
        '''
        self.assertEqual(BiomassTools().measurements(biomass_at_top=0.0, depths=BiomassTools().biomass_depths(depths=(0.0, Constants().rd))), (0.0, 0.0, 0.0))
    def test_layer_measurement_biomass_eq_1_depths_0_rd_plus_1_returns_1_expected_bottom_0(self):
        '''
        Biomass at top eq 1 layer depths (0.0, rd+1) returns (1.0, expected, 0.0) layer measurements.
        '''
        self.assertEqual(BiomassTools().measurements(biomass_at_top=1.0, depths=BiomassTools().biomass_depths(depths=(0.0, Constants().rd+1))),
                         (1.0, BiomassTools().distribution(biomass_at_top=1.0, depth=Constants().rd), 0.0))  # type: ignore
    def test_layer_measurement_biomass_eq_0_depths_rd_plus_1_rd_plus_2_returns_0_0_0(self):
        '''
        Biomass at top eq 0 layer depths (rd+1, rd+2) returns (0.0, 0.0, 0.0) layer measurements.
        '''
        self.assertEqual(BiomassTools().measurements(biomass_at_top=0.0, depths=BiomassTools().biomass_depths(depths=(Constants().rd+1, Constants().rd+2))), (0.0, 0.0, 0.0))

    def test_biomass_0_biomass_at_top_returns_Biomass_with_empty_stock(self):
        '''
        0 biomass at top returns Biomass with empty stock.
        '''
        self.assertEqual(BiomassTools().factory(biomass_at_top=0.0, depths=(0.0, 1.0)).stock, 0.0)
    def test_biomass_0_biomass_at_top_returns_Biomass_with_0_0_measurements(self):
        '''
        0 biomass at top returns Biomass with (0.0, 0.0, 0.0) measurements tuple.
        '''
        self.assertEqual(BiomassTools().factory(biomass_at_top=0.0, depths=(0.0, 1.0)).measurements, Depths(0.0, 0.0, 0.0))
    def test_biomass_0_biomass_at_top_returns_Biomass_with_WEIGHT_stock_measurement(self):
        '''
        0 biomass at top returns Biomass with 0.0 stock measurement.
        '''
        self.assertEqual(BiomassTools().factory(biomass_at_top=0.0, depths=(0.0, 1.0)).measurement_type, Measurement.WEIGHT)  # type: ignore
    def test_biomass_1_biomass_at_top_returns_Biomass_with_expected_stock(self):
        '''
        1 biomass at top returns Biomass with expected stock.
        '''
        self.assertEqual(BiomassTools().factory(biomass_at_top=1.0, depths=(0.0, 1.0)).stock,
                         biomass_between_depths(constants=Constants())(biomass_at_top=1.0, depths=(0.0, 1.0)))  # type: ignore
    def test_biomass_1_biomass_at_top_returns_Biomass_with_expected_measurements(self):
        '''
        1 biomass at top returns Biomass with expected measurements tuple.
        '''
        self.assertEqual(BiomassTools().factory(biomass_at_top=1.0, depths=(0.0, 1.0)).measurements,
                         Depths(1.0,
                                       biomass_at_depth(constants=Constants())(biomass_at_top=1.0, depth=1.0),  # type: ignore
                                       biomass_at_depth(constants=Constants())(biomass_at_top=1.0, depth=1.0)))  # type: ignore

class TestTurnover(unittest.TestCase):
    '''
    Tests turnover function.
    '''
    def test_turnover_returns_tuple(self):
        '''
        Returns tuple.
        '''
        self.assertIsInstance(turnover(constants=Constants())(biomass=1.0), tuple)  # type: ignore
    def test_turnover_return_tuple_sums_to_total_turnover(self):
        '''
        Returns tuple that sums to total turnover.
        '''
        self.assertAlmostEqual(sum(turnover(constants=Constants())(biomass=1.0)), Constants().k2)  # type: ignore
    def test_turnover_negative_biomass_raises_value_error(self):
        '''
        Negative biomass raises ValueError.
        '''
        with self.assertRaises(ValueError):
            turnover(constants=Constants())(biomass=-1.0)  # type: ignore

class TestBiomass(unittest.TestCase):
    '''
    Tests Biomass class.
    '''
    @classmethod
    def setUpClass(cls) -> None:
        '''
        Set up default biomass.
        '''
        cls.default_biomass: Biomass = BiomassTools(constants=Constants()).factory(biomass_at_top=1.0, depths=(0.0, 1.0))

    def test_biomass_returns_expected_stock_approx_0_95(self):
        '''
        Biomass returns expected stock.
        '''
        self.assertEqual(self.default_biomass.stock, biomass_between_depths(constants=Constants())(biomass_at_top=1.0, depths=(0.0, 1.0)))  # type: ignore
    def test_biomass_default_returns_expected_layer_depths_0_1_1(self):
        '''
        Biomass returns expected layer depths.
        '''
        self.assertEqual(self.default_biomass.depths, (0.0, 1.0, 1.0))
    def test_biomass_returns_expected_measurements(self):
        '''
        Biomass returns expected measurements.
        '''
        self.assertEqual(self.default_biomass.measurements,
                         Depths(1.0,
                                       biomass_at_depth(constants=Constants())(biomass_at_top=1.0, depth=1.0),  # type: ignore
                                       biomass_at_depth(constants=Constants())(biomass_at_top=1.0, depth=1.0)))  # type: ignore

# class TestConversion(unittest.TestCase):
#     '''
#     Tests Biomass class conversion in Functions.
#     '''
#     @classmethod
#     def setUpClass(cls) -> None:
#         '''
#         Set up default biomass.
#         '''
#         cls.default_biomass: Biomass = BiomassTools(constants=Constants()).factory(biomass_at_top=1.0, depths=(0.0, 1.0))

#     def test_biomass_convert_returns_expected_stock(self):
#         '''
#         Biomass returns expected stock after conversion
#         '''
#         self.assertEqual(BiomassTools(constants=Constants()).convert(self.default_biomass).stock, self.default_biomass.stock * Constants().g_to_cm(grams=1, organic=True))
#     def test_biomass_convert_returns_expected_measurements(self):
#         '''
#         Biomass returns expected measurements after conversion
#         '''
#         self.assertEqual(BiomassTools(constants=Constants()).convert(self.default_biomass).measurements,
#                          tuple([self.default_biomass.measurements[i] * Constants().g_to_cm(grams=1, organic=True) for i in range(len(self.default_biomass.measurements))]))
#     def test_biomass_convert_returns_expected_measurement_type(self):
#         '''
#         Biomass returns expected stock measurement after conversion
#         '''
#         self.assertEqual(BiomassTools(constants=Constants()).convert(self.default_biomass).measurement_type, Measurement.LENGTH)  # type: ignore
#     def test_convert_length_to_weight_returns_expected_stock_weight(self):
#         '''
#         Convert length to width returns expected stock weight
#         '''
#         length = BiomassTools(constants=Constants()).convert(self.default_biomass)
#         self.assertEqual(BiomassTools(constants=Constants()).convert(length).stock, self.default_biomass.stock)  # type: ignore
#     def test_convert_length_to_weight_returns_expected_mesurement_weight(self):
#         '''
#         Convert length to width returns expected stock weight
#         '''
#         length = BiomassTools(constants=Constants()).convert(self.default_biomass)
#         self.assertEqual(BiomassTools(constants=Constants()).convert(length).measurements, self.default_biomass.measurements)  # type: ignore
