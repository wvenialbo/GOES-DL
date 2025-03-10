##
## Generate coverage report
##

$venv = '.venv'

$output = $args[0]

if (-not $output -or -not (($output -eq 'html') -or ($output -eq 'report') -or ($output -eq 'xml'))) {
    Write-Host "Usage: build.ps1 [html|report|xml]"
    Write-Host ""
    exit
}

if (Test-Path .coverage) {
    $isVirtualEnvActive = $true
    
    if (-not $env:VIRTUAL_ENV) {
        $isVirtualEnvActive = $false
        & $venv/Scripts/Activate.ps1
    }

    if ($output -eq 'report') {
        coverage report -m
    }
    elseif ($output -eq 'xml') {
        coverage xml
    }
    elseif ($output -eq 'html') {
        coverage html
    }
    else {
        Write-Host "Invalid output format."
    }
    
    if (-not $isVirtualEnvActive) {
        deactivate
    }
}
else {
    Write-Host "No coverage data found."
}
