import logging

from orglearn.mind_map.map_convertor import MapConvertor
from orglearn.mind_map.backend.backends import Backends
from orglearn.anki.anki_convertor import AnkiConvertor

import click


@click.group(invoke_without_command=True)
@click.option("-v", "--verbose", is_flag=True, help="Increase verbosity of orglearn.")
@click.pass_context
def main(ctx, verbose):
    """Toolbox for learning from your org notes."""

    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    if ctx.invoked_subcommand is None:
        print("Hello, orglearn")
    else:
        # print('Hello, some command')
        pass


@main.command()
@click.argument("org_files", type=click.Path(exists=True), required=True, nargs=-1)
@click.option(
    "-a",
    "--append",
    is_flag=True,
    help="Append cards to existing apki deck. Requires specifing -o option.",
)
@click.option(
    "-o",
    "--output",
    type=click.Path(resolve_path=True, dir_okay=False, writable=True),
    help="Conversion output file.",
)
@click.option(
    "-m",
    "--mobile",
    is_flag=True,
    help="Generate cards suitable for mobile anki (do not process latex).",
)
@click.option(
    "-i",
    "--ignore-tag",
    "itl",
    multiple=True,
    help="Ignore specified set of tags (can be specified multiple times).",
)
def anki(org_files, append, output, mobile, itl):
    """Convert org files ORG_FILES into an anki deck."""
    if append and not output:
        # TODO(mato): What do you think about using -a <file> instead of -a and -o combination?
        print("Append specified without output flag.")
        return

    c = AnkiConvertor(
        output, org_files, append=append, mobile=mobile, ignore_tags_list=itl
    )


@main.command()
@click.argument("org_files", type=click.Path(exists=True), nargs=-1)
@click.option(
    "-b",
    "--backend",
    "backend_name",
    default=Backends.get_default_backend(),
    type=click.Choice(Backends.get_backends()),
    help="Backend used for conversion. Usually represents output format.",
)
@click.option(
    "-o",
    "--output",
    type=click.Path(resolve_path=True, dir_okay=False, writable=True),
    help="Conversion output file.",
)
@click.option(
    "-i",
    "--ignore-tag",
    "itl",
    multiple=True,
    help="Ignore specified set of tags (can be specified multiple times).",
)
def map(org_files, backend_name, output, itl):
    """Convert org files ORG_FILES into a mind map."""
    backend = Backends.make(backend_name, ignore_tags_list=itl)
    conv = MapConvertor(output, org_files, backend)
