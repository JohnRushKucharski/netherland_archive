'''Validation functions for biomass module.'''

from typing import List, Tuple, Callable, Any

def positive(fx: Callable[...,Any]) -> Callable[..., Any]:  # pylint: disable=invalid-name
    '''
    Decorator that validates positive inputs.
    '''
    def validator(**kwargs) -> Any:
        for key, value in kwargs.items():
            positive_attribute(key=key, value=value)
        return fx(**kwargs)
    return validator
def positive_attribute(key: str, value: float|int) -> None:
    '''
    Validates attribute is positive.
    '''
    if isinstance(value, (float, int)) and not isinstance(value, bool) and value <= 0:
        raise ValueError(f'{key} must be positive.')
def non_negative(fx: Callable[...,Any]) -> Callable[...,Any]:  # pylint: disable=invalid-name
    '''
    Decorator that validates non-negative inputs.
    '''
    def validator(**kwargs) -> Any:
        for key, value in kwargs.items():
            non_negative_attribute(key=key, value=value)
        return fx(**kwargs)
    return validator
def non_negative_attribute(key: str, value: float|int) -> None:
    '''
    Validates attribute is non-negative.
    '''
    if isinstance(value, (float, int)) and not isinstance(value, bool) and value < 0:
        raise ValueError(f'{key} must be non-negative.')
def ascending(fx: Callable[...,Any]) -> Callable[...,Any]:  # pylint: disable=invalid-name
    '''
    Decorator that validates input lists or tuples are in ascending {x_1 < x_2, ... x_n} order.
    '''
    def validator(**kwargs) -> Any:
        for key, value in kwargs.items():
            if isinstance(value, (tuple, list)):
                ascending_attribute(key=key, value=value)
        return fx(**kwargs)
    return validator
def ascending_attribute(key: str, value: List|Tuple) -> None:
    '''
    Validates tuple or list is in ascending order.
    '''
    for index, item in enumerate(value):
        if not isinstance(item, (float, int)):
            break
        if index > 0 and item < value[index-1]:
            raise ValueError(f'{key}: {value} values must in accending order.')
def ascending_positive_attribute(key: str, value: List|Tuple) -> None:
    '''
    Validates tuple or list is in ascending order and positive.
    '''
    for index, item in enumerate(value):
        if not isinstance(item, (float, int)):
            break
        if index > 0 and item < value[index-1]:
            raise ValueError(f'{key}: {value} values must in accending order.')
        non_negative_attribute(key=key, value=item)
def ascending_non_negative_attribute(key: str, value: List|Tuple) -> None:
    '''
    Validates tuple or list is in ascending order and non-negative.
    '''
    for index, item in enumerate(value):
        if not isinstance(item, (float, int)):
            break
        if index > 0 and item < value[index-1]:
            raise ValueError(f'{key}: {value} values must in accending order.')
        non_negative_attribute(key=key, value=item)
def descending(fx: Callable[...,Any]) -> Callable[...,Any]:  # pylint: disable=invalid-name
    '''
    Decorator that validates input lists or tuples are in descending {x_1 > x_2, ... x_n} order.
    '''
    def validator(**kwargs) -> Any:
        for key, value in kwargs.items():
            if isinstance(value, (tuple, list)):
                descending_attribute(key=key, value=value)
        return fx(**kwargs)
    return validator
def descending_attribute(key: str, value: List|Tuple) -> None:
    '''
    Validates tuple or list is in descending order.
    '''
    for index, item in enumerate(value):
        if not isinstance(item, (float, int)):
            break
        if index > 0 and item > value[index-1]:
            raise ValueError(f'{key}: {value} values must in decending order.')
def descending_positive_attribute(key: str, value: List|Tuple) -> None:
    '''
    Validates tuple or list is in descending order and positive.
    '''
    for index, item in enumerate(value):
        if not isinstance(item, (float, int)):
            break
        if index > 0 and item > value[index-1]:
            raise ValueError(f'{key}: {value} values must in decending order.')
        non_negative_attribute(key=key, value=item)
def descending_non_negative_attribute(key: str, value: List|Tuple) -> None:
    '''
    Validates tuple or list is in descending order and non-negative.
    '''
    for index, item in enumerate(value):
        if not isinstance(item, (float, int)):
            break
        if index > 0 and item > value[index-1]:
            raise ValueError(f'{key}: {value} values must in decending order.')
        non_negative_attribute(key=key, value=item)
