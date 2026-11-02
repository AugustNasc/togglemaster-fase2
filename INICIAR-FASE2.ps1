$ErrorActionPreference='Stop'
Push-Location $PSScriptRoot
try {
    docker info --format '{{.ServerVersion}}' 2>$null | Out-Null
    if($LASTEXITCODE -ne 0){throw 'Sem acesso ao Docker. Execute este arquivo no seu PowerShell com Docker Desktop aberto.'}
    if(-not (Test-Path -LiteralPath '.env')){throw 'O arquivo .env da fase 2 ainda nao foi instalado.'}
    if(Test-Path -LiteralPath 'togglemaster-local-expira.txt'){
        $expiry=[DateTimeOffset]::Parse((Get-Content -LiteralPath 'togglemaster-local-expira.txt' -Raw).Trim())
        if($expiry -lt [DateTimeOffset]::Now.AddMinutes(5)){throw 'A sessao temporaria da SQS expirou ou esta perto de expirar. Renove no CloudShell antes do teste.'}
    }
    docker compose up --build -d
    if($LASTEXITCODE -ne 0){throw 'Falha ao iniciar o Compose.'}
    $end=(Get-Date).AddMinutes(4)
    foreach($port in 8001..8005){
        $ready=$false
        while((Get-Date) -lt $end){
            try {Invoke-RestMethod -Uri "http://127.0.0.1:$port/health" -TimeoutSec 4 | Out-Null; $ready=$true;break}
            catch {Start-Sleep -Seconds 2}
        }
        if(-not $ready){throw "A aplicacao da porta $port nao ficou pronta."}
    }
    $running=@(docker compose ps --services --filter status=running)
    if($running.Count -ne 9){throw "Esperados 9 containers em execucao; encontrados $($running.Count)."}
    & (Join-Path $PSScriptRoot 'scripts\smoke.ps1')
    $smoke=Get-Content -LiteralPath 'local-smoke-result.json' -Raw | ConvertFrom-Json
    $code="import os,sys,boto3; c=boto3.client('dynamodb',region_name=os.environ['AWS_REGION'],endpoint_url=os.environ['DYNAMODB_ENDPOINT_URL']); print(sum(p['Count'] for p in c.get_paginator('scan').paginate(TableName='ToggleMasterAnalytics',Select='COUNT',FilterExpression='#f = :f',ExpressionAttributeNames={'#f':'flag_name'},ExpressionAttributeValues={':f':{'S':sys.argv[1]}})))"
    $found=0
    foreach($attempt in 1..45){
        $value=docker compose exec -T analytics-service python -c $code $smoke.flag
        if($LASTEXITCODE -eq 0 -and [int]::TryParse(($value -join '').Trim(),[ref]$found) -and $found -gt 0){break}
        Start-Sleep -Seconds 2
    }
    if($found -lt 1){throw 'O fluxo HTTP passou, mas o evento nao foi confirmado no DynamoDB Local. Confira os logs do analytics e a validade da sessao AWS.'}
    @{passed=$true;containers=$running.Count;flag=$smoke.flag;dynamodb_events=$found;tested_at=(Get-Date).ToString('o')} | ConvertTo-Json | Set-Content -LiteralPath 'local-validation.json' -Encoding utf8
    docker compose ps
    Write-Host "`nFASE 2 LOCAL VALIDADA: 9 containers, avaliacao true e evento no DynamoDB Local." -ForegroundColor Green
} finally {Pop-Location}
