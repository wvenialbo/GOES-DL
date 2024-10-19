##
## This script is used to test the dependencies of the project
##

$venv = '.venv'

$pkgs = 'setuptools', 'build', 'wheel', 'pip-tools', 'findpydeps', `
    'pyinstaller', 'flake8', 'black', 'pylint', 'mypy', 'bandit', `
    'ruff', 'eradicate', 'pycodestyle', 'pydocstyle', 'pyright', `
    'pytest', 'pytest-cov', 'pytest-xdist', 'pytest-mock', 'coverage', `
    'flake8-mypy', 'flake8-confusables', 'flake8-black', 'flake8-pylint', `
    'flake8-isort', 'flake8-bandit', 'flake8-eradicate', 'flake8-bugbear', `
    'flake8-builtins', 'flake8-comprehensions', 'flake8-docstrings', `
    'flake8-docstrings-complete', 'flake8-pyproject', 'flake8-ruff', `
    'flake8-annotations', 'darglint2', 'pep8-naming', 'jupyterlab'

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

foreach ($pkg in $pkgs) {
    python -m pip freeze > $before

    python -m pip install --upgrade $pkg
    
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
    
    pip uninstall -y -r $after
}

if (Test-Path -Path $before) {
    Remove-Item $before
    Remove-Item $after
}

if (-not $isVirtualEnvActive) {
    deactivate
}
