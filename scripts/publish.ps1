##
## Upload package to PyPI
##

$venv = '.venv'

$release = $args[0]
$usage = "Usage: publish.ps1 dist/release"

if (-not $release) {
    Write-Host $usage
    Write-Host ""
    exit
}

$isFolder = Test-Path -Type Container -LiteralPath $project

# Activate the environment if it is not active

$isVirtualEnvActive = $true

if (-not $env:VIRTUAL_ENV) {
    $isVirtualEnvActive = $false
    & $venv/Scripts/Activate.ps1
}

# Display the version of python and pip

python --version
python -m pip --version

# Upload the package

twine upload $release/*

# Deactivate the environment if it was not active

if (-not $isVirtualEnvActive) {
    deactivate
}
