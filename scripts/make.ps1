##
## Make the project development requirements.dev
##

$venv = '.venv'

# Set the list of development tool packages to install

$devs = 'flake8', 'black', 'pylint', 'mypy', 'bandit', 'ruff', 'eradicate', `
    'pydocstyle', 'flake8-black', 'flake8-pylint', 'flake8-isort', `
    'flake8-bandit', 'flake8-eradicate', 'flake8-bugbear', 'darglint2', `
    'flake8-builtins', 'flake8-comprehensions', 'flake8-docstrings', `
    'pep8-naming', 'flake8-docstrings-complete', 'flake8-ruff', `
    'flake8-pyproject', 'flake8-annotations', 'jupyterlab', 'pyright', `
    'pytest', 'pytest-cov', 'pytest-xdist', 'pytest-mock', 'coverage', `
    'safety', 'xenon', 'pydoctest', 'docsig', 'pydoclint'
    # 'flake8-mypy', 'flake8-confusables'

$tool = 'pip', 'setuptools', 'build', 'wheel', 'pip-tools', 'findpydeps', `
    'pyinstaller'

# Activate the environment if it is not active, and upgrade tools

$isVirtualEnvActive = $true

if (-not $env:VIRTUAL_ENV) {
    $isVirtualEnvActive = $false
    & $venv/Scripts/Activate.ps1
}

python -m pip install --upgrade $tool

# Display the version of python and pip

python --version
python -m pip --version

# Save th list of packages to install in 'requirements.in'

$reqi = 'requirements.in'
$reqs = 'requirements.dev'

$devs | Set-Content -Path $reqi
$deps | Add-Content -Path $reqi

# Compile the 'requirements.in' to 'requirements.dev'

python -m piptools compile --upgrade --output-file $reqs $reqi

# Clean up auxiliary files and deactivate the environment if it was not active

Remove-Item $reqi

if (-not $isVirtualEnvActive) {
    deactivate
}
