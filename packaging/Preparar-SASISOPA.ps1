param([switch]$SinAbrir, [switch]$SoloPreparar, [string]$Datos)
$ErrorActionPreference = 'Stop'
trap { Write-Host ('ERROR: ' + $_.Exception.Message) -ForegroundColor Red; exit 1 }
if (!$Datos) { $Datos = Join-Path $env:LOCALAPPDATA 'SASISOPA\Datos' }
$source = Join-Path $PSScriptRoot 'Proyecto\plantillas'
$manifestFile = Join-Path $PSScriptRoot 'procedimientos-incluidos.json'
$manifest = Get-Content $manifestFile -Raw -Encoding UTF8 | ConvertFrom-Json
if ($manifest.documents.Count -ne 18 -or ($manifest.documents | Measure-Object pages -Sum).Sum -ne 523) { throw 'La base debe contener 18 procedimientos y 523 paginas.' }
if (@($manifest.documents.filename | Select-Object -Unique).Count -ne 18) { throw 'Hay documentos duplicados.' }
function Test-Base([string]$folder) {
    foreach ($doc in $manifest.documents) {
        if ([IO.Path]::GetFileName($doc.filename) -ne $doc.filename -or $doc.filename -notmatch '^PROCEDIMIENTO [IVX]+\.pdf$') { throw 'Nombre de documento invalido.' }
        $file = Join-Path $folder $doc.filename
        if (!(Test-Path -LiteralPath $file -PathType Leaf)) { return $false }
        if ((Get-FileHash -LiteralPath $file -Algorithm SHA256).Hash.ToLower() -ne $doc.sha256) { return $false }
    }
    return $true
}
if (!(Test-Base $source)) { throw 'Falta un procedimiento o no coincide con la base verificada. Extrae de nuevo el ZIP completo.' }
$installer = Join-Path $PSScriptRoot 'SASISOPA-Instalador-Windows.exe'
if (!$SoloPreparar) {
    if ((Get-FileHash -LiteralPath $installer -Algorithm SHA256).Hash.ToLower() -ne $manifest.installer_sha256) { throw 'El instalador no coincide con el verificado.' }
    $appDir = Join-Path $env:LOCALAPPDATA 'Programs\SASISOPA'
    $process = Start-Process -FilePath $installer -ArgumentList @('/VERYSILENT','/SUPPRESSMSGBOXES','/NORESTART',"/DIR=`"$appDir`"") -PassThru -Wait
    if ($process.ExitCode -ne 0) { throw "La instalacion fallo: $($process.ExitCode)" }
}
$baseParent = Join-Path $Datos 'plantillas-incluidas'
New-Item -ItemType Directory -Path $baseParent -Force | Out-Null
$baseId = (Get-FileHash -LiteralPath $manifestFile -Algorithm SHA256).Hash.Substring(0,12).ToLower()
$destination = Join-Path $baseParent "base-$baseId"
if ((Test-Path -LiteralPath $destination) -and !(Test-Base $destination)) { $destination += '-' + [guid]::NewGuid().ToString('N').Substring(0,8) }
if (!(Test-Path -LiteralPath $destination)) {
    $stage = Join-Path $baseParent ('preparando-' + [guid]::NewGuid().ToString('N'))
    try {
        New-Item -ItemType Directory -Path $stage | Out-Null
        foreach ($doc in $manifest.documents) { Copy-Item -LiteralPath (Join-Path $source $doc.filename) -Destination $stage }
        if (!(Test-Base $stage)) { throw 'La copia de los procedimientos no paso la comprobacion.' }
        Move-Item -LiteralPath $stage -Destination $destination
    } finally { if (Test-Path -LiteralPath $stage) { Remove-Item -LiteralPath $stage -Recurse -Force } }
}
$settingsDir = Join-Path $Datos 'datos_locales'
New-Item -ItemType Directory -Path $settingsDir -Force | Out-Null
$settings = Join-Path $settingsDir 'base18.json'
$config = [pscustomobject]@{}
if (Test-Path -LiteralPath $settings) {
    Copy-Item -LiteralPath $settings -Destination ($settings + '.anterior-' + [guid]::NewGuid().ToString('N'))
    try { $loaded = Get-Content $settings -Raw -Encoding UTF8 | ConvertFrom-Json; if ($loaded -is [pscustomobject]) { $config = $loaded } } catch { }
}
$config | Add-Member -MemberType NoteProperty -Name templates -Value $destination -Force
$temporary = $settings + '.nuevo-' + [guid]::NewGuid().ToString('N')
try {
    [IO.File]::WriteAllText($temporary,($config | ConvertTo-Json -Depth 20),(New-Object Text.UTF8Encoding($false)))
    Move-Item -LiteralPath $temporary -Destination $settings -Force
} finally { if (Test-Path -LiteralPath $temporary) { Remove-Item -LiteralPath $temporary -Force } }
Write-Host 'LISTO: 18 procedimientos y 523 paginas cargados.' -ForegroundColor Green
if (!$SinAbrir -and !$SoloPreparar) { Start-Process -FilePath (Join-Path $appDir 'SASISOPA.exe') }
