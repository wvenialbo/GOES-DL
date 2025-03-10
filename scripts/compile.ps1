##
## Build a release executable for deployment
##

$venv = '.venv'

$tool = $args[0]
$name = $args[1]
$entry = $args[2]

if (-not $tool -or -not $name -or -not $entry -or -not (($tool -eq 'multi') -or ($tool -eq 'single'))) {
    Write-Host "Usage: build.ps1 [multi|single] <name> <entry-point>"
    Write-Host ""
    Write-Host "  name: executable name"
    Write-Host "  entry-point: .py file containing the entry point"
    Write-Host ""
    exit
}

# Activate the environment if it is not active

$isVirtualEnvActive = $true

if (-not $env:VIRTUAL_ENV) {
    $isVirtualEnvActive = $false
    & $venv/Scripts/Activate.ps1
}

# Install/Update the `pyinstaller` tool package

pip install pyinstaller --upgrade

# Set the PyInstaller option based on user choice

if ($tool -eq 'multi') {
    # Build the application with separate files

    pyinstaller --onedir --name $name $entry
}
elseif ($tool -eq 'single') {
    # Build the application as a single executable

    pyinstaller --onefile --name $name $entry
}

# Deactivate the environment if it was not active

if (-not $isVirtualEnvActive) {
    deactivate
}
