##
## Make the project development requirements.dev
##

$venv = '.venv'

# Set the list of development tool packages to install

$devs = 'bandit', 'ruff', 'mypy', 'pyflakes', 'isort', 'pylint', `
    'eradicate', 'black', 'pycodestyle', 'autopep8', 'pydocstyle', `
    'pydoclint', 'pydoctest', 'docsig', 'flake8', 'pep8-naming', `
    'flake8-bugbear', 'flake8-pyproject', 'flake8-builtins', `
    'flake8-annotations', 'flake8-comprehensions', 'darglint2', `
    'flake8-pytest-style', 'pytest', 'pytest-cov', 'pytest-mock', `
    'pytest-xdist', 'coverage', 'pyinstrument', 'jupyterlab', `
    'types-requests', 'boto3-stubs[s3]'

$tool = 'pip', 'setuptools', 'build', 'wheel', 'pip-tools', 'twine', `
    'findpydeps'

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
