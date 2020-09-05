import logging
import os
import tempfile
import typing

import click

import pypandoc
from orglearn.anki.anki_convertor import AnkiConvertor
from orglearn.anki.node_convertor import AnkiConvertMode
from orglearn.mind_map.backend.backends import Backends
from orglearn.mind_map.map_convertor import MapConvertor
from orglearn.preprocessor import preprocess_string


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
@click.option(
    "-H",
    "--heading-level",
    "heading_level",
    default=4,
    show_default=True,
    type=click.IntRange(1, 8),
    help="Set the heading level of the output pdf file.",
)
def pdf(org_files: typing.Tuple[str], heading_level: int) -> None:
    """Convert ORG_FILES into pdf files."""

    # TODO: Test if pandoc is installed, if not report an error

    with tempfile.NamedTemporaryFile(suffix=".tex") as fp:
        fp.write(
            rb"""   \usepackage{enumitem}
    \usepackage{dsfont}
    \setlistdepth{9}

    \setlist[itemize,1]{label=$\bullet$}
    \setlist[itemize,2]{label=$\bullet$}
    \setlist[itemize,3]{label=$\bullet$}
    \setlist[itemize,4]{label=$\bullet$}
    \setlist[itemize,5]{label=$\bullet$}
    \setlist[itemize,6]{label=$\bullet$}
    \setlist[itemize,7]{label=$\bullet$}
    \setlist[itemize,8]{label=$\bullet$}
    \setlist[itemize,9]{label=$\bullet$}
    \renewlist{itemize}{itemize}{9}

    \setlist[enumerate,1]{label=$\arabic*.$}
    \setlist[enumerate,2]{label=$\alph*.$}
    \setlist[enumerate,3]{label=$\roman*.$}
    \setlist[enumerate,4]{label=$\arabic*.$}
    \setlist[enumerate,5]{label=$\alpha*$}
    \setlist[enumerate,6]{label=$\roman*.$}
    \setlist[enumerate,7]{label=$\arabic*.$}
    \setlist[enumerate,8]{label=$\alph*.$}
    \setlist[enumerate,9]{label=$\roman*.$}
    \renewlist{enumerate}{enumerate}{9}
"""
        )

        fp.flush()

        old_working_directory = os.getcwd()

        for file_path in org_files:

            input_content = ""
            input_content += "#+OPTIONS: tags:nil\n"

            if heading_level:
                input_content += "#+OPTIONS: H:{}\n".format(heading_level)

            with open(file_path, "r") as input_file:
                input_content += preprocess_string(input_file.read())

            # Change the compilation context to the file directory
            # this is needed in order to include images from the paths relative to org file
            os.chdir(os.path.dirname(os.path.abspath(file_path)))

            of = os.path.splitext(os.path.basename(file_path))[0] + ".pdf"
            pypandoc.convert_text(
                input_content,
                "pdf",
                "org",
                outputfile=of,
                extra_args=[
                    "--toc",
                    "-N",
                    "-V",
                    "geometry:top=2.5cm, bottom=2.5cm, left=4cm, right=4cm",
                    "-H",
                    fp.name,
                ],
            )

        # Restore the old working directory
        os.chdir(old_working_directory)
