# Orglearn

Orglean provides tools for learning from org-mode notes. It can generate mind
maps and anki decks.

# Anki

Convert org to anki deck. The convertor will take all leafs of the tree (nodes
without children) and convert them into an anki card. The node title is
front-side of the card and the body is the back-side of the card.

# Mind map

TBD

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

We are using the black for the source code formatting. To use it automatically
preprare pre-commit hooks with the following command.

```sh
pre-commit install # Install the pre-commit hooks
```

