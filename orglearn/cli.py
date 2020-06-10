import logging
import os
import typing

import click

import pypandoc
from orglearn.anki.anki_convertor import AnkiConvertor
from orglearn.anki.node_convertor import AnkiConvertMode
from orglearn.mind_map.backend.backends import Backends
from orglearn.mind_map.map_convertor import MapConvertor


@click.group(invoke_without_command=True)
@click.option("-v", "--verbose", is_flag=True, help="Increase verbosity of orglearn.")
@click.pass_context
def main(ctx: click.Context, verbose: bool) -> None:
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
    "-c",
    "--conversion-mode",
    type=click.Choice(AnkiConvertMode.__members__.keys(), case_sensitive=False),
    help="Anki conversion mode.",
    default=None,
    show_default=True,
)
@click.option(
    "-i",
    "--ignore-shallow-tag",
    "istl",
    multiple=True,
    help="Ignore specified set of shallow tags (can be specified multiple times).",
)
@click.option(
    "-I",
    "--ignore-tag",
    "itl",
    multiple=True,
    help="Ignore specified set of tags (can be specified multiple times).",
)
def anki(
    org_files: typing.Tuple[str],
    append: bool,
    output: str,
    mobile: bool,
    conversion_mode: typing.Optional[str],
    istl: bool,
    itl: bool,
) -> None:
    """Convert org files ORG_FILES into an anki deck."""
    if append and not output:
        print("Append specified without output flag.")
        return

    # TODO: Create click.Choice for enums and return optional enum instead of this conversion
    _conversion_mode = AnkiConvertMode[conversion_mode.upper()] if conversion_mode else None

    c = AnkiConvertor(
        output,
        org_files,
        append=append,
        mobile=mobile,
        convert_mode=_conversion_mode,
        ignore_shallow_tags_list=istl,
        ignore_tags_list=itl,
    )


@main.command("map")
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
def map_cmd(org_files: typing.Tuple[str], backend_name: str, output: str, itl: bool) -> None:
    """Convert org files ORG_FILES into a mind map."""
    backend = Backends.make(backend_name, ignore_tags_list=itl)
    conv = MapConvertor(output, org_files, backend)


@main.command()
@click.argument("org_files", type=click.Path(exists=True), required=True, nargs=-1)
def pdf(org_files: typing.Tuple[str]) -> None:
    """Convert org files ORG_FILES into a pdf file."""

    # TODO: Test if pandoc is installed, if not report an error

    for f in org_files:
        of = os.path.splitext(f)[0] + ".pdf"
        pypandoc.convert_file(f, "pdf", outputfile=of, extra_args=["--toc"])
