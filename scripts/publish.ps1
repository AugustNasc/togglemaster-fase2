param([Parameter(Mandatory)][string]$Account,[string]$Region="us-east-1",[Parameter(Mandatory)][string]$Tag)
$ErrorActionPreference="Stop"
$registry="$Account.dkr.ecr.$Region.amazonaws.com"
aws ecr get-login-password --region $Region | docker login --username AWS --password-stdin $registry
if($LASTEXITCODE -ne 0){throw "Login falhou"}
foreach($svc in @("auth-service","flag-service","targeting-service","evaluation-service","analytics-service")){
  docker build -t "$registry/${svc}:$Tag" "./$svc"
  if($LASTEXITCODE -ne 0){throw "Build falhou: $svc"}
  docker push "$registry/${svc}:$Tag"
  if($LASTEXITCODE -ne 0){throw "Push falhou: $svc"}
}

