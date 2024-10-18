##
## This script is used to run the application in a virtual environment.
##

$venv = '.venv'

$tool = $args[0]

if (-not $tool -or -not (($tool -eq 'exe') -or ($tool -eq 'wheel'))) {
    Write-Host "Usage: run.ps1 [exe|wheel]"
    Write-Host ""
    exit
}

$isVirtualEnvActive = $true

if (-not $env:VIRTUAL_ENV) {
    $isVirtualEnvActive = $false
    & $venv/Scripts/Activate.ps1
}

if ($tool -eq 'exe') {
    ./dist/goes-dl.exe
}
elseif ($tool -eq 'wheel') {
    python -m goes-dl
}

if (-not $isVirtualEnvActive) {
    deactivate
}

