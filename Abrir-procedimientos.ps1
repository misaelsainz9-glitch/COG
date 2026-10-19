param([Security.SecureString]$Clave, [switch]$SinAbrir)
$ErrorActionPreference = 'Stop'
$stage = $null
$plain = $null
try {
    $metadata = Get-Content (Join-Path $PSScriptRoot 'Componentes\paquete.json') -Raw -Encoding UTF8 | ConvertFrom-Json
    $payload = Join-Path $PSScriptRoot 'Componentes\procedimientos.sasisopa'
    $tool = Join-Path $PSScriptRoot 'Componentes\7za.exe'
    foreach ($check in @(@($payload, $metadata.payload_sha256), @($tool, $metadata.extractor_sha256))) {
        if ((Get-FileHash -LiteralPath $check[0] -Algorithm SHA256).Hash.ToLower() -ne $check[1]) { throw 'Descarga incompleta o cambiada. Vuelve a descargar y extraer todo el ZIP.' }
    }
    $destination = Join-Path $PSScriptRoot 'DOCUMENTOS'
    if (Test-Path -LiteralPath $destination) { throw 'Ya existe DOCUMENTOS. Abre esa carpeta; no se sobrescribiran tus archivos.' }
    if (!$Clave) { $Clave = Read-Host 'Pega la clave que recibiste en el chat (no se muestra al pegarla) y pulsa Enter' -AsSecureString }
    $plain = (New-Object Net.NetworkCredential('', $Clave)).Password
    if (!$plain) { throw 'La clave no puede estar vacia.' }
    $stage = Join-Path $PSScriptRoot ('.temporal-' + [guid]::NewGuid().ToString('N'))
    New-Item -ItemType Directory -Path $stage | Out-Null
    Write-Host 'Abriendo y comprobando los 18 procedimientos...'
    & $tool x $payload "-o$stage" '-y' "-p$plain" '-bso0' '-bse0' '-bsp0'
    $result = $LASTEXITCODE
    $plain = $null
    if ($result -ne 0) { throw 'No se pudo abrir el contenido. Comprueba la clave, incluido el guion final, y vuelve a intentarlo.' }
    $content = Join-Path $stage 'TENEX'
    $manifest = Get-Content (Join-Path $content '03_REVISION\manifest.json') -Raw -Encoding UTF8 | ConvertFrom-Json
    foreach ($item in $manifest.files) {
        $file = Join-Path $content $item.path
        if ((Get-FileHash -LiteralPath $file -Algorithm SHA256).Hash.ToLower() -ne $item.sha256) { throw 'Un archivo no coincide con su comprobacion. Vuelve a descargar el paquete.' }
    }
    $pdf = Join-Path $content '01_PDF'
    if (@(Get-ChildItem -LiteralPath $pdf -Filter 'PROCEDIMIENTO *.pdf' -File).Count -ne 18) { throw 'No se encontraron los 18 procedimientos completos.' }
    Move-Item -LiteralPath $content -Destination $destination
    Write-Host 'LISTO: los documentos estan en DOCUMENTOS. Lee primero la ficha de datos y pendientes.' -ForegroundColor Green
    if (!$SinAbrir) { Start-Process explorer.exe -ArgumentList ('"' + $destination + '"') }
    exit 0
} catch {
    Write-Host ('ERROR: ' + $_.Exception.Message) -ForegroundColor Red
    exit 1
} finally {
    $plain = $null
    if ($stage -and (Test-Path -LiteralPath $stage)) { Remove-Item -LiteralPath $stage -Recurse -Force -ErrorAction SilentlyContinue }
}
