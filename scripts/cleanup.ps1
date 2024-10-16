##
## Clean up the Python environment
##

# Remove all packages installed with `pip`

# Activate the environment

& ./.venv/Scripts/Activate.ps1

# Get the list of installed packages >> 'uninstall.txt'

$uninstall = 'uninstall.txt'

pip freeze > $uninstall

# Uninstall packages by the `pip` tool

pip uninstall -y -r $uninstall

# Clean up auxiliary files

Remove-Item $uninstall
