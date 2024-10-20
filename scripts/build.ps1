##
## Build a release package for deployment
##

$venv = '.venv'

$tool = $args[0]
$usage = "Usage: build.ps1 {{{build|sdist|wheel}[-n]}|poetry}"

if (-not $tool) {
    Write-Host $usage
    Write-Host ""
    exit
}

# Activate the environment if it is not active

$isVirtualEnvActive = $true

if (-not $env:VIRTUAL_ENV) {
    $isVirtualEnvActive = $false
    & $venv/Scripts/Activate.ps1
}

# Build the package based on user choice

if ($tool -eq 'build') {
    # A source distribution (sdist) is built from {srcdir} and
    # a binary distribution (wheel) is built from the sdist.

    python -m build
}
elseif ($tool -eq 'sdist') {
    # A source distribution (sdist) is built from {srcdir}.

    python -m build --sdist
}
elseif ($tool -eq 'wheel') {
    # A binary distribution (wheel) is built from {srcdir}.

    python -m build --wheel
}
elseif ($tool -eq 'build-n') {
    # A source distribution (sdist) is built from {srcdir} and
    # a binary distribution (wheel) is built from the sdist.
    # Build dependencies must be installed separately.

    python -m build --no-isolation
}
elseif ($tool -eq 'sdist-n') {
    # A source distribution (sdist) is built from {srcdir}.
    # Build dependencies must be installed separately.

    python -m build --sdist --no-isolation
}
elseif ($tool -eq 'wheel-n') {
    # A binary distribution (wheel) is built from {srcdir}.
    # Build dependencies must be installed separately.

    python -m build --wheel --no-isolation
}
elseif ($tool -eq 'build-p') {
    # A source distribution (sdist), as a tarbal, and a
    # binary distribution (wheel) is built using poetry.

    poetry build
}
elseif ($tool -eq 'sdist-p') {
    # A source distribution (sdist) is built using poetry.

    poetry build --format sdist
}
elseif ($tool -eq 'wheel-p') {
    # A binary distribution (wheel) is built using poetry.

    poetry build --format wheel
}
else {
    Write-Host $usage
    Write-Host ""
}

# Deactivate the environment if it was not active

if (-not $isVirtualEnvActive) {
    deactivate
}
