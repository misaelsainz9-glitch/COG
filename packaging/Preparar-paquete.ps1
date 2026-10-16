param([Security.SecureString]$Clave, [switch]$SinAbrir, [string]$Datos)
$ErrorActionPreference = 'Stop'
$stage = $null
$complete = $false
try {
    $metadata = Get-Content (Join-Path $PSScriptRoot 'Componentes\paquete.json') -Raw -Encoding UTF8 | ConvertFrom-Json
    $payload = Join-Path $PSScriptRoot 'Componentes\procedimientos.sasisopa'
    $tool = Join-Path $PSScriptRoot 'Componentes\7za.exe'
    if ((Get-FileHash -LiteralPath $payload -Algorithm SHA256).Hash.ToLower() -ne $metadata.payload_sha256) { throw 'La descarga esta incompleta o cambiada. Vuelve a descargar y extraer todo el ZIP.' }
    if ((Get-FileHash -LiteralPath $tool -Algorithm SHA256).Hash.ToLower() -ne $metadata.extractor_sha256) { throw 'Falta un componente o esta cambiado. Extrae todo el ZIP de nuevo.' }
    if (!$Clave) { $Clave = Read-Host 'Copia la contrasena que recibiste en el chat (no se mostrara al pegarla)' -AsSecureString }
    $plain = (New-Object Net.NetworkCredential('', $Clave)).Password
    if (!$plain) { throw 'La contrasena no puede estar vacia.' }
    $parent = Join-Path $env:LOCALAPPDATA 'SASISOPA\Paquetes'
    $stage = Join-Path $parent ('contenido-' + [guid]::NewGuid().ToString('N'))
    New-Item -ItemType Directory -Path $stage -Force | Out-Null
    Write-Host 'Preparando los documentos. Espera un momento...'
    & $tool x $payload "-o$stage" '-y' "-p$plain" '-bso0' '-bse0' '-bsp0'
    $code = $LASTEXITCODE
    $plain = $null
    if ($code -ne 0) { throw 'No se pudo abrir el contenido protegido. Verifica la contrasena, incluido el guion final, e intentalo otra vez.' }
    $setup = Join-Path $stage 'SASISOPA\Preparar-SASISOPA.ps1'
    if (!(Test-Path -LiteralPath $setup -PathType Leaf)) { throw 'El paquete no contiene el preparador esperado.' }
    $arguments = @('-NoProfile','-ExecutionPolicy','Bypass','-File',$setup)
    if ($SinAbrir) { $arguments += '-SinAbrir' }
    if ($Datos) { $arguments += @('-Datos',$Datos) }
    & powershell.exe @arguments
    if ($LASTEXITCODE -ne 0) { throw 'No se completo la instalacion. Revisa el mensaje anterior.' }
    $complete = $true
    Write-Host 'LISTO. Programa instalado y 18 procedimientos cargados.' -ForegroundColor Green
    exit 0
} catch {
    Write-Host ('ERROR: ' + $_.Exception.Message) -ForegroundColor Red
    exit 1
} finally {
    $plain = $null
    if ($stage -and !$complete -and (Test-Path -LiteralPath $stage)) { Remove-Item -LiteralPath $stage -Recurse -Force -ErrorAction SilentlyContinue }
}
