# MediaTubeScripts

## Intro

Scripts to process source files with ffmpeg, mediainfo to host in browser

## Dependencies

The following tools must be in the users path.

* ffmpeg
* mediainfo (cli)
* libwebp

## Development

### Setup venv!

#### Linux
```sh
python3 -m venv .venv
source .venv/scripts/activate
```

#### Windows
```bat
python3 -m venv .venv
.venv/scripts/activate
```

### Install dependencies

```sh
pip install -r requirements.txt
```

## Debug

Install package in edit mode

```sh
pip install -e .
```

## Tests

Expect test video file (1920x1080@30fps) to be in test/examples/test.mp4

```sh
pytest test
```



## Docs

Build docs

```sh
sphinx-build -b html docs/source docs/build
```

# Dist

Create binary install package

```sh
python3 setup.py bdist
```
