'''
An interface for stocks of material in a layer.
'''

from enum import Enum
from typing import Protocol, Callable

class Measurement(Enum):
    '''Enum for stock mesurement types.'''
    LENGTH = 0  # cm
    WEIGHT = 1  # g

class Tag(Enum):
    '''Enum for stock types.'''
    BIOMASS = 'biomass'
    OUT_BIOMASS = 'biomass out'
    LABILE = 'labile'
    OUT_LABILE = 'labile out'
    REFRACTORY = 'refractory'
    OUT_REFRACTORY = 'refractory out'
    INORGANIC = 'inorganic'
    OUT_INORGANIC = 'inorganic out'

def is_organic(tag: Tag) -> bool:
    '''
    Returns the category of a stock tag.
    '''
    match tag:
        case Tag.BIOMASS|Tag.LABILE|Tag.REFRACTORY|Tag.OUT_LABILE:
            return True
        case Tag.INORGANIC|Tag.OUT_INORGANIC:
            return False
        case _:
            raise ValueError(f'Unknown stock tag: {tag}')

def is_inlayer(tag: Tag) -> bool:
    '''
    Returns whether a stock tag is part of the layer current stock.
    '''
    match tag:
        case Tag.BIOMASS|Tag.LABILE|Tag.REFRACTORY|Tag.INORGANIC:
            return True
        case Tag.OUT_LABILE|Tag.OUT_INORGANIC:
            return False
        case _:
            raise ValueError(f'Unknown stock tag: {tag}')

class Stock(Protocol):
    '''
    An interface for stocks of material in a layer.
    '''
    tag: Tag
    '''The type of stock.'''
    measurement_type: Measurement
    '''The type of measurement: WEIGHT OR LENGTH.'''
    converter: Callable[[float, Measurement, Measurement], float]
    '''A function to convert between measurement types.'''
    _stock: float
    '''
    Private use weight or length to access.
    Amount [in units of measurement type].
    '''

    @property
    def weight(self) -> float:
        '''
        Returns weight [in g].
        '''
        return self.converter(
            amount=self._stock,  # type: ignore
            in_type=self.measurement_type, out_type=Measurement.WEIGHT)
    @property
    def length(self) -> float:
        '''
        Returns length [in cm].
        '''
        return self.converter(
            amount=self._stock,  # type: ignore
            in_type=self.measurement_type, out_type=Measurement.LENGTH)

    def to_string(self, ndigits: int = 3) -> str:
        '''
        Returns a string representation of the stock.
        '''
        return f'{self.tag.name}({self.measurement_type.name.lower()}: {self._stock:.{ndigits}f})'
