param([string]$MasterKey="dev-master-key",[string]$Base="")
$ErrorActionPreference="Stop"
function Url($port,$path) { if ($Base) { return "$Base$path" }; return "http://localhost:$port$path" }
$authPath=if($Base){"/auth/admin/keys"}else{"/admin/keys"}
$key=Invoke-RestMethod -Method Post -Uri (Url 8001 $authPath) -Headers @{Authorization="Bearer $MasterKey"} -ContentType "application/json" -Body '{"name":"smoke"}'
$headers=@{Authorization="Bearer $($key.key)"}
$name="smoke-"+[guid]::NewGuid().ToString("N").Substring(0,8)
Invoke-RestMethod -Method Post -Uri (Url 8002 "/flags") -Headers $headers -ContentType "application/json" -Body (@{name=$name;is_enabled=$true}|ConvertTo-Json) | Out-Null
Invoke-RestMethod -Method Post -Uri (Url 8003 "/rules") -Headers $headers -ContentType "application/json" -Body (@{flag_name=$name;rules=@{type="PERCENTAGE";value=100}}|ConvertTo-Json -Depth 4) | Out-Null
$result=Invoke-RestMethod -Uri (Url 8004 "/evaluate?user_id=smoke-user&flag_name=$name")
if($result.result -ne $true){throw "Avaliacao deveria retornar true"}
@{flag=$name;evaluation=$result;passed=$true} | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $PSScriptRoot '..\local-smoke-result.json') -Encoding utf8
Write-Output "Fluxo HTTP aprovado. Confira separadamente SQS e DynamoDB."

