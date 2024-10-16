##
## Update the dependency lists
##

$project = 'GOES_DL'

# Activate the environment

& ./.venv/Scripts/Activate.ps1

# Install/Update the `findpydeps` tool package

pip install findpydeps --upgrade

# Get the list of installed packages >> 'installed.txt'

$installed_pkgs = 'installed.txt'

pip freeze > $installed_pkgs

# Extract required packages from source code >> 'required.txt'

$required_pkgs = 'required.txt'

findpydeps -l -i $project > $required_pkgs

# Read the content of 'required.txt' and 'installed.txt' into arrays

$required = Get-Content -Path $required_pkgs
$installed = Get-Content -Path $installed_pkgs

# Replace underscores with dashes in 'required.txt'

$required = $required -replace '_', '-'

# Treat known special cases in 'required.txt':
#   - replace `cv2` with `opencv-python-*`
#   - replace `sklearn` with `scikit-learn`

$required = $required -replace 'cv2', 'opencv-python-headless'
$required = $required -replace 'sklearn', 'scikit-learn'

# Create two empty arrays for 'requirements.txt' and 'requirements-dev.txt'

$required_prod = @()

$required_dev = @()

# Loop through each line in 'installed.txt'

foreach ($line in $installed) {

    # Split the package name from the version string

    $packageName = $line.Split('==')[0]

    # Check if the package name is in 'required.txt'

    if ($required -contains $packageName) {

        # Add to 'requirements.txt'

        $required_prod += $line + "`n"

    }
    else {

        # Add to 'requirements-dev.txt'

        $required_dev += $line + "`n"

    }
}

# Write the results to separate text files:
#
# Replace '==' with '~=' for backward-compatibility in 'requirements.txt'
#           or with '>=' for forward compatibility in 'requirements-dev.txt'

# Just pin the current version of the package in 'requirements.txt'
#$requirements = 'requirements.txt'
#$requirements_dev = 'requirements-dev.txt'

#$required_prod.Replace('==', '~=') | Set-Content -NoNewline -Path $requirements
#$required_dev.Replace('==', '>=') | Set-Content -NoNewline -Path $requirements_dev

# Clean up auxiliary files

$files = $required_pkgs, $installed_pkgs

Foreach ($file in $files) {
    If (Test-Path $file) {
        Remove-Item $file
    }
}
