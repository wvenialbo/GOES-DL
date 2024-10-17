$venv = '.venv'
$reqi = 'requirements.in'
$reqs = 'requirements.txt'

$deps = 'boto3'

$devs = 'flake8', 'black', 'pylint', 'mypy', 'bandit', 'ruff', 'eradicate', `
        'pydocstyle', 'flake8-black', 'flake8-pylint', 'flake8-isort', `
        'flake8-bandit', 'flake8-eradicate', 'flake8-bugbear', 'darglint2', `
        'flake8-builtins', 'flake8-comprehensions', 'flake8-docstrings', `
        'pep8-naming', 'flake8-docstrings-complete', 'flake8-ruff', `
        'flake8-pyproject', 'flake8-annotations', 'jupyterlab'
        # 'flake8-mypy', 'flake8-confusables'

$tool = 'pip', 'setuptools', 'build', 'wheel', 'pip-tools', 'findpydeps'

python --version
python -m pip --version

if (-not (Test-Path -Path $venv)) {
    python -m venv $venv
}

& $venv/Scripts/Activate.ps1
python -m pip install --upgrade $tool

$tool | Set-Content -Path $reqi
$devs | Add-Content -Path $reqi
$deps | Add-Content -Path $reqi

python -m piptools compile --upgrade --output-file $reqs $reqi

Remove-Item $reqi

deactivate
