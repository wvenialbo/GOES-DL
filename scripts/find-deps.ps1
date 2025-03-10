##
## Find the project dependencies and create/update requirements.txt
##

$venv = '.venv'

$project = $args[0]

if (-not $project) {
    Write-Host "Usage: find-deps.ps1 <project>"
    Write-Host ""
    Write-Host "  project: the path to the project"
    Write-Host ""
    exit
}

# Activate the environment if it is not active

$isVirtualEnvActive = $true

if (-not $env:VIRTUAL_ENV) {
    $isVirtualEnvActive = $false
    & $venv/Scripts/Activate.ps1
}

# Get the list of installed packages >> 'installed.txt'

$installed_txt = 'installed.txt'

pip freeze > $installed_txt

# Extract required packages from source code >> 'required.txt'

$required_txt = 'required.txt'

findpydeps -l -i $project > $required_txt

# Read the content of 'required.txt' and 'installed.txt' into arrays

$required = Get-Content -Path $required_txt
$installed = Get-Content -Path $installed_txt

# Replace underscores with dashes in 'required.txt'

$required = $required -replace '_', '-'

# Treat known special cases in 'required.txt':
#   - replace `cv2` with `opencv-python-*`
#   - replace `sklearn` with `scikit-learn`
#   - remove `botocore` wich comes with `boto3`

$required = $required -replace 'cv2', 'opencv-python-headless'
$required = $required -replace 'sklearn', 'scikit-learn'
$required = $required -replace "botocore", ""

# Create two empty arrays for 'requirements.prj' and 'requirements.dev'

$required_prj = @()

# Loop through each line in 'installed.txt'

foreach ($line in $installed) {
    # Split the package name from the version string

    $packageName = $line.Split('==')[0]

    # Check if the package name is in 'required.txt'

    if ($required -contains $packageName) {

        # Add to 'requirements.txt'

        $required_prj += $line + "`n"

    }
}

$requirements_txt = 'requirements.txt'

# Pin the current version of the packages...
# $required_prj | Set-Content -NoNewline -Path $requirements_txt

# ... or replace '==' with '~=' for backward-compatibility
#                  or with '>=' for forward compatibility
$required_prj.Replace('==', '~=') | Set-Content -NoNewline -Path $requirements_txt

# Clean up auxiliary files

$files = $required_txt, $installed_txt

Foreach ($file in $files) {
    If (Test-Path $file) {
        Remove-Item $file
    }
}

# Deactivate the environment if it was not active

if (-not $isVirtualEnvActive) {
    deactivate
}
