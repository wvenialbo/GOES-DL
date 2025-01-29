name: PyDocStyle

on: [workflow_dispatch]

jobs:
  pydocstyle:
    name: Documentation linting with PyDocStyle
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.9", "3.10", "3.11", "3.12", "3.13"]
    steps:
    - uses: actions/checkout@v4
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install --upgrade pydocstyle
        pip install -r requirements.txt
    - name: Analysing the code with pydocstyle
      run: |
        pydocstyle "./src/GOES_DL"
