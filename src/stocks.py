'''
This module defines the stocks that are tracked by each layer in the netherland model.

Stocks are held by layers in a Dict[Tag, Stock] dictionary.
'''
from enum import Enum, auto
from dataclasses import dataclass
from typing import Dict, Optional, Callable, Self

import numpy as np

from src.constants import Constants

class Tag(Enum):
    '''
    A enumerated list of the stock variables held within each layer.

    Note: Nitrogen and Phosphorus are not included in the current version.
    '''
    BIOMASS = auto(),
    '''Live below ground biomass.'''
    LABILE = auto(),
    '''Reactive inert organic material.'''
    REFRACTORY = auto(),
    '''Unreactive inert organic material (no outflow from this stock).'''
    INORGANIC = auto()
    '''Category for inorganic sediment.'''

class Category(set, Enum):
    '''
    The stock tags defined above can be categorized as organic or inorganic.

        ex: if Tag.BIOMASS in Category.ORGANIC:
                ...
    '''
    ORGANIC = {Tag.BIOMASS, Tag.LABILE, Tag.REFRACTORY}
    INORGANIC = {Tag.INORGANIC}

@dataclass
class Stock:
    '''
    An interface for defining stock variables.
    '''
    length: float
    weight: float
    _update_fx: Callable[[Self, float, Optional[float]], float]

    def update(self, deposition: float, biomass: Optional[float]) -> float:
        '''
        Updates weight and length state variables through turnover, decomposition, and erosion.
        
            [1] Erosion: in every timestep the conversion of biomass and accretion of ash 
                change portion organic, labile, etc., so this cannot be computed using constants. 
        '''
        #TODO: test updates
        return self._update_fx(self, deposition, biomass)

    def __str__(self):
        return f'(weight={round(self.weight,2)}, length:{round(self.length,2)})'

@dataclass
class Biomass(Stock):
    '''
    Biomass stock variable. Implements Stock interface.
    '''
    depth: float
    weight: float
    length: float
    biomass: float
    _update_fx: Callable[[Self, float, Optional[float]], float]

def biomass_init(constants: Constants, deposition: float, biomass: float) -> Stock:
    '''
    Constructs new biomass object with access to constants.
    '''
    def weight_at_depth(biomass: float = 1, depth: float = 0) -> float:
        return biomass * pow(np.e, -constants.k1*depth)
    def weight_fx(biomass: float, depth: float) -> float:
        '''
        Computes weight of biomass between top and bottom [in g].

        Arguments:
            biomass [float]: biomass at surface [in g/cm].
            depth [float]: depth over which biomass in layer is computed [in cm].    
        
        Returns:
            [float]: live below ground biomass [in g].

        Notes: 
            [1] Eq. 4 in Morris & Bowden.
        '''
        #TODO: Solve for Rz where z is depth.
        #TODO: Check weight and length fx
        # ex. [1] length_fx(1, 0, 4) = length_fx(1, 0, 2) + length(R_2, 2, 4)
        return (biomass * weight_at_depth(depth=depth) - biomass) / -constants.k1 * constants.sa
    def length_fx(biomass: float, depth: float) -> float:
        return weight_fx(biomass, depth) * constants.g_to_cm(grams=1, organic=True)
    def update_fx(stock: Biomass, deposition: float, biomass: None|float) -> float:
        '''biomass needs to come from caller.'''
        if deposition > 0:
            raise AttributeError('Positive deposition for update of biomass material is invalid')
        #erosion is a length, compute loss using t-1 biomass.
        eroded = length_fx(stock.biomass, depth=abs(deposition))
        #biomass that was NOT eroded times turnover constant.
        turnover = (stock.biomass - eroded) * constants.k2
        #new biomass (growing from above) is independent of the erosion and turnover.
        stock.biomass = stock.biomass if biomass is None else biomass
        #compute biomass over uneroded depth
        stock.depth += deposition # subtraction (deposition < 0)
        stock.weight = weight_fx(stock.biomass, stock.depth)
        stock.length = stock.weight * constants.g_to_cm(grams=1, organic=True)
        return turnover
    if deposition < 0:
        raise AttributeError('Negative deposition for creation of new biomass layer is invalid.')
    return Biomass(depth=deposition,
                   weight=weight_fx(biomass=biomass, depth=deposition),
                   length=length_fx(biomass=biomass, depth=deposition),
                   biomass=biomass, _update_fx=update_fx)

def labile_init(constants: Constants, deposition: float) -> Stock:
    '''
    Constructs new labile stock object with access to constants through update_fx closure.
    '''
    #TODO: test closures.
    def length_fx(depth: float) -> float:
        return depth * constants.fo * constants.fl
    def weight_fx(depth: float) -> float:
        return length_fx(depth=depth) * constants.cm_to_g(cm=1, organic=True)
    def update_fx(stock: Stock, deposition: float, biomass=None) -> float:
        if deposition > 0:
            raise AttributeError('Positive deposition for update of labile material is invalid.')
        turnover = stock.length * constants.k
        stock.length += length_fx(depth=deposition)
        stock.length -= turnover
        stock.weight = weight_fx(depth=stock.length)
        return turnover # without mineralization does this evaporate.
    if deposition < 0:
        raise AttributeError('Negative deposition of for creation of new labile layer is invalid.')
    return Stock(length=length_fx(depth=deposition), weight=weight_fx(depth=deposition),
                 _update_fx=update_fx)

def refractory_init(constants: Constants, deposition: float) -> Stock:
    '''
    Constructs new labile stock object with access to constants through update_fx closure.
    '''
    def length_fx(depth: float) -> float:
        return depth * constants.fo * constants.fc
    def weight_fx(depth: float) -> float:
        return length_fx(depth=depth) * constants.cm_to_g(cm=1, organic=True)
    def update_fx(stock: Stock, deposition: float, biomass=None) -> float:
        if deposition > 0:
            raise AttributeError(
                'Positive deposition for update of refractory material is invalid.')
        stock.length += length_fx(depth=deposition)
        stock.weight = weight_fx(stock.length)
        return 0.0 # no outflow from refractory pool.
    if deposition < 0:
        raise AttributeError(
            'Negative deposition of for creation of new refractory layer is invalid.')
    return Stock(length=length_fx(depth=deposition), weight=weight_fx(depth=deposition),
                 _update_fx=update_fx)

def inorganic_init(constants: Constants, deposition: float) -> Stock:
    '''
    Constructs new inorganic stock object with access to constants through update_fx closue.
    '''
    def length_fx(depth: float) -> float:
        return depth * constants.fi
    def weight_fx(depth: float) -> float:
        return length_fx(depth=depth) * constants.cm_to_g(cm=1, organic=False)
    def update_fx(stock: Stock, deposition: float, biomass=None) -> float:
        stock.length += length_fx(depth=deposition)
        stock.weight = weight_fx(stock.length)
        return 0.0 # no outflow from inorganic pool.
    if deposition < 0:
        raise AttributeError('Negative deposition of for creation of new labile layer is invalid.')
    return Stock(length=length_fx(depth=deposition), weight=weight_fx(depth=deposition),
                 _update_fx=update_fx)

initializers = {
    Tag.BIOMASS: biomass_init,
    Tag.LABILE: labile_init,
    Tag.REFRACTORY: refractory_init,
    Tag.INORGANIC: inorganic_init
}

def factory(constants: Constants, deposition: float, biomass: float) -> Dict[Tag, Stock]:
    '''
    Constructs a dictionary of new stocks.
    '''
    return {tag: initializers[tag](constants, deposition, biomass)
            if tag == Tag.BIOMASS else initializers[tag](constants, deposition) for tag in Tag}
