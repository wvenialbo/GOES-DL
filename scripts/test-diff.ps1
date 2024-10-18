##
## This script is used to test the difference between the dependencies before
## and after the installation of a package.
##

$venv = '.venv'

$before = 'before.txt'
$after = 'after.txt'
$dependencies = 'dependencies.txt'

$isVirtualEnvActive = $true

if (-not $env:VIRTUAL_ENV) {
    $isVirtualEnvActive = $false
    & $venv/Scripts/Activate.ps1
}

if (-not (Test-Path -Path $dependencies)) {
    python --version > $dependencies
    python -m pip --version >> $dependencies
    Add-Content -Path $dependencies -Value "--------"
    Add-Content -Path $dependencies -Value ""
}

python -m pip freeze > $before

python -m pip install --upgrade 'flake8'

$content_before = Get-Content -Path $before

if ($content_before) {
    python -m pip freeze > $after
    $content_after = Get-Content -Path $after
    $content_after = $content_after | Where-Object { $_ -notin $content_before }
}
else {
    python -m pip freeze > $after
    $content_after = Get-Content -Path $after
}

$content_after | Add-Content -Path $dependencies
Add-Content -Path $dependencies -Value ""
Add-Content -Path $dependencies -Value "--------"
Add-Content -Path $dependencies -Value ""

Remove-Item $before
Remove-Item $after

if (-not $isVirtualEnvActive) {
    deactivate
}
