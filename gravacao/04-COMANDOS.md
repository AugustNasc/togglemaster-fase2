# Comandos para a gravação

Execute cada bloco na tela indicada. Os caminhos abaixo partem da raiz do projeto. Use o CloudShell para AWS e PowerShell no Windows para o Compose.

## Preparação - antes de gravar

CloudShell:

```sh
cd ~/togglemaster-fase2
python3 gravacao/preparar_aws.py --funcional --nos 3
```

Esse é o caminho da cópia já preparada no CloudShell. No Windows, a cópia separada está na pasta `GRAVACAO-TOGGLEMASTER/projeto`. A conferência precisa terminar com `AMBIENTE AWS CONFERIDO`.

## Cena 2 - Compose no PowerShell

Dentro da pasta `projeto`:

```powershell
docker compose config --services
docker compose ps
powershell -File scripts/smoke.ps1
docker compose exec analytics-service python -c "import app; print(app.dynamodb_client.scan(TableName='ToggleMasterAnalytics')['Count'])"
```

O último comando mostra a quantidade de eventos locais. Execute após o teste e aguarde o consumidor. Se o evento não aparecer, não considere a integração local validada. Antes da gravação, o script `gravacao/validar_local.ps1 -Iniciar` pode fazer a inicialização e a checagem de HTTP. Nunca rode `docker compose config` sem `--services` na gravação: a saída completa pode revelar credenciais do ambiente.

## Cena 3 - EKS no CloudShell

```sh
kubectl get nodes
kubectl get namespaces | head -20
bash gravacao/mostrar_aws.sh
kubectl -n tm-evaluation get configmap app-config
kubectl -n tm-evaluation get hpa evaluation
```

No editor do repositório, abra `k8s/evaluation.json` para mostrar probes, recursos e referência ao Secret. Não abra o conteúdo do Secret real.

## Cena 4 - armazenamento e identidade

```sh
aws rds describe-db-instances --region us-east-2 --query 'DBInstances[].{Nome:DBInstanceIdentifier,Status:DBInstanceStatus,Tipo:DBInstanceClass,Publico:PubliclyAccessible}' --output table
aws elasticache describe-replication-groups --region us-east-2 --query 'ReplicationGroups[].{Nome:ReplicationGroupId,Status:Status,TLS:TransitEncryptionEnabled}' --output table
aws eks list-pod-identity-associations --region us-east-2 --cluster-name togglemaster-fase2 --query 'associations[].{Namespace:namespace,ServiceAccount:serviceAccount}' --output table
```

Mostre os arquivos `infra/evaluation-policy.json` e `infra/analytics-policy.json` no repositório. Eles contêm políticas, não access keys. A saída lista apenas os dois RDS: explique a adaptação, sem contar os databases como instâncias.

## Cena 5 - fluxo ao vivo

```sh
python3 gravacao/preparar_aws.py --funcional
cat gravacao/evidencias-atuais/url-publica.txt
```

Copie a URL impressa para o Chrome. A nova flag foi criada pelo teste; não há chave na URL. Mostre o JSON com `result: true`.

## Cena 6 - duas guias do CloudShell

Guia de observação:

```sh
watch -n 3 'kubectl get hpa -A; kubectl -n tm-evaluation get pods; kubectl -n tm-analytics get pods'
```

Guia da carga, na raiz do projeto:

```sh
python3 gravacao/carga_gravacao.py
```

Espere as métricas atualizarem; observe réplicas desejadas e pods prontos. Não confunda `Pending` com pod disponível. Se não escalar nessa execução, mostre a evidência anterior como um teste anterior e diga isso. Para parar o `watch`, pressione Ctrl+C.

## Cena 7 - fila e tabela

```sh
aws sqs get-queue-attributes --region us-east-2 --queue-url https://sqs.us-east-2.amazonaws.com/699191579246/togglemaster-events --attribute-names ApproximateNumberOfMessages ApproximateNumberOfMessagesNotVisible --output json
cat infra/dynamodb-evidence.json
```

O JSON do DynamoDB é uma coleta anterior com 41.354 eventos. Ele não deve ser apresentado como contagem atual após novos testes. Na aba DynamoDB, abra `ToggleMasterAnalytics` e explore um evento de teste. Não faça scan da tabela inteira repetidamente só para atualizar o número. Os atributos de SQS são aproximados.

## Após gravar

```sh
kubectl get hpa -A
python3 gravacao/preparar_aws.py --nos 2
```

Se o script pedir para aguardar os HPAs voltarem a uma réplica, aguarde. Não force a redução durante a carga.
