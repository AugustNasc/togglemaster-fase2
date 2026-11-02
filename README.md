# ToggleMaster - Tech Challenge Fase 2

Cinco microsservi�os da FIAP conteinerizados e implantados na AWS em 02/11/2026. O fluxo de avalia��o at� o DynamoDB foi executado; os dois HPAs escalaram de 1 para 5 r�plicas.

## Estado da entrega

| Item | Resultado |
| --- | --- |
| EKS | `togglemaster-fase2`, regi�o `us-east-2` |
| Workers | `togglemaster-workers-free`, t3.small; 3 n�s usados na carga, retorno para 2 solicitado ap�s estabiliza��o |
| Imagens | Cinco ECR, tag imut�vel `fase2-v2` |
| Aplica��es | Auth, flag e targeting: 1 pod; evaluation e analytics chegaram a 5 pods prontos |
| PostgreSQL | Dois RDS privados, tr�s databases e usu�rios separados |
| Redis | ElastiCache privado com TLS |
| Eventos | SQS Standard -> analytics -> DynamoDB `ToggleMasterAnalytics` |
| Ingress | F5 NGINX + NLB; somente `/evaluate` exposto |
| Credenciais AWS dos pods | EKS Pod Identity, permiss�es por servi�o |

**Desvio do enunciado:** ele pede tr�s inst�ncias RDS independentes. A conta gratuita limitou a cria��o a duas. A adapta��o aprovada mant�m `auth_db` no primeiro RDS e `flags_db`/`targeting_db` em databases e usu�rios distintos no segundo. Funciona, mas n�o atende literalmente ao requisito de tr�s RDS. Confirme a aceita��o com o professor antes de entregar.

Esta � uma conta pessoal no plano gratuito, n�o um Learner Lab da AWS Academy. N�o houve upgrade de plano.

## Testes realizados

- Smoke test: autentica��o da chave interna, cria��o de flag e regra, avalia��o `true` e evento confirmado no DynamoDB.
- Chamada HTTP pelo endere�o p�blico do NLB, a partir do CloudShell: resposta `true`.
- Carga p�blica: 120 segundos, 32 clientes; 40.352 respostas HTTP bem-sucedidas e 112 falhas (aproximadamente 0,28%). O teste registra quantidade de falhas, sem discriminar suas causas ou lat�ncias.
- HPAs por CPU com alvo 70%, m�nimo 1 e m�ximo 5: ambos escalaram. Houve pods pendentes por capacidade e o grupo foi ampliado manualmente de 2 para 3 n�s. Todos os 5 pods de cada servi�o ficaram prontos depois.
- Lote adicional de 1.000 mensagens SQS: todos os 1.000 eventos identificados no DynamoDB.
- Total observado no DynamoDB: 41.354 eventos; fila com zero mensagens dispon�veis e zero em processamento no momento da coleta.

Esses n�meros s�o evid�ncias de laborat�rio, n�o uma garantia de disponibilidade ou desempenho. A evid�ncia da carga e o estado final est�o em `infra/*-result.json` e `infra/*-evidence.json`. O Chrome local permaneceu em uma p�gina de erro durante a tentativa de abrir o endere�o; a valida��o HTTP bem-sucedida veio do CloudShell. N�o foi conclu�da uma valida��o pelo navegador local.

Endpoint demonstrado: [http://k8s-nginxing-togglema-8f6e8dfb5a-abc942c96fbc4fd8.elb.us-east-2.amazonaws.com/evaluate?user_id=public-demo&flag_name=demo-8d8f1648](http://k8s-nginxing-togglema-8f6e8dfb5a-abc942c96fbc4fd8.elb.us-east-2.amazonaws.com/evaluate?user_id=public-demo&flag_name=demo-8d8f1648)

## Organiza��o

- Pastas `*-service`: c�digo de origem e Dockerfiles usados nas imagens v2.
- `docker-compose.yml`: exatamente 9 servi�os para execu��o local.
- `local/`: SQL e cria��o autom�tica da tabela DynamoDB Local.
- `k8s/`: namespaces e objetos das aplica��es, sem valores de Secrets.
- `infra/`: scripts espec�ficos desta conta, permiss�es IAM e evid�ncias reais. Os JSON `k8s-*` s�o fotografias do estado; n�o substituem a instala��o dos controladores com Helm.
- `docs/`: relat�rio edit�vel, checklist e roteiro do v�deo.

## Executar localmente

1. Inicie o Docker Desktop com Linux containers.
2. Copie `.env.example` para `.env`. Use uma fila SQS Standard **exclusiva de desenvolvimento**, regi�o e credenciais tempor�rias com permiss�o SQS. Inclua `AWS_SESSION_TOKEN` quando a sess�o exigir.
3. Execute `docker compose config --services`: devem aparecer 9 servi�os.
4. Execute `docker compose up --build -d` e confira `docker compose ps`.
5. Execute `powershell -File scripts/smoke.ps1`.
6. Confira eventos com `docker compose exec analytics-service python -c "import app; print(app.dynamodb_client.scan(TableName='ToggleMasterAnalytics')['Count'])"`.
7. Para parar: `docker compose down`. Volumes PostgreSQL permanecem; o DynamoDB Local � em mem�ria.

O Compose usa 5 aplica��es, 2 PostgreSQL, Redis e DynamoDB Local. A SQS � real e fica fora desses nove cont�ineres. Flags e targeting t�m databases e usu�rios distintos no PostgreSQL compartilhado. Valores `*_local` e `dev-*` s�o apenas de desenvolvimento. A execu��o dos nove cont�ineres em conjunto ainda precisa ser validada: o Docker local estava indispon�vel. Os cinco builds e o fluxo na AWS foram validados separadamente.

## Reproduzir a implanta��o AWS

Os scripts `infra/` est�o vinculados aos nomes, conta e regi�o usados neste laborat�rio. Leia e adapte antes de usar em outra conta. Eles n�o provisionam toda a infraestrutura do zero e exigem AWS CLI, kubectl, Python com boto3, Helm e acesso administrativo ao cluster.

1. Provisione EKS e workers, cinco ECR, RDS privados, ElastiCache Redis com TLS, fila SQS Standard e tabela DynamoDB on-demand com partition key `event_id` (String). Para cumprir integralmente o enunciado, use tr�s RDS independentes quando o ambiente permitir.
2. Use a mesma VPC. Libere PostgreSQL 5432 e Redis 6379 apenas da rede dos workers. Mantenha sa�da para ECR, SQS e DynamoDB.
3. Execute `aws eks update-kubeconfig --region us-east-2 --name togglemaster-fase2`.
4. Garanta os add-ons VPC CNI, kube-proxy, CoreDNS, Pod Identity Agent e metrics-server. Verifique `kubectl top nodes`.
5. Revise `infra/configure-access.py` antes de executar. Ele cria os pap�is e associa��es de Pod Identity e configura acesso de rede. Evaluation s� envia � fila; analytics consome a fila e escreve na tabela. O controlador AWS administra o NLB.
6. Publique as cinco imagens com `scripts/publish.ps1`. N�o sobrescreva tags imut�veis: use uma nova tag ao mudar c�digo.
7. Execute `python3 infra/bootstrap-databases.py` uma vez. Aguarde os Jobs conclu�rem. O script l� as credenciais mestras do Secrets Manager em mem�ria e cria Secrets internos e databases. Se um Job j� existir, confira seu estado em vez de presumir nova execu��o.
8. Execute `python3 infra/deploy-apps.py`. Aguarde o Job `seed-service-key` concluir e os Deployments ficarem dispon�veis. Os Secrets n�o s�o exportados para o pacote.
9. Instale o AWS Load Balancer Controller com Helm (`aws-load-balancer-controller`, reposit�rio oficial `https://aws.github.io/eks-charts`), usando o ServiceAccount associado, cluster, regi�o e VPC. Foi usado 1 controller; integra��es WAF/Shield ficaram desabilitadas porque n�o fazem parte do laborat�rio.
10. Instale F5 NGINX via `helm upgrade --install nginx oci://ghcr.io/nginx/charts/nginx-ingress --version 2.8.0 --namespace nginx-ingress --create-namespace --set controller.replicaCount=1 --set controller.service.type=ClusterIP`. O NLB � criado pelo Service separado `k8s/public-service.json`; ele usa subnets desta conta.
11. Aplique o Service p�blico e execute `python3 infra/publish-ingress.py`. Aguarde propaga��o DNS e destino saud�vel. Somente `/evaluate` � roteado.
12. Execute `python3 infra/smoke-test.py`. O script usa port-forward para a administra��o interna e n�o imprime a chave. Ele exige permiss�o de leitura da tabela para conferir o evento.
13. Execute `python3 infra/load-test.py` para repetir a carga de 120 segundos. Confira a capacidade antes: dois t3.small foram insuficientes para todas as r�plicas do teste. O m�ximo do node group n�o instala um autoscaler de n�s.

N�o aplique todos os arquivos `infra/*.json` indiscriminadamente. Existem pol�ticas IAM, evid�ncias e snapshots com finalidades diferentes. Para novas imagens, o caminho principal � `infra/deploy-apps.py`; `k8s/` permite revisar os objetos correspondentes. N�o execute simultaneamente HPA e KEDA sobre o mesmo Deployment.

## Seguran�a e limita��es

RDS � privado, conex�es usam `sslmode=require`, Redis usa `rediss://`, pods s�o n�o-root e t�m probes, requests e limits. A chave interna fica em Secret e seu hash no auth. Servi�os administrativos s�o ClusterIP; n�o envie chaves pelo endpoint p�blico HTTP. TLS p�blico com dom�nio/certificado n�o foi configurado.

H� Secrets tempor�rios de bootstrap no namespace `tm-setup`, com credenciais de inicializa��o. Depois de conferir que os Jobs conclu�ram, remova esses recursos tempor�rios pelo procedimento da equipe, sem apagar os Secrets das aplica��es. Eles n�o est�o neste pacote. O node group inicial `togglemaster-workers` falhou no tipo t3.medium e foi mantido com capacidade zero; o grupo em uso � o `togglemaster-workers-free`.

As probes `/health` verificam o processo, n�o todas as depend�ncias. Os eventos do evaluation s�o enviados em goroutines: falhas de envio podem perder eventos, pois n�o h� outbox. Analytics usa MessageId como `event_id`, reduzindo duplica��o em reentregas. O cache dura 30 segundos. Depend�ncias antigas exigem revis�o antes de uso em produ��o.

## O que falta para entregar

Veja `docs/CHECKLIST.md`. O reposit�rio privado � https://github.com/AugustNasc/togglemaster-fase2. Integrante �nico: Augusto Nascimento de Almeida, RM 376571, Discord `thecash`. Restam a demonstra��o local dos 9 cont�ineres, liberar acesso para avalia��o, gravar o v�deo de at� 20 minutos, inserir seu link no relat�rio e confirmar a aceita��o dos dois RDS. N�o envie o relat�rio com campos pendentes. Ap�s a carga, os dois HPAs retornaram automaticamente a uma r�plica; foi solicitado o retorno do grupo para dois n�s.

Os recursos AWS continuam ativos e consomem cr�ditos. Ap�s concluir a grava��o e guardar o necess�rio, revise o invent�rio antes de desativar o ambiente. N�o apague bancos sem avaliar seus dados.
