'''
Entry point for command line application.
'''
import pickle
from pathlib import Path
from typing import Tuple, Optional
from typing_extensions import Annotated

import typer

from rich import print as rich_print

from src import __app_name__, __version__
from src.constants import MORRIS_CONSTANTS
from src.layers import Layers

DEFAULT_OUTPUT_FILE = str(Path(__file__).parent.parent.joinpath('data').joinpath('model.pkl'))


app = typer.Typer()
#pylint: disable=line-too-long

@app.command()
def initialize(config_filepath: Annotated[str,typer.Option(help='Path to file containing model constants.')] = MORRIS_CONSTANTS,
               model_file: Annotated[str, typer.Option(help='Path to file where outputs are saved.')] = DEFAULT_OUTPUT_FILE,
               verbose: Annotated[bool, typer.Option(help='Prints a summary of the model state.')] = True) -> None:
    '''
    Entry point for running the netherland model. Loads 
    '''
    layers = Layers(constants_filepath=config_filepath)
    if verbose:
        rich_print(*layers.to_string(), sep='\n')
    with open(model_file, 'wb') as file:
        rich_print()
        rich_print(f'writing to: {model_file}')
        pickle.dump(layers,file)

@app.command()
def update(timestep_inputs: Annotated[Tuple[float], typer.Option('--input', help='Inputs in the order: deposition, ...', prompt=True)],
           model_file: Annotated[str, typer.Option(help='Path to file where outputs are saved.')] = DEFAULT_OUTPUT_FILE,
           verbose: Annotated[bool, typer.Option(help='Prints a summary of the model state.')] = True) -> None:
    '''
    Moves model forward by one timestep.
    '''
    with open(model_file, 'rb') as file:
        rich_print()
        rich_print(f'reading from: {model_file}')
        layers = pickle.load(file)
    layers.update(deposition=timestep_inputs[0])
    if verbose:
        rich_print()
        rich_print(*layers.to_string(), sep='\n')

@app.command()
def main(version: Optional[bool] = typer.Option(None,
                                                '--version', '-v', 
                                                help='Show application version and exit.',
                                                is_eager=True)) -> None:
    '''
    Prints application name and version then exits.
    '''
    if version:
        rich_print(f'{__app_name__} v{__version__}')
        raise typer.Exit()

if __name__ == '__main__':
    app(prog_name=__app_name__)
