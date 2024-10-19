##
## Build a release package for deployment
##

$venv = '.venv'

$tool = $args[0]

if (-not $tool -or -not (($tool -eq 'build') -or ($tool -eq 'poetry') -or ($tool -eq 'wheel'))) {
    Write-Host "Usage: build.ps1 [build|poetry|wheel]"
    Write-Host ""
    exit
}

# Activate the environment if it is not active

$isVirtualEnvActive = $true

if (-not $env:VIRTUAL_ENV) {
    $isVirtualEnvActive = $false
    & $venv/Scripts/Activate.ps1
}

# Build the package based on user choice

if ($tool -eq 'wheel') {
    # Build the package as a wheel

    python -m build -n --wheel
}
elseif ($tool -eq 'wheel') {
    # Build the package as a .tar.gz

    python -m build -n
}
elseif ($tool -eq 'poetry') {
    poetry build -f sdist
}

# Deactivate the environment if it was not active

if (-not $isVirtualEnvActive) {
    deactivate
}
