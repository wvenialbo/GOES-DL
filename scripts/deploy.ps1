##
## Install the project in editable mode
##

$venv = '.venv'

# Activate the environment if it is not active, and upgrade tools

$isVirtualEnvActive = $true

if (-not $env:VIRTUAL_ENV) {
    $isVirtualEnvActive = $false
    & $venv/Scripts/Activate.ps1
}

# Install the project

python -m pip install -e .

#-e git+https://github.com/wvenialbo/GOES-DL.git@c43f2536acc4b2139363485912b04699582483c6#egg=goes_dl

# Deactivate the environment if it was not active

Remove-Item $reqi

if (-not $isVirtualEnvActive) {
    deactivate
}
