[![GitHub](https://img.shields.io/github/license/MatejKastak/orglearn?style=flat-square)](https://github.com/MatejKastak/orglearn/blob/master/LICENSE)

# Orglearn

Orglean provides tools for learning from org-mode notes. It can generate mind
maps and anki decks.

# Anki

Convert org to anki deck. The convertor will take all leafs of the tree (nodes
without children) and convert them into an anki card. The node title is
front-side of the card and the body is the back-side of the card.

# Mind map

TBD

# PDF

Orglearn is able to create pdf from your notes. You can achieve similar results
converting org files to pdf using emacs. But we think that using `pandoc`
results in better looking pdfs.

To be able to convert org files to pdf you need to have `pandoc` installed on
your system.

# Instalation

```sh
python -m venv env # In case you want to install in virtualenv.
. env/bin/activate
pip install .
```

# Usage

Below are some basic examples for running orglearn:

```sh
orglearn anki file1.org # Convert org file into anki deck ./file1.apkg
orglearn anki file1.org file2.org # Convert multiple files into single deck
```

# Contributing

Contribution guidelines TBD.

We are using the [black](https://github.com/psf/black) for the source code
formatting. To use it automatically preprare pre-commit hooks with the following
command.

```sh
pre-commit install # Install the pre-commit hooks
```

