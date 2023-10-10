'''
Describes layers of sediment and their associated stocks.
'''
from dataclasses import dataclass
from typing import List, Tuple, NamedTuple

from src.stock import Measurement
from src.constants import Constants
from src.live import BiomassTools, Biomass
from src.inanimate import InanimateTools, Inanimate
from src.utilities import elevations_to_depth, enumerate_backwards
from src.validators import (
    positive_attribute, non_negative_attribute,
    ascending_non_negative_attribute, descending_attribute)

@dataclass
class Layer:
    '''
    A layer of sediment
    '''
    biomass: Biomass
    '''Live below ground biomass.'''
    inanimate: Inanimate  # state variable
    '''Inert organic material.'''
    depths: Tuple[float, float]
    '''Depth of top and bottom of layer from surface [in cm].'''
    elevations: Tuple[float, float]
    '''Elevations of top and bottom of layer [in cm].'''
    measurements: Measurement = Measurement.LENGTH

    def __post_init__(self):
        descending_attribute(key='elevations', value=self.elevations)
        ascending_non_negative_attribute(key='depths', value=self.depths)

    def depth(self) -> float:
        '''
        Returns depth of layer [in cm].
        '''
        return elevations_to_depth(elevations=self.elevations)

    def transition(self, depth_delta: float, years: float = 1.0) -> None:
        '''
        Turns over biomass and inanimate stocks.

        Note:
            [1] Biomass does not change. 
            [2] Implicity, new live material instantaneously replaces turned over material.
            [3] Mutates inanimate state variable.
        '''
        turnover = (x * years for x in self.biomass.turnover(output=self.measurements))
        # note: the removal layer has losses mass below but this is not yet recorded.
        removal = self.biomass.removal(depth_delta=depth_delta * years, output=self.measurements)


        


        self.inanimate = self.inanimate.decompose(biomass=self.biomass,
                                                  depth_delta=depth_delta, years=years)

    def to_string(self) -> str:
        '''
        Returns string representation of layer.
        '''
        return f'''Layer(elevations={self.elevations}, {self.biomass.to_string(False)}, {self.inanimate.to_string()})'''  # pylint: disable=line-too-long

Tools = NamedTuple('Tools', [('biomass', BiomassTools), ('inanimate', InanimateTools)])

def first_layer(constants: Constants, measurements: Measurement) -> Layer:
    '''
    Initializes a bottom layer of sediment.
    '''
    elevations = (constants.du, constants.db)
    if (depth:= elevations_to_depth(elevations=elevations)) < constants.rd:
        raise AttributeError(f'''Initial layer depth: {depth} = ({constants.du} - {constants.db})
                              must be greater or equal to maximum root depth: {constants.rd}.''')
    tools = Tools(biomass=BiomassTools(constants=constants),
                  inanimate=InanimateTools(constants=constants))
    biomass = tools.biomass.factory(biomass_at_top=constants.ro, depths=(0.0, depth))
    return Layer(biomass=biomass,
                 inanimate=tools.inanimate.factory(deposition=depth-biomass.length),
                 depths=(0.0, depth), elevations=(constants.du, constants.db),
                 measurements=measurements)

@dataclass
class Core:
    '''
    List of layers with position corresponding to timestep.
    '''
    tools: Tools
    layers: List[Layer]
    measurements: Measurement = Measurement.LENGTH

    def is_live(self, layer: Layer) -> bool:
        '''
        Returns true if layer is in root zone.
        '''
        return layer.depths[0] < self.tools.biomass.max_root_depth

    def total_biomass(self) -> float:
        '''
        Returns total biomass in core.
        '''
        total: float = 0.0
        for _, layer in enumerate_backwards(self.layers):
            if self.is_live(layer):
                if self.measurements is Measurement.WEIGHT:
                    total += layer.biomass.weight
                else:
                    total += layer.biomass.length
            else:
                break
        return total

    def step_foward(self, biomass_at_top: float, deposition: float=0.0, years: float = 1.0) -> None:
        '''
        Steps core forward in time by one timestep.
        '''
        positive_attribute('years', years)
        non_negative_attribute('biomass_at_top', biomass_at_top)
        # TODO: compute number of substeps to use based on constant and rate of change in biomass, and deposition.  # pylint: disable=line-too-long
        self.substep(biomass_at_top=biomass_at_top, deposition=deposition, years=years)

    def substep(self, biomass_at_top: float, deposition: float = 0.0, years: float = 1.0) -> None:
        '''
        Substep of step_forward function.
        '''
        self.transition(depth_delta=max(0.0, deposition), years=years)
        elevations = (x + deposition for x in self.layers[-1].elevations)
        if deposition < 0:
            # erosion
            pass
        self.layers.append(self.create_layer(biomass_at_top,
                                             depth=deposition, elevations=elevations))  # type: ignore
        # crete new layer and append it. (keep track of its N-1 index value) (make create function).
        # if its new bottom is below rd then remove rd to bottom biomass (convert function)
        # convert function might just take biomass and convert to labile, refactory - or compute biomass then do that.
        # if its old top was below rd should be able to ignore but maybe convert all biomass to be safe.
        for i, layer in enumerate_backwards(self.layers):
            if i < len(self.layers)-1:
                layer.transition(depth_delta=deposition, years=years)
        return

    def create_layer(self, biomass_at_top: float,
                     depth:float, elevations: Tuple[float, float]) -> Layer:
        '''
        Creates a new layer.
        '''
        # pylint: disable=line-too-long
        return Layer(biomass=self.tools.biomass.factory(biomass_at_top=biomass_at_top,depths=(0.0, depth)),
                     inanimate=self.tools.inanimate.factory(deposition=depth), depths=(0.0, depth), elevations=elevations)

    def transition(self, depth_delta: float, years: float=1.0) -> None:
        '''
        Conversions between biomass and inanimate materials.
        '''
        # TODO: at the moment this is pointless below rd.
        for _, layer in enumerate_backwards(self.layers):
            layer.transition(depth_delta=depth_delta, years=years)

    def to_string(self) -> str:
        '''
        Returns string representation of core.
        '''
        msg: str = 'Core(layers=['
        for i, layer in enumerate(self.layers):
            msg += layer.to_string()
            if i < len(self.layers) - 1:
                msg += ', '
        return msg + '])'

def factory(constants: Constants=Constants(), measurements: Measurement=Measurement.LENGTH) -> Core:
    '''
    Creates a new core, with a single bottom layer.
    '''
    tools = Tools(biomass=BiomassTools(constants=constants),
                  inanimate=InanimateTools(constants=constants))
    return Core(tools=tools, layers=[first_layer(constants=constants, measurements=measurements)], measurements=measurements)


# @dataclass(frozen=True)
# class Layer:
#     '''
#     A layer of sediment.
#     '''
#     elevations: Tuple[float, float]
#     '''Elevations of top and bottom of layer.'''
#     stocks: Tuple[Stock, ...]
#     '''Stocks associated with layer.'''

#     def depth(self) -> float:
#         '''
#         Returns depth of layer.
#         '''
#         return elevations_to_depth(elevations=self.elevations)

#     def erode(self, deposition: float) -> None:
#         '''
#         Erodes layer by negative deposition.
#         '''
#         # 0 depth top layer (biomass will be added here) and will be same value at top of next layer.
#         # erode other previous layer, remove biomass
#         depth = elevations_to_depth(elevations=self.elevations)


# def first_layer(constants: Constants) -> Layer:
#     '''
#     Initializes a bottom layer of sediment.
#     '''
#     return Layer(elevations=(constants.du, constants.rd),
#                  stocks=(Functions(constants=constants).factory(biomass_at_top=constants.ro, depths=(0.0, constants.db-constants.du)),))  # type: ignore

# class Core:
#     '''
#     List of layers with position corresponding to timestep.

#     In each timestep, a new layer is added to the top of the sediment core.

#     Note: the sequencing of actions matters here!
#         [1] Turnover: assumption this happens before erosion.
#         [2] Deposition: is handled next. (<0: erosion, >0: deposition)
#         [3] Biomass: recompute based on changed depth.    
#     '''
#     def __init__(self, constants=Constants()):
#         self.surface_area: float = constants.sa
#         self.max_root_depth: float = constants.rd # here?
#         self.layers: List[Layer] = [first_layer(constants)]
#         self._biomass_utilities = Functions(constants=constants)

#     def step_foward(self, biomass_at_top: float, deposition: float) -> None:
#         '''
#         Steps core forward in time by one timestep.
#         '''
#         # turnover
#         if deposition < 0:
#             self.erosion(deposition=deposition)

#     def erosion(self, deposition: float) -> None:
#         '''
#         Erodes starting at top layer of core.
#         '''
#         # 0 depth top layer (biomass will be added here) and will be same value at top of next layer.
#         # erode other previous layer, remove biomass
#         depth = abs(deposition)
#         for _, layer in enumerate(self.layers):
#             layer_depth = elevations_to_depth(elevations=layer.elevations)
#             if depth < layer_depth:
#                 # bottom layer of change
#                 pass
#             #depth -= elevations_to_depth(elevations=layer.elevations)

# # initializers = {
# #     Tag.BIOMASS: biomass_init,
# # }

# # def stocks_factory(constants: Constants, deposition: float, biomass: float) -> Tuple[Stock]:
# #     '''
# #     Creates stocks associated this deposition of new layer.
# #     '''

# # class Layer:
# #     '''
# #     A cohert in the Morris and Bowden model. 
# #     A band of sediment associated with a single timestep.
# #     '''
# #     top: float
# #     '''Elevation of top of layer.'''
# #     bottom: float
# #     '''Elevation of bottom of layer.'''
# #     stocks: Tuple[Stock]
# #     '''Stocks associated with layer.'''

# # def layer_init(constants: Constants, top: float, bottom: float, biomass: float) -> Layer:
# #     '''
# #     Creates a new layer.
# #     Can only be created thought deposition.
# #     '''
# #     return Layer(top=top, bottom=bottom,
# #                  stocks=stock.factory(constants=constants, deposition=top-bottom, biomass=biomass))

# # class Layers:
# #     '''Tuple of layers with position corresponding to timestep'''
# #     layers: Tuple[Layer]
