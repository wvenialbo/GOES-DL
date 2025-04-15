##
## Upload package to PyPI
##

$venv = ".venv"
$dist = "dist/"

$usage = "Usage: publish.ps1 v1.0-rc1"

if (-not $args[0]) {
    Write-Host $usage
    Write-Host ""
    exit
}

$release = $dist + $args[0]

mkdir $release
Move-Item -Path $dist"*.gz" -Destination $release
Move-Item -Path $dist"*.whl" -Destination $release

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
