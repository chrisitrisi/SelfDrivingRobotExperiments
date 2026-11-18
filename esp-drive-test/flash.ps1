# Aufruf in PowerShell:  .\flash.ps1          (Port COM6)
#                        .\flash.ps1 COM4     (anderer Port)
param([string]$Port = "COM4")

$env:IDF_PATH = "C:\Espressif\frameworks\esp-idf-v5.1.2"
$env:IDF_PYTHON_ENV_PATH = "C:\Espressif\python_env\idf5.1_py3.11_env"
$env:PATH = "C:\Espressif\tools\idf-python\3.11.2;C:\Espressif\tools\idf-python\3.11.2\Scripts;$env:PATH"
. "$env:IDF_PATH\export.ps1" | Out-Null

Set-Location $PSScriptRoot
& "$env:IDF_PYTHON_ENV_PATH\Scripts\python.exe" "$env:IDF_PATH\tools\idf.py" -p $Port build flash monitor
