[![GitHub](https://img.shields.io/github/license/MatejKastak/orglearn?style=flat-square)](https://github.com/MatejKastak/orglearn/blob/master/LICENSE)

# Orglearn

Orglean provides toolbox for learning from your org-mode notes. It can generate mind
maps, anki decks and even pdfs textbooks.

## Modes [commands]

### Anki

Convert notes to anki deck. The convertor will take all leafs of the tree (nodes
without children) and convert them into anki cards. The node title is
front-side of the card and the body is the back-side of the card.

### Mind map

Convert notes into a [mid map](https://en.wikipedia.org/wiki/Mind_map). This is a
good way to visualize the relationships between each node.

### PDF

Orglearn is able to create pdf from your notes. You can achieve similar results
converting org files to pdf using emacs. But we think that using `pandoc`
results in better looking pdfs and gives us the best way to customize the result.

To be able to convert org files to pdf you need to have `pandoc` installed on
your system.

## Instalation

The latest stable release of `orglearn` can be obtained via `pypi`:
```sh
pip install orglearn
```

If you wish to install the latest `master` branch:

```sh
git clone https://github.com/MatejKastak/orglearn && cd orglearn
python -m venv env && . env/bin/activate # In case you want to install in virtualenv.
pip install .
```

## Usage

Below are some basic examples for running orglearn:

```sh
orglearn anki file1.org # Convert org file into anki deck ./file1.apkg
orglearn anki file1.org file2.org # Convert multiple files into single deck
```

## Contributing

Constributions are highly appreciated. If you choose to contribute please read the Contribution Guidelines (TBD).

We are using the [black](https://github.com/psf/black) for the source code
formatting. To use it automatically preprare pre-commit hooks with the following
command.

```sh
pre-commit install # Install the pre-commit hooks
```

