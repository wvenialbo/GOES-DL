param ([switch]$nobrowser)

& .venv/Scripts/Activate.ps1

if ($nobrowser) {
    jupyter-lab --no-browser
}
else {
    jupyter-lab
}


