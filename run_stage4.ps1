# run_stage4.ps1
# Convenience script to run Stage 4 feature-extractor end-to-end
# Usage: open VS Code integrated PowerShell in project root and run:
#   .\run_stage4.ps1

Set-StrictMode -Version Latest

Write-Output "Running Stage 4 helper script..."

# 1) Move to project root (safe-guard if script invoked from elsewhere)
Set-Location (Split-Path -Parent $MyInvocation.MyCommand.Path)
Write-Output "Working directory: $(Get-Location)"

# 2) Allow script activation for this session only
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned -Force

# 3) Try to activate venv if Activate.ps1 exists
$activate = Join-Path (Get-Location) 'medisign_env\Scripts\Activate.ps1'
if (Test-Path $activate) {
    Write-Output "Activating virtualenv via Activate.ps1"
    & $activate
} else {
    Write-Output "Activate.ps1 not found; will use venv python directly"
}

# 4) Resolve venv python path
$venv_python = Join-Path (Get-Location) 'medisign_env\Scripts\python.exe'
if (-Not (Test-Path $venv_python)) {
    Write-Error "venv python not found at $venv_python. Please check venv name/path."
    exit 10
}
Write-Output "Using venv python: $venv_python"

# 5) Fix protobuf pin
Write-Output "Uninstalling any existing protobuf..."
& $venv_python -m pip uninstall -y protobuf
Write-Output "Installing protobuf==3.20.3"
& $venv_python -m pip install protobuf==3.20.3
Write-Output "Running pip check..."
& $venv_python -m pip check

# 6) Create preprocessed_vtest.npy if missing
$preproc = Join-Path (Get-Location) 'dataset\samples\preprocessed_vtest.npy'
if (-Not (Test-Path $preproc)) {
    Write-Output "Preprocessed file not found; creating from vtest.avi (this may take 10-60s)..."
    & $venv_python - <<'PY'
from modules import preprocessing
import numpy as np, pathlib
p = pathlib.Path('dataset/samples/preprocessed_vtest.npy')
arr = preprocessing.preprocess_video('dataset/samples/vtest.avi', num_frames=60, target_size=(224,224))
np.save(p, arr)
print('Saved', p)
PY
} else {
    Write-Output "Preprocessed file exists: $preproc"
}

# 7) Run feature extractor and tee output to feature_run.txt
$env:TF_CPP_MIN_LOG_LEVEL = '2'
Write-Output "Running MobileNetV2 feature extractor (CPU). Output will be saved to feature_run.txt"
& $venv_python -m modules.feature_extractor --input dataset\samples\preprocessed_vtest.npy --backbone mobilenetv2 --device cpu *>&1 | Tee-Object -FilePath feature_run.txt

Write-Output "Stage 4 run complete. feature_run.txt created in project root. Open and paste its full contents here."
