##
## Install the project development requirements.dev
##

$venv = '.venv'

$requirements_txt = $args[0]

if (-not $requirements_txt) {
    $requirements_txt = 'requirements.txt'
}

# Activate the environment if it is not active

$isVirtualEnvActive = $true

if (-not $env:VIRTUAL_ENV) {
    $isVirtualEnvActive = $false
    & $venv/Scripts/Activate.ps1
}

# Display the version of python and pip

python --version
python -m pip --version

# Install the project development requirements.dev

$requirements_dev = 'requirements.dev'

python -m pip install --upgrade -r $requirements_dev

# Install the project requirements.txt, if it exists

if (Test-Path -Path $requirements_txt) {
    python -m pip install --upgrade -r $requirements_txt
}

# Deactivate the environment if it was not active

if (-not $isVirtualEnvActive) {
    deactivate
}
