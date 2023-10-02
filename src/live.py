'''
Live module. 

A module for calculating belowground biomass 
and turnover of belowground biomass into labile and refractory material.

Uses:
    [1] EROSION: remove eroded biomass from previous layer(s).
    [2] TURNOVER: convert to labile and refractory material in previous layer(s).
        [a] k2 or 
        [b] 100% (if elevation < root zone)   
    [3] ADD TOP LAYER: biomass based on biomass at surface and elevations.
    [4] UPDATE BIOMASS: update between bottom depth (of new layer) and root zone. 
'''
from typing import Tuple, NamedTuple, Dict, Callable, Any

import numpy as np

from src.constants import Constants
from src.stock import Measurement, Stock, Tag
from src.validators import non_negative, non_negative_attribute, ascending_non_negative_attribute

def biomass_at_depth(constants: Constants) -> Callable[[float, float, bool], float]:
    '''
    Returns a function that computes biomass at a given depth [in g/cm].

    Notes:
        [1] Returns equation 3 in Morris & Bowden.
        [2] It is exponential decay: Poe^-kt with P=biomass and t=depth.
    '''
    @non_negative
    def f(biomass_at_top: float, depth: float, output_weight: bool) -> float:  # pylint: disable=invalid-name
        '''
        Returns the biomass at a given depth [in g or g/cm2].

        Args:
            biomass (float): biomass at surface [in g/cm2].
            depth (float): depth [in cm].
            output_weight (bool): if True, returns biomass in g, otherwise g/cm2.
        
        Returns:
            float: biomass [in g or g/cm2].

        Notes:
            [1] This is eq. 3 in Morris & Bowden.
            [2] This is exponential decay: Poe^-kt with P=biomass and t=depth.
            [3] Surface area term is added to convert from g/cm2 to g.
        '''
        # pylint: disable=line-too-long
        if depth > constants.rd:
            return 0.0
        result = biomass_at_top * np.exp(-constants.k1*depth)
        return result * constants.sa if output_weight else result
    return f

def biomass_between_depths(
        constants: Constants=Constants(),
        distribution_function: Callable[..., Any] = biomass_at_depth) -> Callable[[float, Tuple[float, float]], float]:  # pylint: disable=line-too-long
    '''
    Returns a function that computes biomass [in g] between two elevations [in cm].

    Notes:
        [1] This is eq. 4 in Morris & Bowden.
        [2] This is the integral of between the depths.
        [3] Returns g not g/cm2 (as it is in Morris & Bowden).
    '''
    @non_negative
    def integrate(biomass_at_top: float, depths: Tuple[float, float]) -> float:
        ascending_non_negative_attribute(key='depths', value=depths)
        #TODO: why is the result less than biomass_at_depth(biomass, depth[0])?
        # if not depths[0] < constants.rd and biomass_at_top > 0.0:
        #     raise AttributeError('Top depth of layer with biomass must be less than root depth.')
        f = distribution_function(constants=constants) # pylint: disable=invalid-name
        return (f(biomass_at_top=biomass_at_top, depth=depths[1], output_weight=True) -
                f(biomass_at_top=biomass_at_top, depth=depths[0], output_weight=True))/-constants.k1
    return integrate

def turnover(constants: Constants) -> Callable[[float], Tuple[float, float, float]]:
    '''
    Returns a function that computes turnover of biomass
    into labile, refractory, and inorganic material [in g/yr].

    Notes:
        [1] This is parts of equations 5, 6 & 10 in Morris & Bowden.
        [2] Eq. 5: k2(1-fc)Wb(t) is turnover to labile material (with fl=1-fc).
        [3] Eq. 6: k2fcWb(t) is turnover to refractory material.
        [4] Eq. 10: -k3(Wb)k2 is turnover of inorganic ash by below ground biomass.
        [5] Assumes no loss of biomass, e.g. turnover simultaneously replaced by new biomass.
        [6] Assumes biomass input is in g not g/cm2 (as it is in Morris & Bowden).
    '''
    @non_negative
    def f(biomass: float) -> Tuple[float, float, float]:  # pylint: disable=invalid-name
        '''
        Returns a tuple of labile, refractory, and inorganic material [in g/yr].

        Args:
            biomass (float): biomass [in g] (NOT g/cm2).

        Returns:
            Tuple[float, float, float]: labile, refractory, and inorganic material [in g/yr].

        Notes:
            [1] This is parts of equations 5, 6 & 10 in Morris & Bowden.
            [2] First element, eq. 5: k2(1-fc)Wb(t) is turnover to labile material (with fl=1-fc).
            [3] Second element, eq. 6: k2fcWb(t) is turnover to refractory material.
            [4] Third element, eq. 10: -k3(Wb)k2 is turnover to inorganic material.
            [5] Assumes no loss of biomass, e.g. turnover simultaneously replaced by new biomass.
            [6] Assumes biomass is in g not g/cm2 (as it is in Morris & Bowden).
        '''
        # return Tuple[labile, refractory, inorganic]
        return (biomass * constants.k2 * constants.fl,
                biomass * constants.k2 * constants.fc,
                biomass * constants.k2 * constants.k3)
    return f

Depths = NamedTuple('Layers', [('top', float), ('live_bottom', float), ('bottom', float)])  # pylint: disable=line-too-long

def measurement_converter(tools: 'Tools') -> Callable[[float, Measurement, Measurement], float]:
    '''
    Returns function to convert biomass weights [g] and length [in cm].
    '''
    def f(biomass: float, input_type: Measurement, output_type: Measurement) -> float:  # pylint: disable=invalid-name
        '''
        Returns amount converted from 
        input type [weight, or length] to output type [weight or length].

        Args:
            biomass (float): biomass to convert [in g or cm].
            input_type (Measurment): input measurement type.
            output_type (Measurment): output measurement type.

        Returns:
            float: biomass [in g or cm].        
        '''
        if input_type == output_type:
            return biomass
        match input_type:
            case Measurement.WEIGHT: # convert weight to length.
                return biomass * tools.weight_to_length_constant
            case Measurement.LENGTH: # convert length to weight.
                return biomass / tools.weight_to_length_constant
            case _:
                raise NotImplementedError(f'Unknown measurement type: {input_type}.')
    return f

class Tools:
    '''
    Utility functions for biomass calculations given a set of constants.
    '''
    def __init__(self, constants: Constants=Constants()):
        self.factory = create_factory(tools=self)
        self.distribution = biomass_at_depth(constants=constants)
        self.integrate = biomass_between_depths(
            constants=constants, distribution_function=biomass_at_depth)
        self.remove = remove(tools=self) # type: ignore
        self.turnover = turnover(constants=constants) # type: ignore
        self.measurement_converter = measurement_converter(tools=self)

        self.weight_to_length_constant = constants.g_to_cm(grams=1, organic=True)
        self.max_root_depth = constants.rd

    def biomass_factory(self, biomass_at_top: float, depths: Tuple[float, float]) -> 'Biomass':
        '''
        Creates new biomass object.

        Args:
            biomass_at_top (float): biomass at surface [in g/cm2].
            depths (Tuple[float, float]): depths of top and bottom of layer [in cm].

        Returns:
            Biomass: new biomass object.
        '''
        _depths = self.biomass_depths(depths=depths)
        return Biomass(
            depths=_depths, tools=self,
            stock=self.integrate(biomass_at_top=biomass_at_top, depths=depths), # type: ignore
            measurements=self.measurements(biomass_at_top=biomass_at_top, depths=_depths))

    def biomass_depths(self, depths: Tuple[float, float]) -> Depths:
        '''
        Computes top, bottom of live layer and bottom of biomass [in cm].
        '''
        return Depths(top=depths[0],
                      live_bottom=depths[1] if depths[1] < self.max_root_depth else self.max_root_depth,  # pylint: disable=line-too-long
                      bottom=depths[1])

    def measurements(self, biomass_at_top: float, depths: Depths) -> Depths:
        '''
        Computes biomass at top, bottom of live layer and bottom [in g/cm].

        Args:
            biomass_at_top (float): biomass at surface [in g/cm2].
            depths (Depths): depths of top, bottom of live layer and bottom [in cm].

        Returns:
            Depths: biomass at top, bottom of live layer and bottom [in g/cm].

        Raises:
            AttributeError: if top depth is below root zone and biomass_at_top is positive.

        Notes:
            Uses distribution function to compute biomass at bottom of live layer and bottom.
        '''
        if depths.top >= self.max_root_depth:
            if biomass_at_top > 0.0:
                raise AttributeError(
                    f'''The top depth: {depths.top} of layer with live biomass: {biomass_at_top} 
                    cannot be below the root zone: {self.max_root_depth}.''')
            return Depths(top=0.0, live_bottom=0.0, bottom=0.0)
        # there is some live biomass in layer.
        live_bottom = self.distribution(
            biomass_at_top=biomass_at_top,  # type: ignore
            depth=depths.live_bottom-depths.top, # counts from top layer.
            output_weight=False)
        return Depths(top=biomass_at_top, live_bottom=live_bottom, bottom=biomass_at_top)

def remove(tools: Tools) -> Callable[['Biomass', float], Tuple[float, float, float]]:  # pylint: disable=line-too-long
    '''
    Returns a function that removes biomass from layer due to accretion or deposition,
    when max root depth is exceeded.

    Note:
        This is not part of the Morris & Bowden model.
    '''
    # pylint: disable=invalid-name
    @non_negative
    def f(biomass: 'Biomass', depth_delta: float) -> Tuple[Tuple[float, float, float], Tuple[float, float, float]]:  # pylint: disable=line-too-long
        '''
        Returns two tuples:
        Tuple of labile, refractory, and inorganic material removed [in g].
        Tuple of top, live bottom, and bottom of layer biomass [in g/cm2].

        Args:
            biomass (Biomass): biomass [in g].
            depth_delta (Biomass): depth change [in cm].

        Returns:
            Tuple[Tuple[float, float, float], Tuple[float, float, float]]: 
                [0] labile, refractory, and inorganic material removed [in g].
                [1] top, live bottom, and bottom of layer biomass [in g/cm2].

        Notes:
            This is not part of the Morris & Bowden model.
        '''
        # compute depths of material to remove in cm.
        top_of_removal = max(
            biomass.depths.top,
            biomass.depths.live_bottom - depth_delta)
        removal_depths = (
            top_of_removal,
            biomass.depths.bottom)
        # live material at top of removal zone in g/cm2.
        biomass_at_top_of_removal = tools.distribution(
            biomass_at_top=biomass.measurements.top, # type: ignore
            depth=top_of_removal, output_weight=False)
        # biomass to be removed in g.
        biomass_to_remove = tools.integrate(
            biomass_at_top=biomass_at_top_of_removal,# type: ignore
            depths=removal_depths)
        # Tuple[Tuple[labile, refractory, inorganic], Tuple[top, live_bottom, bottom]]
        return (tools.turnover(biomass=biomass_to_remove), # type: ignore
        (biomass.measurements.top, biomass_at_top_of_removal, 0.0))
    return f

class Biomass(Stock):
    '''
    Data structure for below ground biomass.
    '''
    def __init__(self, depths: Depths, stock: float,
                 measurements: Depths, tools: Tools) -> None:
        non_negative_attribute('stock', stock)
        self.tools = tools
        self._stock = stock
        self.depths = depths
        self.tag = Tag.BIOMASS
        self.measurements = measurements
        self.measurement_type = Measurement.WEIGHT
        self.converter = self.tools.measurement_converter

    def update(self, increment: float, inc_type: Measurement) -> None:
        '''
        Updates biomass by increment.
        '''
        # TODO: should the depths be updated.
        self._stock += self.converter(increment, inc_type, self.measurement_type)

    def turnover(self, output_type: Measurement) -> Tuple[float, float, float]:
        '''
        Returns labile, refractory and inorganic material [in g/yr] from turnover.

        Args:
            output_type (Measurement): output measurement type.

        Returns:
            Tuple[float, float, float]: labile, refractory and inorganic material [in g].h
        '''
        # pylint: disable=line-too-long
        return self.__convert_tuple(
            self.tools.turnover(biomass=self._stock), output_type) # type: ignore

    def removal(self, depth_delta: float, output_type: Measurement) -> Tuple[float, float, float]:
        '''
        Returns labile, refractory, and inorganic material [in g] removed due to erosion.

        Args:
            depth_delta (float): increase in layer depths [in cm].

        Returns:
            Tuple[float, float, float]: labile, refractory, and inorganic material [in g].
        '''
        # TODO: Test - Does removal conserve mass s.t. mass[t-1] - removal = mass[t]?
        removal, measurements = self.tools.removal( # type: ignore
            biomass=self, depth_delta=depth_delta)
        self.measurements = measurements
        self.update(-sum(removal), self.measurement_type)
        return self.__convert_tuple(removal, output_type)

    def __convert_tuple(self, values: Tuple[float, float, float],
                        output_type: Measurement) -> Tuple[float, float, float]:
        '''
        Converts tuple of biomass to output measurement.
        '''
        if output_type == self.measurement_type:
            return values
        return tuple(self.tools.measurement_converter(x, output_type) for x in values)  # type: ignore # pylint: disable=line-too-long

    def depths_dictionary(self) -> Dict[str, Tuple[float,float]]:
        '''
        Returns of dictionary of depth, biomass pairs.
        '''
        return {
            'top': (self.depths.top, self.measurements.top),
            'live_bottom': (self.depths.live_bottom, 
                            self.measurements.live_bottom),
            'bottom': (self.depths.bottom, self.measurements.bottom)
        }

class BiomassOut(Stock):
    '''
    Biomass leaving the system (via erosion), used to track mass balance.
    '''
    def __init__(self, stock: float, tools: Tools,
                 measurement_type: Measurement) -> None:
        non_negative_attribute('stock', stock)
        self._stock = stock
        self.tag = Tag.OUT_BIOMASS
        self.measurement_type = measurement_type
        self.converter = tools.measurement_converter

    def update(self, increment: float, inc_type: Measurement):
        '''
        Updates biomass leaving system by increment.
        '''
        self._stock += self.converter(increment, inc_type, self.measurement_type)

class Live:
    '''
    Living stocks in layer.
    '''
    def __init__(self, stocks: Biomass,
                 measurement_type: Measurement) -> None:
        self._stocks = stocks
        self.measurement_type = measurement_type
        self.inactive_stocks = BiomassOut(stock=0.0, tools=self._stocks.tools,
                                          measurement_type=self.measurement_type)
    @property
    def biomass(self) -> Biomass:
        '''
        Returns biomass.
        '''
        return self._stocks
    @property
    def weight(self) -> float:
        '''
        Returns total weight of active animate material [in g].
        '''
        return self._stocks.weight
    @property
    def length(self) -> float:
        '''
        Returns total length of active animate material [in cm].
        '''
        return self._stocks.length
    @property
    def total_weight(self) -> float:
        '''
        Returns total weight of all animate material [in g].
        '''
        return self.weight + self.inactive_stocks.weight
    @property
    def total_length(self) -> float:
        '''
        Returns total length of all animate material [in cm].
        '''
        return self.length + self.inactive_stocks.length

    def transfer(self, biomass_at_top: float, depth_delta: float,
                 output_type: Measurement) -> Tuple[Tuple[float, float, float], Tuple[float, float, float]]:  # pylint: disable=line-too-long
        '''
        Performs the following operations (in order):
            [1] turnover [in g or cm / yr]
            [2] removal [in g or cm] (no time component)
            [3] replace biomass object (using biomass_at_surface and depth_delta)

        Returns:
            Tuple[Tuple[float, float, float], Tuple[float, float, float]]:
                [0] turnover: labile, refractory, and inorganic material [in g or cm / yr].
                [1] removal:  labile, refractory, and inorganic material [in g or cm].
        '''
        # TODO: do the depths change due to transfer.
        # TODO: Test for conservation of mass, i.e. is stock[t-1] + biomass_change = stock[t]?
        _turnover = self._stocks.turnover(output_type=output_type)
        _removals = self._stocks.removal(depth_delta=depth_delta, output_type=output_type)
        self._stocks = self._stocks.tools.biomass_factory(
            biomass_at_top=biomass_at_top,
            depths=(self._stocks.depths.top + depth_delta,
                    self._stocks.depths.bottom + depth_delta))
        # Tuple[turnover [g/yr], removal [g]]
        return (_turnover, _removals)

def create_factory(tools: Tools) -> Callable[[float, Tuple[float, float]], Live]:
    '''
    Returns a function that creates a new live object.
    '''
    @non_negative
    def f(biomass_at_top: float, depths: Tuple[float, float]) -> Live:  # pylint: disable=invalid-name
        '''
        Returns a new live object.
        '''
        ascending_non_negative_attribute(key='depths', value=depths)
        return Live(stocks=tools.biomass_factory(
            biomass_at_top=biomass_at_top, depths=depths), # type: ignore
            measurement_type=Measurement.WEIGHT)
    return f
