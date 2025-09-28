$ErrorActionPreference = 'Stop'

pip install -U pip ; pip install -e libs/archi_core ; pip install pytest
pytest -q
