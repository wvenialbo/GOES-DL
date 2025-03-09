##
## Make the project development requirements.dev
##

$venv = '.venv'

$tool = 'pip', 'pip-tools', 'findpydeps', 'setuptools', 'build', 'wheel', `
        'twine', 'pyinstaller', 'pyinstaller_versionfile'

# Activate the environment if it is not active, and upgrade tools

$isVirtualEnvActive = $true

if (-not $env:VIRTUAL_ENV) {
    $isVirtualEnvActive = $false
    & $venv/Scripts/Activate.ps1
    if (-not $env:VIRTUAL_ENV) {
        exit 1
    }
}

python -m pip install --upgrade $tool

# Display the version of python and pip

py -0
python --version
python -m pip --version

# Save th list of devtime packages to install in 'requirements-dev.in'

$reqdevi = 'requirements-dev.in'
$reqdevo = 'requirements-dev.txt'

# Compile the 'requirements-dev.in' to 'requirements-dev.txt'

if (Test-Path -Path $reqdevi) {
    python -m piptools compile --upgrade --output-file $reqdevo $reqdevi
}

# Save th list of packages to install in 'requirements.in'

$reqdepi = 'requirements.in'
$reqdepo = 'requirements.txt'

# Compile the 'requirements.in' to 'requirements.txt'

if (Test-Path -Path $reqdepi) {
    python -m piptools compile --upgrade --output-file $reqdepo $reqdepi
}


if (-not $isVirtualEnvActive) {
    deactivate
}
