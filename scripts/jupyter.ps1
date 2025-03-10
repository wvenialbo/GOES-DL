##
## Start Jupyter Lab
##

$venv = '.venv'

$nobrowser = $args[0]

$isVirtualEnvActive = $true

if (-not $env:VIRTUAL_ENV) {
    $isVirtualEnvActive = $false
    & $venv/Scripts/Activate.ps1
}

if ($nobrowser) {
    jupyter-lab --no-browser
}
else {
    jupyter-lab
}

if (-not $isVirtualEnvActive) {
    deactivate
}
