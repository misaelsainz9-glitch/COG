param([Parameter(Mandatory=$true)][string]$Zip)
$ErrorActionPreference = 'Stop'
trap { $msg = $_.ToString().Replace('%','%25').Replace("`r",'%0D').Replace("`n",'%0A'); Write-Output "::error::$msg"; exit 1 }
Add-Type -AssemblyName System.IO.Compression.FileSystem
$folder = Join-Path $env:RUNNER_TEMP ('extraido con Windows ' + [guid]::NewGuid().ToString('N'))
# Windows PowerShell 5.1/.NET extraction, without any third-party unzip tool.
[IO.Compression.ZipFile]::ExtractToDirectory($Zip,$folder)
$package = Join-Path $folder 'SASISOPA'
$setup = Join-Path $package 'Preparar-paquete.ps1'
$testData = Join-Path $env:RUNNER_TEMP ('datos ZIP normal ' + [guid]::NewGuid().ToString('N'))
function Invoke-Prepare([string]$password) {
    $script = $setup.Replace("'","''"); $data = $testData.Replace("'","''")
    $command = "& '$script' -SinAbrir -Datos '$data' -Clave (ConvertTo-SecureString '$password' -AsPlainText -Force); exit `$LASTEXITCODE"
    $encoded = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($command))
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -EncodedCommand $encoded
    return $LASTEXITCODE
}
# Public fixture password only. Real document passwords never enter this job.
$wrong = @(Invoke-Prepare 'INCORRECTA')[-1]
if ($wrong -eq 0 -or (Test-Path $testData)) { throw 'Wrong password was accepted or changed user data' }
$correct = @(Invoke-Prepare 'PRUEBA-PUBLICA-SIN-DATOS-REALES')[-1]
if ($correct -ne 0) { throw 'Preparation from the ordinary Windows ZIP failed' }
$configFile = Join-Path $testData 'datos_locales\base18.json'
$config = Get-Content $configFile -Raw -Encoding UTF8 | ConvertFrom-Json
$files = @(Get-ChildItem -LiteralPath $config.templates -Filter '*.pdf')
if ($files.Count -ne 18) { throw 'Expected 18 prepared PDFs' }
$before = Get-Content $configFile -Raw -Encoding UTF8
$payload = Join-Path $package 'Componentes\procedimientos.sasisopa'
$stream = [IO.File]::Open($payload,[IO.FileMode]::Append)
try { $stream.WriteByte(0) } finally { $stream.Dispose() }
$damaged = @(Invoke-Prepare 'PRUEBA-PUBLICA-SIN-DATOS-REALES')[-1]
if ($damaged -eq 0 -or (Get-Content $configFile -Raw -Encoding UTF8) -ne $before) { throw 'Damaged content was accepted or changed settings' }
$app = Join-Path $env:LOCALAPPDATA 'Programs\SASISOPA\SASISOPA.exe'
$report = Join-Path $env:RUNNER_TEMP 'comprobacion-zip-normal.json'
$p = Start-Process $app -ArgumentList @('--smoke-test',"`"$report`"") -PassThru
if (!$p.WaitForExit(60000)) { $p.Kill(); throw 'Installed application timed out' }
$p.Refresh()
if ($p.ExitCode -ne 0) { throw 'Installed application failed' }
$result = Get-Content $report -Raw -Encoding UTF8 | ConvertFrom-Json
if (!$result.ok -or !$result.large_blue_signatures -or !$result.manual_attendance) { throw 'Installed application checks failed' }
Write-Output '::notice::Ordinary ZIP extraction in Windows PowerShell 5.1, bundled extractor, password handling, automatic installation, 18 preloaded synthetic PDFs, corrupt-content rejection and installed-app checks passed.'
exit 0
