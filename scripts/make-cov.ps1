##
## Run unit tests with coverage
##

$venv = '.venv'

$isVirtualEnvActive = $true

if (-not $env:VIRTUAL_ENV) {
    $isVirtualEnvActive = $false
    & $venv/Scripts/Activate.ps1
}

coverage run -m unittest discover .\tests

if (-not $isVirtualEnvActive) {
    deactivate
}
