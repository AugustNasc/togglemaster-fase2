param([switch]$Iniciar)
$ErrorActionPreference='Stop'
$project=(Resolve-Path (Join-Path $PSScriptRoot '..')).Path
Push-Location $project
try {
  docker info --format '{{.ServerVersion}}' 2>$null
  if($LASTEXITCODE -ne 0){throw 'Docker indisponivel. Inicie o Docker Desktop com Linux containers.'}
  if(-not (Test-Path -LiteralPath '.env')){throw 'Falta .env. Copie .env.example e preencha uma fila SQS exclusiva local e credenciais temporarias limitadas. Nao use sua senha do console.'}
  $services=@(docker compose config --services)
  if($LASTEXITCODE -ne 0){throw 'Configuracao local incompleta. Nao exiba o .env na gravacao.'}
  if($services.Count -ne 9){throw "Esperados 9 servicos; encontrados $($services.Count)."}
  $services | ForEach-Object {Write-Host $_}
  if($Iniciar){
    docker compose up --build -d
    if($LASTEXITCODE -ne 0){throw 'O Compose nao iniciou. Confira os logs antes de gravar.'}
  }
  $limit=(Get-Date).AddMinutes(3)
  foreach($port in 8001..8005){
    $ok=$false
    while((Get-Date) -lt $limit){
      try {Invoke-RestMethod -Uri "http://127.0.0.1:$port/health" -TimeoutSec 5 | Out-Null; $ok=$true;break}
      catch {Start-Sleep -Seconds 2}
    }
    if(-not $ok){throw "Servico da porta $port nao ficou saudavel."}
  }
  & (Join-Path $project 'scripts\smoke.ps1')
  if(-not $?){throw 'Teste HTTP local falhou.'}
  docker compose ps
  Write-Host 'Nove servicos configurados e fluxo HTTP local validado. Confira separadamente a chegada do evento no DynamoDB Local.'
} finally {Pop-Location}
