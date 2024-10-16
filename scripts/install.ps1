$venv = '.venv'
$vers = 'version.txt'
$reqs = 'installed.txt'

Param($requirements='requirements.txt')

$tool = 'pip', 'pip-tools', 'setuptools', 'build'

python --version
python -m pip --version

if (Test-Path -Path $venv) {
    python -m venv --upgrade $venv
    python -m venv --upgrade-deps $venv
}
else {
    python -m venv --copies $venv
}

& $venv/Scripts/Activate.ps1
python -m pip install --upgrade $tool

python -m pip install --upgrade -r $requirements

python --version > $vers
python -m pip --version >> $vers
python -m pip freeze > $reqs

deactivate
