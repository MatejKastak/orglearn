import logging

from orglearn.map.map_convertor import MapConvertor
from orglearn.map.backend.backends import Backends
from orglearn.anki.anki_convertor import AnkiConvertor

import click

@click.group(invoke_without_command=True)
@click.option('-v', '--verbose', is_flag=True)
@click.pass_context
def main(ctx, verbose):
    """Toolbox for learning from your org notes."""

    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    if ctx.invoked_subcommand is None:
        print('Hello, orglearn')
    else:
        # print('Hello, some command')
        pass

@main.command()
@click.argument('org_files', type=click.Path(exists=True), nargs=-1)
@click.option('-a', '--append', is_flag=True)
@click.option('-o', '--output', type=click.Path(resolve_path=True, dir_okay=False, writable=True))
def anki(org_files, append, output):
    """Convert org files into an anki deck."""
    if append and not output:
        # TODO(mato): What do you think about using -a <file> instead of -a and -o combination?
        print('Append specified without output flag.')
        return

    c = AnkiConvertor(output, org_files, append=append)

@main.command()
@click.argument('org_files', type=click.Path(exists=True), nargs=-1)
@click.option('-b', '--backend', 'backend_param', default=Backends.get_default_backend(), type=click.Choice(Backends.get_backends()))
@click.option('-o', '--output', type=click.Path(resolve_path=True, dir_okay=False, writable=True))
def map(org_files, backend_param, output):
    """Convert org files into a mind map."""

    # TODO(mato): Create function to return available backends

    # TODO(mato): Register backend map: string -> backend

    # print(Backend.BACKENDS)
    # backend = Backend.make(backend_param)
    print(Backends.BACKENDS)
    backend = Backends.make(backend_param)
    conv = MapConvertor(output, org_files, backend)
