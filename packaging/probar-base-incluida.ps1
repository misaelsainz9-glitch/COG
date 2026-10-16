param([Parameter(Mandatory=$true)][string]$Package)
$ErrorActionPreference = 'Stop'
$testData = Join-Path $env:RUNNER_TEMP 'datos aislados de prueba'
$prepare = Join-Path $Package 'Preparar-SASISOPA.ps1'
& powershell.exe -NoProfile -ExecutionPolicy Bypass -File $prepare -SinAbrir -Datos $testData
if ($LASTEXITCODE -ne 0) { throw 'Automatic install and base preparation failed' }
$configFile = Join-Path $testData 'datos_locales\base18.json'
$config = Get-Content $configFile -Raw -Encoding UTF8 | ConvertFrom-Json
$firstBase = $config.templates
if (@(Get-ChildItem -LiteralPath $firstBase -Filter '*.pdf').Count -ne 18) { throw 'Missing included PDFs' }
$config | Add-Member -NotePropertyName conservar -NotePropertyValue 'valor previo'
[IO.File]::WriteAllText($configFile,($config | ConvertTo-Json),(New-Object Text.UTF8Encoding($false)))
$sentinel = Join-Path $testData 'perfil-existente.txt'
Set-Content $sentinel 'NO BORRAR'
& powershell.exe -NoProfile -ExecutionPolicy Bypass -File $prepare -SinAbrir -SoloPreparar -Datos $testData
if ($LASTEXITCODE -ne 0) { throw 'Repeated preparation failed' }
$config = Get-Content $configFile -Raw -Encoding UTF8 | ConvertFrom-Json
if ($config.templates -ne $firstBase -or $config.conservar -ne 'valor previo') { throw 'Settings were lost on repeat' }
if ((Get-Content $sentinel -Raw).Trim() -ne 'NO BORRAR') { throw 'User files changed' }
Set-Content (Join-Path $firstBase 'PROCEDIMIENTO I.pdf') 'USER MODIFICATION'
& powershell.exe -NoProfile -ExecutionPolicy Bypass -File $prepare -SinAbrir -SoloPreparar -Datos $testData
if ($LASTEXITCODE -ne 0) { throw 'Could not preserve modified previous base' }
$config = Get-Content $configFile -Raw -Encoding UTF8 | ConvertFrom-Json
if ($config.templates -eq $firstBase) { throw 'Modified base was reused' }
if ((Get-Content (Join-Path $firstBase 'PROCEDIMIENTO I.pdf') -Raw).Trim() -ne 'USER MODIFICATION') { throw 'User modification was overwritten' }
$before = Get-Content $configFile -Raw -Encoding UTF8
Set-Content (Join-Path $Package 'Proyecto\plantillas\PROCEDIMIENTO I.pdf') 'DAMAGED PACKAGE'
& powershell.exe -NoProfile -ExecutionPolicy Bypass -File $prepare -SinAbrir -SoloPreparar -Datos $testData
if ($LASTEXITCODE -eq 0) { throw 'Damaged package was accepted' }
if ((Get-Content $configFile -Raw -Encoding UTF8) -ne $before) { throw 'Damaged package changed settings' }
$report = Join-Path $env:RUNNER_TEMP 'programa-instalado-base.json'
$app = Join-Path $env:LOCALAPPDATA 'Programs\SASISOPA\SASISOPA.exe'
$p = Start-Process $app -ArgumentList @('--smoke-test',"`"$report`"") -PassThru
if (!$p.WaitForExit(60000)) { $p.Kill(); throw 'Installed app timed out' }
$p.Refresh()
if ($p.ExitCode -ne 0 -or !(Test-Path $report)) { throw 'Installed app smoke test failed' }
$result = Get-Content $report -Raw -Encoding UTF8 | ConvertFrom-Json
if (!$result.ok -or !$result.large_blue_signatures -or !$result.manual_attendance) { throw 'Installed app report failed' }
Write-Output '::notice::Automatic install, 18 synthetic PDFs, repeat setup, existing settings, modified base preservation, damaged package rejection and installed app checks passed.'
