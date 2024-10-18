##
## Clean up the Python environment
##

$venv = '.venv'

# Check if the environment exists, ensure we do not modify the system Python

if (Test-Path -Path $venv) {
    # Activate the environment if it is not active

    $isVirtualEnvActive = $true

    if (-not $env:VIRTUAL_ENV) {
        $isVirtualEnvActive = $false
        & $venv/Scripts/Activate.ps1
    }
    
    # Get the list of installed packages >> 'uninstall.txt'
    
    $uninstall = 'uninstall.txt'
    
    pip freeze > $uninstall

    # Remove all packages installed with `pip`

    if (Get-Content $uninstall) {
        pip uninstall -y -r $uninstall
    }
    else {
        Write-Warning "No packages to uninstall"
    }
    
    # Clean up auxiliary files
    
    Remove-Item $uninstall
    
    # Deactivate the environment if it was not active
    
    if (-not $isVirtualEnvActive) {
        deactivate
    }
}
