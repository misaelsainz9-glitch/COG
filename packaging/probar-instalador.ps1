# Recheck the downloaded release installer, its installed executable and user data.
$ErrorActionPreference = 'Stop'
trap { $msg = $_.ToString().Replace('%','%25').Replace("`r",'%0D').Replace("`n",'%0A'); Write-Output "::error::$msg"; exit 1 }
$installer = (Resolve-Path release/SASISOPA-Instalador-Windows.exe).Path
$installDir = Join-Path $env:RUNNER_TEMP 'SASISOPA instalado'
$dataDir = Join-Path $env:LOCALAPPDATA 'SASISOPA\Datos'
New-Item -ItemType Directory -Path $dataDir -Force | Out-Null
$sentinel = Join-Path $dataDir 'conservar-datos.txt'
Set-Content -Path $sentinel -Value 'DATOS DE PRUEBA NO BORRAR'
function Install-App {
  $p = Start-Process -FilePath $installer -ArgumentList @('/VERYSILENT','/SUPPRESSMSGBOXES','/NORESTART',"/DIR=`"$installDir`"") -PassThru -Wait
  if ($p.ExitCode -ne 0) { throw "Installer failed: $($p.ExitCode)" }
}
function Check-App($name) {
  $report = Join-Path $env:RUNNER_TEMP "$name.json"
  $p = Start-Process -FilePath "$installDir\SASISOPA.exe" -ArgumentList @('--smoke-test',"`"$report`"") -PassThru
  $null = $p.Handle
  if (!$p.WaitForExit(60000)) {
    $p.Kill()
    $detail = if (Test-Path $report) { Get-Content $report -Raw } else { 'No report' }
    $startupLog = Join-Path $dataDir 'error_inicio.txt'
    if (Test-Path $startupLog) { $detail += Get-Content $startupLog -Raw }
    throw "Executable test timed out: $detail"
  }
  $p.Refresh()
  if (Test-Path $report) { $detail = Get-Content $report -Raw; Write-Output $detail } else { $detail = 'No smoke report was created' }
  if ($p.ExitCode -ne 0) { throw $detail }
  if (!(($detail | ConvertFrom-Json).ok)) { throw 'Invalid executable report' }
  Copy-Item $report "release/$name.json"
}
Install-App
Check-App 'comprobacion-instalado'
Install-App
Check-App 'comprobacion-actualizado'
$p = Start-Process -FilePath "$installDir\unins000.exe" -ArgumentList @('/VERYSILENT','/SUPPRESSMSGBOXES','/NORESTART') -PassThru -Wait
if ($p.ExitCode -ne 0) { throw 'Uninstall failed' }
if (Test-Path "$installDir\SASISOPA.exe") { throw 'Executable remained after uninstall' }
if ((Get-Content $sentinel -Raw).Trim() -ne 'DATOS DE PRUEBA NO BORRAR') { throw 'User data changed during install/update/uninstall' }
@{ install=$true; update=$true; uninstall=$true; user_data_preserved=$true } | ConvertTo-Json | Set-Content release/comprobacion-instalador.json
