'''
This module describes a single cohert or layer of sediment, defined by a model timestep.
'''
from typing import List, Tuple, NamedTuple

from src.constants import Constants
from src.stock import Measurement
from src.live import Live
from src.live import Tools as LiveTools
from src.inanimate import Inanimates
from src.inanimate import Tools as InanimateTools
from src.utilities import enumerate_backwards

Stocks = NamedTuple('Stocks', [('live', Live), ('inanimate', Inanimates)])

class Layer:
    '''
    Accounting in a layer of sediment.
    '''
    def __init__(self, stocks: Stocks,
                 bottom_elevation: float, measurement_type: Measurement):
        self.stocks = stocks
        self.measurement_type: Measurement = measurement_type
        depth = stocks.live.length + stocks.inanimate.length
        self.elevations = (bottom_elevation + depth, bottom_elevation)

    def depth(self) -> float:
        '''
        Returns the depth of the layer.
        '''
        return self.elevations[0] - self.elevations[1]

    def transfer(self, biomass_at_top: float, deposition: float, years: float) -> None:
        '''
        Transfers biomass turnover and removal and inanimate material between layers.
        '''
        # transfer from biomass to inanimates.
        turnover, removal = self.stocks.live.transfer(
            biomass_at_top, deposition, output_type=self.measurement_type)
        transfer = map(sum, zip(tuple(x * years for x in turnover), removal))
        self.stocks.inanimate.transfer(transfer, self.measurement_type) # type: ignore

Tools = NamedTuple('Tools', [('live', LiveTools), ('inanimate', InanimateTools)])

class Core:
    '''
    Main computational element.
    '''
    def __init__(self, layers: List[Layer],
                 tools: Tools, measurement_type: Measurement):
        self.tools: Tools = tools
        self.layers: List[Layer] = layers
        self.measurement_type: Measurement = measurement_type

    @property
    def elevations(self) -> Tuple[float, float]:
        '''
        Returns the top and bottom elevations of the core.
        '''
        return (self.layers[0].elevations[0], self.layers[-1].elevations[1])

    def step_forward(self, biomass_at_surface: float, deposition: float, years: float) -> None:
        '''
        Sets the core forward in time.
        '''
        n: int = self.n_substeps( # pylint: disable=invalid-name
            biomass_at_surface, deposition, years)
        self.substep_forward(
            self.substep_biomass_delta(biomass_at_surface, n), deposition / n, years, n)

    def n_substeps(self, biomass_at_surface: float, deposition: float, years: float) -> int:
        '''
        Returns the number of substeps required to transition the core forward in time.
        '''
        return 1 # at the moment for testing.

    def substep_biomass_delta(self, biomass_at_surface: float, n_substeps: int) -> float:
        '''
        Returns change in surface biomass between timesteps divided by n substep increments.
        
        Args:
            biomass_at_surface (float): biomass at surface for new layer [in g/cm2].
            n_substeps (int): number of substeps.

        Returns:
            Difference between previous timestep biomass at surface
            and new timestep biomass at surface divided into n substep increments [in g/cm2].
        '''
        return (biomass_at_surface - self.layers[0].stocks.live.biomass.measurements.top) / n_substeps  # pylint: disable=line-too-long

    def biomass_at_top(self, layer: Layer) -> float:
        '''
        Returns biomass at top of layer.
        '''
        return layer.stocks.live.biomass.measurements.top

    def substep_forward(self, biomass_delta: float, deposition_delta: float,
                        years: float, substeps: int) -> None:
        '''
        Moves the position of the layer forward by a portion of a year,
        defined by the number of substeps and years arguments. 
        '''
        # TODO: deal with erosion case.
        portion_years = years / substeps  # pylint: disable=invalid-name
        biomass_at_surface = self.layers[0].stocks.live.biomass.measurements.top
        for _ in range(1, substeps+1):
            # @surface of top not in layers yet.
            biomass_at_surface += biomass_delta
            # loop from top layer down to bottom layer.
            for _, layer in enumerate_backwards(self.layers):
                # TODO: make sure this works if layer is below root depth.
                output_weight = True if self.measurement_type is Measurement.WEIGHT else False
                biomass_at_top = self.tools.live.distribution(biomass_at_surface,
                                                              deposition_delta, output_weight)
                layer.transfer(biomass_at_top, deposition_delta, portion_years)
            # add top layer after computing turnover, removal and redistribution of biomass.
            self.layers.append(self.layer_factory(biomass_at_surface, deposition_delta))
        if substeps > 1:
            # biomass at surface has been incrementing it should be summed to the correct value.
            top_layer = self.layer_factory(biomass_at_surface, deposition_delta * substeps)
            # delete the temporary layers.
            del self.layers[-substeps:]
            # add summed layer to top of core.
            self.layers.append(top_layer)

    def layer_factory(self, biomass_at_surface: float, deposition: float) -> Layer:
        '''
        Creates a new layer.
        '''
        inanimate = self.tools.inanimate.factory(deposition)
        live = self.tools.live.factory(biomass_at_surface, (0.0, deposition))
        # top moves up by deposition, old top is bottom of new top layer.
        elevations = (self.elevations[0] + deposition, self.elevations[0])
        return Layer(stocks=Stocks(live=live, inanimate=inanimate),
                     bottom_elevation=elevations[1], measurement_type=self.measurement_type)

def factory(constants: Constants, measurement_type: Measurement) -> Core:
    '''
    Creates a new core.
    '''
    depth = constants.du - constants.db
    tools = Tools(live=LiveTools(constants=constants),
                  inanimate=InanimateTools(constants=constants))
    def first_layer(biomass_at_surface: float, deposition: float) -> Layer:
        '''
        Creates first (forever bottom) layer.
        '''
        inanimate = tools.inanimate.factory(deposition)
        live = tools.live.factory(biomass_at_surface, (0.0, deposition))
        return Layer(stocks=Stocks(live=live, inanimate=inanimate),
                     bottom_elevation=constants.db, measurement_type=measurement_type)
    return Core(layers=[first_layer(constants.ro, depth)],
                tools=tools, measurement_type=measurement_type)

# @dataclass
# class Layer:
#     '''
#     A cohert in the Morris and Bowden model. A band of sediment associated with a single timestep.
#     '''
#     top: float
#     bottom: float
#     stocks: Dict[stock.Tag, stock.Stock]

#     def to_string(self) -> List[str]:
#         '''Summarizes information about layer.'''
#         return [f'top: {round(self.top, 0)}, bottom: {round(self.bottom, 0)}'] + \
#         [f'{k.name.lower()}{v}' for k,v in self.stocks.items()]

#     def erosion(self, erosion: float, constants: Constants, is_bottom_layer: bool = False) -> float:
#         '''
#         Removes sediment from top of layer, returns excess erosion.

#         Notes:
#             [1] bottom layer maintains fixed initial depth, defined in du, db constants.
#             [2] completely eroded layers are given zero depth but not removed.
#         '''
#         if is_bottom_layer:
#             self.top += erosion
#             self.bottom = self.top - (constants.du - constants.db)
#             return 0.0
#         if (excess_erosion := erosion - (self.bottom - self.top)) < 0:
#             # layer is completely eroded.
#             self.bottom += excess_erosion
#             self.top = self.bottom
#             return excess_erosion
#         self.top += erosion
#         return 0.0

# def factory(constants: Constants, top: float, bottom: float, biomass: float) -> Layer:
#     '''
#     Creates a new layer.
#     '''
#     return Layer(top=top, bottom=bottom,
#                  stocks=stock.factory(constants=constants, deposition=top-bottom, biomass=biomass))
