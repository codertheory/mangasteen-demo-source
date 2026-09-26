# Mangasteen demo source

A source repository for [Mangasteen](https://mangasteen.codertheory.dev) that serves invented series with generated artwork. It exists for store screenshots and demos, so the app can be shown full of content without showing anyone else's work.

Every title, author, description, cover and page here is made up. The covers and reader pages are drawn by a script from shapes, halftone patterns and system fonts.

## Using it

In Mangasteen, go to Browse, then Extensions, and add this repository:

```
https://github.com/codertheory/mangasteen-demo-source
```

Then enable **Demo Source**. It has 24 series with Popular, Latest, search, chapter lists and a reader. Chapter dates are relative to the current time, so Latest always looks recently updated.

## Regenerating

The catalog lives in `catalog.json`. Covers, pages and `sources/demo/main.js` are generated from it:

```bash
python3 -m venv .venv && .venv/bin/pip install -r tools/requirements.txt
.venv/bin/python tools/generate.py
bash scripts/sign-sources.sh
```

Edit `tools/main.template.js` rather than `main.js`, and bump `version` in `sources/demo/extension.json` on every change. Fonts come from macOS, so the generator needs a Mac.

## License

MIT. The generated artwork is part of this repository and covered by the same license.
