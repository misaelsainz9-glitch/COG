$ErrorActionPreference = 'Stop'
$root = Join-Path $env:RUNNER_TEMP 'Apertura con espacios y acentos á'
python fixture.py $root
if ($LASTEXITCODE -ne 0) { throw 'Synthetic fixture failed' }
$correct = Join-Path $root 'Extraido con Windows'
Expand-Archive -LiteralPath (Join-Path $root 'normal.zip') -DestinationPath $correct
$wrong = Join-Path $root 'Clave incorrecta'
$corrupt = Join-Path $root 'Descarga cambiada'
$missing = Join-Path $root 'Sin componente'
Copy-Item -LiteralPath $correct -Destination $wrong -Recurse
Copy-Item -LiteralPath $correct -Destination $corrupt -Recurse
Copy-Item -LiteralPath $correct -Destination $missing -Recurse
function Invoke-Opener([string]$folder, [string]$password) {
    $script = Join-Path $folder 'Abrir-procedimientos.ps1'
    $command = "& '$($script.Replace("'","''"))' -SinAbrir -Clave (ConvertTo-SecureString '$password' -AsPlainText -Force)"
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -Command $command
    return $LASTEXITCODE
}
# Save the native program output separately from its return code.
function Check-Opener([string]$folder,[string]$password,[bool]$success) {
    $result = @(Invoke-Opener $folder $password)
    $code = $result[-1]
    $result | ForEach-Object { Write-Host $_ }
    if ($success -and $code -ne 0) { throw "Expected success: $code" }
    if (!$success -and $code -eq 0) { throw 'Expected a rejected operation' }
    if (Get-ChildItem -LiteralPath $folder -Force -Filter '.temporal-*') { throw 'Temporary plaintext folder left behind' }
}
Check-Opener $correct 'PRUEBA-PUBLICA-SIN-DATOS-REALES' $true
$docs = Join-Path $correct 'DOCUMENTOS'
if (@(Get-ChildItem -LiteralPath (Join-Path $docs '01_PDF') -Filter 'PROCEDIMIENTO *.pdf').Count -ne 18) { throw 'Expected 18 PDFs' }
$manifest = Get-Content (Join-Path $docs '03_REVISION\manifest.json') -Raw -Encoding UTF8 | ConvertFrom-Json
foreach ($file in $manifest.files) {
    if ((Get-FileHash (Join-Path $docs $file.path) -Algorithm SHA256).Hash.ToLower() -ne $file.sha256) { throw 'Extracted file differs' }
}
Check-Opener $wrong 'CLAVE-PUBLICA-EQUIVOCADA' $false
if (Test-Path (Join-Path $wrong 'DOCUMENTOS')) { throw 'Wrong key produced output' }
[IO.File]::AppendAllText((Join-Path $corrupt 'Componentes\procedimientos.sasisopa'),'ALTERADO')
Check-Opener $corrupt 'PRUEBA-PUBLICA-SIN-DATOS-REALES' $false
if (Test-Path (Join-Path $corrupt 'DOCUMENTOS')) { throw 'Changed payload produced output' }
Remove-Item (Join-Path $missing 'Componentes\7za.exe')
Check-Opener $missing 'PRUEBA-PUBLICA-SIN-DATOS-REALES' $false
if (Test-Path (Join-Path $missing 'DOCUMENTOS')) { throw 'Missing component produced output' }
$before = (Get-FileHash (Join-Path $docs '01_PDF\SASISOPA_UNIDO.pdf') -Algorithm SHA256).Hash
Check-Opener $correct 'PRUEBA-PUBLICA-SIN-DATOS-REALES' $false
if ((Get-FileHash (Join-Path $docs '01_PDF\SASISOPA_UNIDO.pdf') -Algorithm SHA256).Hash -ne $before) { throw 'Existing documents were modified' }
@{ passed=$true; native_windows_powershell_5=$true; synthetic_documents=$true; no_private_key_or_private_documents=$true; ordinary_windows_zip_extraction=$true; correct_key=$true; wrong_key_rejected=$true; corrupt_payload_rejected=$true; missing_component_rejected=$true; existing_output_preserved=$true; no_plaintext_residue_on_failure=$true; wrapper_sha256=(Get-FileHash 'Abrir-procedimientos.ps1' -Algorithm SHA256).Hash.ToLower() } | ConvertTo-Json | Set-Content 'resultado-windows.json' -Encoding UTF8
