##
## Run the CI/CD toolchain
##

$venv = '.venv'

$project = $args[0]

if (-not $project) {
    $project = './src/goesdl'
}

$isFolder = Test-Path -Type Container -LiteralPath $project

# Run the document linters

Write-Host "Running CI/CD toolchain for $project"
Write-Host ""

# Activate the environment if it is not active

$isVirtualEnvActive = $true

if (-not $env:VIRTUAL_ENV) {
    $isVirtualEnvActive = $false
    & $venv/Scripts/Activate.ps1
}

Write-Host "--- Running bandit <file>|<dir> --recursive"
if ($isFolder) {
    bandit $project --recursive
}
else {
    bandit $project
}

if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}
Write-Host "All checks passed!"
Write-Host ""

Write-Host "--- Running ruff {check|format} <file> [--fix]"
ruff check $project

if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}
Write-Host ""

Write-Host "--- Running mypy {<file>|<dir>}"
mypy $project

if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}
Write-Host "All checks passed!"
Write-Host ""

Write-Host "--- Running pyflakes {<file>|<dir>}"
pyflakes $project

if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}
Write-Host "All checks passed!"
Write-Host ""

Write-Host "--- Running isort {<file>|<dir>} [--check] [--diff] [--atomic]"
isort $project --check --diff

if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}
Write-Host "All checks passed!"
Write-Host ""

Write-Host "--- Running pylint {<file>|<dir>}"
pylint $project

if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}

Write-Host "--- Running eradicate {<file>|<dir> --recursive} [--aggressive ...]"
if ($isFolder) {
    eradicate $project --recursive --aggressive
}
else {
    eradicate $project --aggressive
}

if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}
Write-Host "All checks passed!"
Write-Host ""

Write-Host "--- Running black {<file>|<dir>} [--check]"
black $project --check

if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}
Write-Host "All checks passed!"
Write-Host ""

Write-Host "--- Running pycodestyle {<file>|<dir>} [--first] [--show-source] [--show-pep8]"
pycodestyle $project --show-source --show-pep8

if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}
Write-Host "All checks passed!"
Write-Host ""

Write-Host "--- Running autopep8 {<file>|<dir> --recursive [--jobs n]} [--diff] [--aggressive ...]"
if ($isFolder) {
    autopep8 $project --recursive --jobs 0 --diff --aggressive
}
else {
    autopep8 $project --diff --aggressive
}

if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}
Write-Host "All checks passed!"
Write-Host ""

Write-Host "--- Running pydocstyle {<file>|<dir>}"
pydocstyle $project

if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}
Write-Host "All checks passed!"
Write-Host ""

Write-Host "--- Running pydoclint {<file>|<dir>} [--quiet]"
pydoclint $project

if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}
Write-Host "All checks passed!"
Write-Host ""

Write-Host "--- Running pydoctest {<file>|<dir>} [--parser {google|numpy|sphinx}]"
if ($isFolder) {
    Push-Location -Path $project
    #pydoctest --parser numpy
    Pop-Location
}
else {
    Write-Warning "pydoctest does not support single file testing"
}

if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}
Write-Host "All checks passed!"
Write-Host ""

Write-Host "--- Running docsig {<file>|<dir>}"
docsig $project

if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}
Write-Host "All checks passed!"
Write-Host ""

Write-Host "--- Running flake8 {<file>|<dir>}"
flake8 $project

if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}
Write-Host "All checks passed!"
Write-Host ""

# Deactivate the environment if it was not active

if (-not $isVirtualEnvActive) {
    deactivate
}
