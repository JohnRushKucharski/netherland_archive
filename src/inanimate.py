'''
Module for inorganic, labile and refractory material.
'''
from typing import Tuple, NamedTuple, Callable

from src.constants import Constants
from src.validators import non_negative
from src.stock import Measurement, Stock, Tag, is_organic

def decomposition(constants: Constants) -> Callable[[float], float]:
    '''
    Returns function that converts labile material [in g/yr] that leaves the system.
    '''
    @non_negative
    def f(labile_weight: float) -> float:  # pylint: disable=invalid-name
        '''
        Decomposition of labile material [in g/yr], this a loss from the system.

        Notes:
            [1] This is part of eq. 5: kCl(t) in Morris & Bowden.
            [2] Labile weight is in g not g/cm2 (as it is in Morris & Bowden).
        '''
        return labile_weight * constants.k
    return f

def ash_uptake(constants: Constants) -> Callable[[float], float]:
    '''
    Returns function that computes uptake of inorganic ash [in g/yr] that leaves the system,
    though above ground biomass production (ash uptake).
    '''
    @non_negative
    def f(biomass_weight: float) -> float:  # pylint: disable=invalid-name
        '''
        Uptake of inorganic ash [g/yr] by above ground biomass.

        Notes:
            [1] This is part of eq. 10: -k3(Wb)B/Rl in Morris & Bowden.
        '''
        return constants.k3 * biomass_weight * constants.wa_to_rl
    return f

class Tools:
    '''
    Utility functions for inanimate material.
    '''
    def __init__(self, constants: Constants=Constants()):
        self.factory = create_factory(constants, self)
        self.ash_uptake = ash_uptake(constants)
        self.decomposition = decomposition(constants)
        self.weight_to_length_converter = constants.g_to_cm

def measurement_converter(
        tools: Tools, organic: bool) -> Callable[[float, Measurement, Measurement], float]:
    '''
    Returns function that converts weight to length [in cm].
    '''
    weight_to_length_constant: float = tools.weight_to_length_converter(grams=1, organic=organic)
    def f(amount: float, in_type: Measurement, out_type: Measurement) -> float:  # pylint: disable=invalid-name
        '''
        Returns amount converted 
        from input type [weight, or length] to output type [weight or length].

        Args:
            amount: value to convert [in g or cm].
            input: input measurement type.
            output: output measurement type.
        
        Returns:
            Amount converted to output measurement type.

        Raises:
            NotImplementedError: if conversion not implemented for input measurement type.

        Notes:
            [1] Returns amount if input equals output.
            [2] Assumes amount is in g or cm, not g/cm2 or cm/cm2.
        '''
        if in_type == out_type:
            return amount
        match input:
            case Measurement.LENGTH:
                return amount / weight_to_length_constant
            case Measurement.WEIGHT:
                return amount * weight_to_length_constant
            case _:
                raise NotImplementedError(
                    f'Conversion not implemented for {in_type.name}.') 
    return f

class BaseStock(Stock):
    '''
    Base class for inanimate material.
    Instantiated for stocks with no outflow,
    i.e., refractory and 'out of system' stocks.
    '''
    def __init__(self, tag: Tag, stock: float, tools: Tools,  # pylint: disable=unused-argument
                 measurement_type: Measurement = Measurement.LENGTH):
        self.tag: Tag
        self.tools: Tools = tools
        self._stock: float = stock
        self.measurement_type: Measurement = measurement_type
        self.converter = measurement_converter(tools, is_organic(self.tag))

    def update(self, increment: float, inc_type: Measurement) -> None:
        '''
        Updates stock by increment.
        '''
        self._stock += self.converter(increment, inc_type, self.measurement_type)

class Labile(BaseStock):
    '''
    Reactive organic material.
    '''
    def __init__(self, stock: float, tools: Tools, measurement_type: Measurement):
        super().__init__(tag=Tag.LABILE, stock=stock,
                         tools=tools, measurement_type=measurement_type)

    def transfer(self) -> float:
        '''
        Returns outflow [in g] from labile (to out of system).

        Notes:
            [1] This is part of eq. 5: kCl(t) in Morris & Bowden.
            [2] Labile weight is in g not g/cm2 (as it is in Morris & Bowden).
        '''
        decomp = self.tools.decomposition(self.weight)
        self.update(increment=-decomp, inc_type=Measurement.WEIGHT)
        return decomp

class Inorganic(BaseStock):
    '''
    Inorganic material.
    '''
    def __init__(self, stock: float, tools: Tools, measurement_type: Measurement):
        super().__init__(tag=Tag.LABILE, stock=stock,
                         tools=tools, measurement_type=measurement_type)

    def transfer(self) -> float:
        '''
        Returns outflow [in g] from inorganic (to out of system).

        Notes:
            [1] This is part of eq. 10: -k3(Wb)B/Rl in Morris & Bowden.
            [2] Biomass weight is in g not g/cm2 (as it is in Morris & Bowden).
        '''
        uptake = self.tools.ash_uptake(self.weight)
        self.update(increment=-uptake, inc_type=Measurement.WEIGHT)
        return uptake

Stocks = NamedTuple('ActiveStocks',[
    ('labile', Labile),
    ('refractory', BaseStock),
    ('inorganic', Inorganic)])

InactiveStocks = NamedTuple('InactiveStocks',[
    ('labile_out', BaseStock),
    ('refractory_out', BaseStock),
    ('inorganic_out', BaseStock)])

class Inanimates:
    '''
    Non-living sediments.
    '''
    def __init__(self, stocks: Stocks, tools: Tools,
                 measurement_type: Measurement):
        self._stocks = stocks
        self.measurement_type = measurement_type
        self.inactive_stocks = InactiveStocks(
            BaseStock(tag=Tag.OUT_LABILE, stock=0,
                      tools=tools, measurement_type=measurement_type),
            BaseStock(tag=Tag.OUT_REFRACTORY, stock=0,
                      tools=tools, measurement_type=measurement_type),
            BaseStock(tag=Tag.OUT_INORGANIC, stock=0,
                      tools=tools, measurement_type=measurement_type))
    @property
    def labile(self) -> Stock:
        '''
        Returns labile stock.
        '''
        return self._stocks.labile
    @property
    def refractory(self) -> Stock:
        '''
        Returns refractory stock.
        '''
        return self._stocks.refractory
    @property
    def inorganic(self) -> Stock:
        '''
        Returns inorganic stock.
        '''
        return self._stocks.inorganic
    @property
    def weight(self) -> float:
        '''
        Returns total weight of active inanimate material [in g].
        '''
        return sum((item.weight for item in self._stocks))
    @property
    def length(self) -> float:
        '''
        Returns total length of active inanimate material [in cm].
        '''
        return sum((item.length for item in self._stocks))
    @property
    def total_weight(self) -> float:
        '''
        Returns total weight of all inanimate material [in g].
        '''
        return (sum((item.weight for item in self._stocks)) +
                sum((item.weight for item in self.inactive_stocks)))
    @property
    def total_length(self) -> float:
        '''
        Returns total length of all inanimate material [in cm].
        '''
        return (sum((item.length for item in self._stocks)) +
                sum((item.length for item in self.inactive_stocks)))

    def transfer(self, inputs: Tuple[float, float, float],
                 input_type: Measurement) -> None:
        '''
        Transfers material between stocks.

        Args:
            inputs: tuple of inputs [in g] to labile, refractory and inorganic stocks.

        Note:
            The following order is imposed:
            [1] Decomposition of labile (out of system).
            [2] Uptake of refractory (out of system model).
            [3] Input of *turnover*.
        '''
        if input_type is not self.measurement_type:
            raise AttributeError(f'''The input_type: {input_type.name} must equal
                                 the measurement_type: {self.measurement_type.name}.''')
        self.inactive_stocks.labile_out.update(
            increment=self._stocks.labile.transfer(),
            inc_type=Measurement.WEIGHT)
        self.inactive_stocks.inorganic_out.update(
            increment=self._stocks.inorganic.transfer(),
            inc_type=Measurement.WEIGHT)
        self._stocks.labile.update(
            increment=inputs[0], inc_type=Measurement.WEIGHT)
        self._stocks.refractory.update(
            increment=inputs[1], inc_type=Measurement.WEIGHT)
        self._stocks.inorganic.update(
            increment=inputs[2], inc_type=Measurement.WEIGHT)

    def to_string(self, ndigits: int = 3) -> str:
        '''
        Returns string representation of inanimate object.
        '''
        msg: str = 'Inanimate(stocks=['
        for i, stock in enumerate(self._stocks):
            msg += stock.to_string(ndigits=ndigits)
            if i < len(self._stocks) - 1:
                msg += ', '
        return msg + ']'

def create_factory(constants: Constants, tools: Tools) -> Callable[[float], Inanimates]:
    '''
    Returns function that creates new inanimate object.
    '''
    organic_converter = measurement_converter(tools, organic=True)
    inorganic_converter = measurement_converter(tools, organic=False)
    @non_negative
    def f(deposition: float, in_type: Measurement, out_type: Measurement) -> Inanimates:  # pylint: disable=invalid-name
        '''
        Creates a new inanimate object.

        Args:
            deposition: deposition of sediment [in cm].
        
        Returns:
            Inanimate object with length stocks.
        '''
        # TODO: test length and weight are same as deposition.
        return Inanimates(
            stocks=Stocks(
                labile=Labile(
                    stock=organic_converter(
                        deposition * constants.fo * constants.fl, in_type, out_type),
                    tools=tools, measurement_type=out_type),
                refractory=BaseStock(
                    tag=Tag.REFRACTORY,
                    stock=organic_converter(
                        deposition * constants.fo * constants.fc, in_type, out_type),
                    tools=tools, measurement_type=out_type),
                inorganic=Inorganic(
                    stock=inorganic_converter(
                        deposition * constants.fi, in_type, out_type),
                    tools=tools, measurement_type=out_type)
            ), tools=tools, measurement_type=out_type)
    return f
