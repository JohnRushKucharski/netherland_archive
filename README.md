# netherland

Keeps track salt marsh elevation in dynamic simulations. 

The marsh elevation in this model is a function of: (1) exogenous deposition and erosion of organic and inorganic sediment, (2) below ground biomass production, (3) decomposition. 

It mostly follows the SEMIDEC model described in:
> Morris, J. T., & Bowden, W. B. (1986). A Mechanistic, Numerical Model of Sedimentation, Mineralization, and Decomposition for Marsh Sediments. *Soil Science Society of America Journal*, 50(1), 96-105. https://doi.org/10.2136/sssaj1986.03615995005000010019x

The following illustration diagrams the processes that control the flow of sediment in and out of stock variables that are tracked by the model.

![alt text](https://github.com/JohnRushKucharski/netherland/blob/main/diagram.jpg?raw=true)

## Assumptions

1. Below ground biomass is entirely organic (i.e., labile or refractory).
    **Implication**: no inorganic material is created by turnover or removal, which convert biomass to inanimate organic material. This is an odd assumption given eq. 9, 10 in Morris & Boweden, which arises from eq. 5, 6 in Morris & Bowden.
        - Maybe this could be set in the constants.toml (to assume or  not assume inorganic)
2. Below ground biomass does *not* grow below the "max" root zone depth.
    **Implication**: during periods of deposition biomass below this depth is subject to removal (i.e., conversion to inanimate organic material).
3. Biomass *always* extends down to the maximum root depth.
    **Implication**: this is an implicit assumption introduced by eq. 4 in Morris & Bowden. This is less concerning in an *established* marsh model, but may cause errors in more dynamic environments (i.e., where biomass is being established, removed, re-established, etc.)
4. Converted biomass is *perfectly mixed* within a sediment layer.
    **Implication**: this is a logical error, since biomass is exponentially distributed throughout the layer, this is made as a simplifying assumption - which could in theory be *partially* resolved by creating sublayers. This assumption is probably only an issue for very large layers (of substaintial deposition).
5. This is discrete time model, there are "order of operations" assumptions.
    **Order of Operations**:
    1. Transition [Turnover, Decomposition]
    2. Deposition/Erosion
    3. Removal
    4. New Layer (see below)
    5. Litter
    **Implication**: turnover occurs throughout timestep at constant rate, with deposition/erosion occuring instantaneously at the end of the timestep. This can be *partially* resolved with the use sub-timesteps (as a timestep parameter).
6. Biomass is in addition to the weight or length of deposited material.
    **Implication**: When a new layer is created, if depostion is positive (e.g., it is not an empty layer) the final weight or length will slightly exceed the deposition total. This implicitly assumes sediment is not "used" in the production of biomass. 
7. The bottom layer has cannot be removed. It maintains a constant depth.
    **Implication**: This is probably a reasonable assumption for most uses, but it effects the model outputs, since this layer will always maintain a constant depth.

## Simulation
1. A *.toml file is provided containing constants used in a core throughout a simulation.
2. During each timestp in a simulation the following parameters are provided:
    **Timestep Parameters**:
    1. Deposition/Erosion
        *Note*: negative deposition is erosion.
    2. Biomass at surface/Biomass above surface
        *Note*: if biomass above surface is provided then a constant factor is used to conver this value into biomass at surface.
    3. Litter/Litter fraction
        *Note*: if litter fraction is provided then this factor is multiplied by the biomass at surface value to compute the litter to be added to the model.
    4. Substeps
        *Note*: this is an optional parameter, used to approximate a continuous processes. The timestep values are equally apportioned over each of the sub-timesteps.
