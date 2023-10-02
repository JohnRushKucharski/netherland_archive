'''
Manages the import of constants from an input .toml file.
'''
#TODO: the default values need checking in the .toml file.
# Example: Constants.g_to_cm3(grams=1, organic=False) default bo converts 1 g to 10cm3 and with with sa=1, g_to_cm() to 10 cm # pylint: disable=line-too-long
# for organic material defined in Morris and Bowden (e.g. organic=True) the conversion is even more extreme. # pylint: disable=line-too-long

import tomllib
from pathlib import Path
from dataclasses import dataclass, field

MORRIS_CONSTANTS: str = str(Path(__file__).parent.parent.
                            joinpath('data').joinpath('morris_constants.toml'))

@dataclass
class Constants:
    '''
    Class for constructing required constants give a .toml file path.
    '''
    # pylint: disable=invalid-name
    file_path: str = MORRIS_CONSTANTS
    b: float = field(init=False)
    '''
    Factor decribing net transport of litter over cell [dmls].
        =0: no retention of litter.
        <1: net outflux.
        =1: no transport or influx = outflux.
        >1: net influx.
    '''
    sa: float = field(init=False)
    '''Surface area [in cm2].'''
    du: float = field(init=False)
    '''Initial top elevation [in cm].'''
    db: float = field(init=False)
    '''Initial bottom elevation [in cm].'''
    bo: float = field(init=False)
    '''Bulk density of organic matter [in g/cm3].'''
    bi: float = field(init=False)
    '''Bulk density of inoganic matter [in g/cm3].'''
    fo: float = field(init=False)
    '''Fraction of sediment that is organic [dmls].'''
    fi: float = field(init=False)
    '''Fraction of sediment that is inorganic [dmls].'''
    k: float = field(init=False)
    '''Specific decay constant for labile organic material [in 1/yr].'''
    fc: float = field(init=False)
    '''Fraction of sediment that is refractory [dmls].'''
    fl: float = field(init=False)
    '''Fraction of sediment that is labile [dmls].'''
    ro: float = field(init=False)
    '''Initial live below ground biomass at surface 
    (assumed constant across surface area) [in g/cm2].'''
    rd: float = field(init=False)
    '''Maximum root depth [in cm].'''
    k1: float = field(init=False)
    '''Distribution parameter for below ground biomass a function of depth 
    (assumed constant across surface area) [in 1/cm].'''
    k2: float = field(init=False)
    '''Turnover rate of below ground biomass (a portion) [in 1/yr].'''
    k3: float = field(init=False)
    '''Portion of plant matter that is inorganic ash [dmls].'''
    sv_to_ro: float = field(init=False)
    '''Conversion factor for converting stem volume (from NBSDynamics) 
    into live biomass concentration at sediment surface (ro) [dmls].'''
    wa_to_rl: float = field(init=False)
    '''Ratio of above ground biomass production to below ground biomass [dmls].'''

    def __post_init__(self):
        with open(self.file_path, mode='rb') as file:
            data = tomllib.load(file)
            self.b = data['core']['b']
            self.sa = data['core']['sa']
            self.du = data['layer']['du']
            self.db = data['layer']['db']
            self.bo = data['stocks']['bo']
            self.bi = data['stocks']['bi']
            self.fo = data['stocks']['fo']
            self.fi = 1 - self.fo
            self.k = data['stocks']['k']
            self.fc = data['stocks']['fc']
            self.fl = 1 - self.fc
            self.ro = data['stocks']['ro']
            self.rd = data['stocks']['rd']
            self.k1 = data['stocks']['k1']
            self.k2 = data['stocks']['k2']
            self.k3 = data['stocks']['k3']
            self.sv_to_ro = data['stocks']['sv_to_ro']
            self.wa_to_rl = data['stocks']['wa_to_rl']
        # pylint: disable=line-too-long
        if self.sa <= 0:
            raise ValueError(f'sa: {self.sa} (surface area [in cm2]) must be greater than 0.')
        if self.du <= self.db:
            raise ValueError(f'du: {self.du} (top elevation [in cm]) must be greater than db: {self.db} (bottom elevation [in cm]).')
        if self.bo <= 0:
            raise ValueError(f'bo: {self.bo} (bulk density of organic matter [in g/cm3]) must be greater than 0.')
        if self.bi <= 0:
            raise ValueError(f'bi: {self.bi} (bulk density of inorganic matter [in g/cm3]) must be greater than 0.')
        if self.fo < 0 or self.fo > 1:
            raise ValueError(f'fo: {self.fo} (fraction of sediment that is organic [dmls]) must be greater than 0.')
        if self.fi < 0 or self.fi > 1:
            raise ValueError(f'fi: {self.fi} (fraction of sediment that is inorganic [dmls]) must be greater than 0.')
        if self.fo + self.fi != 1:
            raise ValueError(f'fo: {self.fo} (fraction of sediment that is organic [dmls]) plus fi: {self.fi} (fraction of sediment that is inorganic [dmls]) must equal 1.')
        if self.k <= 0:
            raise ValueError(f'k: {self.k} (specific decay constant for labile organic material [in 1/yr]) must be greater than 0.')
        if self.fc < 0 or self.fc > 1:
            raise ValueError(f'fc: {self.fc} (fraction of sediment that is refractory [dmls]) must be greater than 0.')
        if self.fl < 0 or self.fl > 1:
            raise ValueError(f'fl: {self.fl} (fraction of sediment that is labile [dmls]) must be greater than 0.')
        if self.fc + self.fl != 1:
            raise ValueError(f'fc: {self.fc} (fraction of sediment that is refractory [dmls]) plus fl: {self.fl} (fraction of sediment that is labile [dmls]) must equal 1.')
        if self.ro < 0:
            raise ValueError(f'ro: {self.ro} (initial live below ground biomass at surface [in g/cm2]) must be greater than or equal to 0.')
        if self.rd <= 0:
            raise ValueError(f'rd: {self.rd} (maximum root depth [in cm]) must be greater than 0.')
        if (self.du - self.db) < self.rd:
            raise ValueError(f'initial layer depth: {self.du - self.db} (du: {self.du} - db: {self.db}) must be greater than or equal to the maximum root depth: {self.rd}.')
        if self.k1 <= 0 or self.k1 >= 1:
            raise ValueError(f'k1: {self.k1} (distribution parameter for below ground biomass a function of depth [in 1/cm]) must be greater than 0 and less than 1.')
        if self.k2 <= 0:
            raise ValueError(f'k2: {self.k2} (turnover rate of below ground biomass [in 1/yr]) must be greater than 0.')
        if self.k3 < 0 or self.k3 > 1:
            raise ValueError(f'k3: {self.k3} (portion of plant matter that is inorganic ash [dmls]) must be greater than 0 and less than 1.')
        if self.sv_to_ro <= 0:
            raise ValueError(f'sv_to_ro: {self.sv_to_ro} (conversion factor for converting stem volume (from NBSDynamics) into live biomass concentration at sediment surface (ro) [dmls]) must be greater than 0.')
        if self.wa_to_rl <= 0:
            raise ValueError(f'wa_to_rl: {self.wa_to_rl} (ratio of above ground biomass production to below ground biomass [dmls]) must be greater than 0.')

    def g_to_cm3(self, grams: float = 1, organic=True) -> float:
        '''
        Converts weight [in g] to volume [in cm3] based on bulk density constant [in g/cm3].
        '''
        return grams * (1 / self.bo) if organic else grams * (1 / self.bi)

    def g_to_cm(self, grams: float = 1, organic=True) -> float:
        '''
        Converts weight [in g] to length [in cm] based on bulk density [in g/cm3] 
        and surface area [in cm2] constants.
        '''
        return self.g_to_cm3(grams, organic) * self.sa

    def cm_to_g(self, cm: float = 1, organic=True) -> float:
        '''
        Converts length [in cm] to weight [in g]
        based on bulk density [in g/cm3] and surface area [in cm2] constants.
        '''
        return cm * (1/self.g_to_cm(grams=1, organic=organic))
