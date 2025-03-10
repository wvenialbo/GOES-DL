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

    py -0
    py --version
    py -m pip --version

    # Upgrade the environment and its dependencies

    py -m venv --upgrade $venv
    py -m venv --upgrade-deps $venv

    # Re-activate the environment if it was active
    
    if ($isVirtualEnvActive) {
        & $venv/Scripts/Activate.ps1
    }
}
else {
    # Display the current version of python and pip

    py -0
    py --version
    py -m pip --version

    # Create a new environment

    py -m venv $venv
}
