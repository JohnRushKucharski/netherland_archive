'''
Utility functions for the package.
'''

from typing import List, Tuple, Generator, Any

from src.validators import descending

@descending
def elevations_to_depth(elevations: Tuple[float, float]) -> float:
    '''
    Returns depth [in cm] given elevations [in cm].
    '''
    if len(elevations) != 2:
        raise ValueError(f'elevations: {elevations} must be a tuple of length 2.')
    return elevations[0] - elevations[1]

def enumerate_backwards(data: List[Any]|Tuple) -> Generator[Tuple[int, Any], None, None]:
    '''
    Returns a tuple of (index, item) tuples in reverse order.
    '''
    for i in range(len(data)-1, -1, -1):
        yield (i, data[i])
