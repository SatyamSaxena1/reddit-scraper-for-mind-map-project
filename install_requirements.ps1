# PowerShell helper to create venv and install requirements
$venv = "$PWD\.venv"
python -m venv $venv
Write-Host "Activating venv..."
& "$venv\Scripts\Activate.ps1"
Write-Host "Installing requirements..."
python -m pip install -r requirements.txt
Write-Host "Done. Activate the venv with: & .\\.venv\\Scripts\\Activate.ps1"
