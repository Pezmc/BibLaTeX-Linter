BibLaTeX Linter
==============

*A simple [web app](https://biblatex-linter.herokuapp.com/) to lint BibLaTeX files*

[BibLaTeX Linter](https://biblatex-linter.herokuapp.com/) is a small Python powered web app, based on [BibLaTeX-Check](https://github.com/Pezmc/BibLaTeX-Check). Paste in a .bib file, and it goes through a list of references and checks if certain required fields are available, for instance, if each publication is assigned a year or if a journal article has a volume and issue number.

Please note that it is **not a BibLaTeX validator**. And in the current version, it might not yet be able to parse every valid bib file.

## Using the website

Head to [https://biblatex-linter.herokuapp.com/](https://biblatex-linter.herokuapp.com/) paste the contents of your .bib file and click validate!

## Running Locally

Make sure you have Python [installed properly](http://install.python-guide.org).

```sh
$ pipenv install

pipenv run python3 manage.py runserver
```

Your app should now be running on [localhost:8000](http://localhost:8000/).

## Alternatives

BibLaTeX Linter is adapted from [BibLaTeX-Check](https://github.com/Pezmc/BibLaTeX-Check), which, in turn, was adapted from [BibTex Check](https://code.google.com/p/bibtex-check/) by Fabian Beck, which can be used to validate BibTex files.

See [BibTex vs BibLaTeX vs NatBib](http://tex.stackexchange.com/questions/25701/bibtex-vs-biber-and-BibLaTeX-vs-natbib) for a comparison of different referencing packages.

## Screenshot

![Screenshots of the BibLaTeX check screen](https://github.com/Pezmc/BibLaTeX-Check/blob/screenshots/screenshots/checkscreen.png?raw=true "BibLaTeX Check")

## License

MIT license