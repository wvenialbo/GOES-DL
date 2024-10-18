##
## Initialize/update the project environment
##

$venv = '.venv'

# Update the environment if it exists, otherwise create it

if (Test-Path -Path $venv) {
    # Deactivate the environment if it is active

    $isVirtualEnvActive = $false

    if ($env:VIRTUAL_ENV) {
        $isVirtualEnvActive = $true
        deactivate
    }

    # Display the current version of python and pip

    python --version
    python -m pip --version

    # Upgrade the environment and its dependencies

    python -m venv --upgrade $venv
    python -m venv --upgrade-deps $venv

    # Re-activate the environment if it was active
    
    if ($isVirtualEnvActive) {
        & $venv/Scripts/Activate.ps1
    }
}
else {
    # Display the current version of python and pip

    python --version
    python -m pip --version

    # Create a new environment

    python -m venv $venv
}
