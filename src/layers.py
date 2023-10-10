'''
This module describes sediment cores which are composed of layers.
'''
from typing import List

import src.layer as layer
from src.stocks import Tag
from src.constants import MORRIS_CONSTANTS, Constants

class Layers:
    '''
    A layered group of sediment bands, 
    i.e. List[Layer] at a specific location with a constant surface area.
    '''

    def __init__(self, constants_filepath: str = MORRIS_CONSTANTS):
        self._constants = Constants(constants_filepath)
        self._surface_area = self._constants.sa
        self._layers = [
            layer.factory(constants=self.constants,
                          top=self.constants.du, bottom=self.constants.db,
                          biomass=self.constants.ro)]

    @property
    def surface_area(self) -> float:
        '''Read only property for surface area.'''
        return self._surface_area

    @property
    def layers(self) -> List[layer.Layer]:
        '''Read only property for list of layers.'''
        return self._layers

    @property
    def constants(self) -> Constants:
        '''Read only property for constants throughout layers and stocks.'''
        return self._constants

    @property
    def depth(self) -> float:
        '''Returns the summed depth of all layers in the sediment core.'''
        return sum((layer.top - layer.bottom) for layer in self.layers)

    # def stocks_depths(self) -> Dict[Tag, float]:
    #     '''
    #     Returns length of stocks in all layers.
    #     '''
    #     stocks = {tag.name:0.0 for tag in Tag}
    #     for cohert in self.layers:
    #         for k, v in cohert.stocks.items():
    #             stocks[k] += v.length
    #     return stocks

    def stock_depth(self, tag: Tag) -> float:
        '''
        Retuns length of specified stock across all layers.
        '''
        return sum(layer.stocks[tag].length for layer in self.layers)

    def biomass_weight(self) -> float:
        '''
        Similiar to stock_depth function, 
        but for weight and optimized for biomass 
        since it only present to constant depth of constants.rd.
        '''
        #TODO: check that biomass not found below rd.
        return sum(layer.stocks[Tag.BIOMASS].weight
            for layer in self.layers if layer.top < self.constants.rd)

    def update(self, deposition: float, biomass: float) -> None:
        '''
        Moves model forward one timestep by adding a new layer and updating existing layers.
        
        Arguments:
            biomass [float]: biomass at marsh surface [in g/cm].
            deposition [float]: negative values are erosion [in cm].

        Assumptions:
            [1] negative deposition = erosion.
            [2] reduction in biomass at surface = mortality.
            [3] turnover only occurs when mortality = 0.

        Process:
            [1] Erosion, return biomass[t-1] for litter.
            [1] Mortality, if no erosion return biomass[t-1] for litter.
            [2] Turnover  
        '''
        if deposition < 0:
            self.erosion(erosion=deposition, biomass=biomass)
        else:
            new_bottom = self.layers[len(self.layers)-1].top
            self.layers.append(layer.factory(constants=self.constants,
                                             bottom=new_bottom, top=new_bottom+deposition,
                                             biomass=biomass))

    # def litter_weight(self, biomass: float) -> float:
    #     '''
    #     Computes if mortality has occured and the weight of litter to be added to the top layer.
    #     '''
    #     mortality_biomass_weight = self.biomass_weight() - biomass_weight(ro=biomass, du=0, db=self.constants.rd)
    #     return 0 if mortality_biomass_weight < 0 else mortality_biomass_weight * (1 / self.constants.sv_to_ro)

    # def add_biomass(self, biomass: float = 0.0) -> None:
    #     '''Adds biomass to layers if biomass exceeds biomass from previous timestep.'''
    #     top: float = 0                  # starts as marsh surface.
    #     final_depth = self.constants.rd # maximum root depth [in cm].
    #     def recursion(i: int, biomass: float, top: float):
    #         '''Loops over layers in downward direction until maximum root depth is reached.'''
    #         if top < final_depth:
    #             bottom = min(final_depth, top + (self.layers[i].top - self.layers[i].bottom))

    def erosion(self, erosion: float, biomass: float) -> None:
        '''
        Adds new zero depth layer and recursively erods subsequent bed layers. 
        Bottom layer maintains fixed depth. 
        '''
        # litter_weight = litter_weight(biomass)
        def recursion(i: int, erosion: float) -> None:
            is_bottom_layer = True if i == 0 else False
            excess_erosion = self.layers[i].erosion(erosion, self.constants, is_bottom_layer)
            if excess_erosion < 0:
                # layer i erodes completely and process continues on layer i-1
                recursion(i=i-1, erosion=excess_erosion)
        # first, erode lower layers to find top/bottom elevation of new layer
        recursion(i=len(self.layers)-1, erosion=erosion)
        # add new zero depth layer on top previous layers
        new_top = self.layers[len(self.layers)-1].top
        #TODO: make sure the mass is right on this new 0 depth layer.
        self.layers.append(layer.factory(self.constants, new_top, new_top, biomass))

    def to_string(self) -> List[str]:
        '''Summarizes information about layers.'''
        msg = [f'layers(n={len(self.layers)})']
        for i in reversed(range(len(self.layers))):
            msg.append('-' * len(msg[0]))
            msg.append(f'layer {i}: ' + ', '.join(self.layers[i].to_string()))
        msg.append('-' * len(msg[0]))
        return msg

def factory(constants_filepath: str = MORRIS_CONSTANTS) -> Layers:
    '''Constructs a new sediment core comprised of a single bottom layer.'''
    return Layers(constants_filepath=constants_filepath)
