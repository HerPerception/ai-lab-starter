## To run the test file (until you get a pyproject.toml):
```
PYTHONPATH=src python -m unittest discover -s tests -v
```

## To run the test file (if the project root has a pyproject.toml):
* 1. Link your local src/ailab package into your venv
```
pip install -e .
```

* 2. Run unittest discover without PYTHONPATH
```
python -m unittest discover -s tests -v
```