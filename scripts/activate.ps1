##
## Initialize/update the project environment
##

$venv = '.venv'

if (-not $env:VIRTUAL_ENV) {
    & $venv/Scripts/Activate.ps1
}
