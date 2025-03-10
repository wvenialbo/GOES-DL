$project = '~/path/to/project/'
$venv = '.venv'

if (Test-Path -Path $project) {
    cd $project

    if ($env:VIRTUAL_ENV) {
        deactivate
    }

    if (Test-Path -Path $venv) {
        & $venv/Scripts/Activate.ps1
    }
    else {
        Write-Host "no virtual environment found!"
        Write-Host ""
    }
}
else {
    Write-Warning "project folder not found!"
    Write-Host ""
}
