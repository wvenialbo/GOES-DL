##
## Initialize/update the project environment
##

$venv = '.venv'

if ($env:VIRTUAL_ENV) {
    deactivate
}

if (Test-Path -Path $venv) {
    & $venv/Scripts/Activate.ps1
}
else {
    Write-Warning "no virtual environment found!"
    Write-Host ""
}
