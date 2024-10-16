##
## Build the package for deployment
##

# To build a wheel:
# .\pack.ps1 -Wheel
#
# To build a .tar.gz:
# .\build.ps1

param (
    [switch]$Wheel
)

# Activate the environment

& ./.venv/Scripts/Activate.ps1

# Build the package based on user choice

if ($Wheel) {

    # Install/Update the `build` and `wheel` tools packages

    pip install build wheel --upgrade

    # Build the package as a wheel

    python -m build -n --wheel

} else {

    # Install/Update the `build` tool package

    pip install build --upgrade

    # Build the package as a .tar.gz

    python -m build -n

}
