# ToggleMaster - Tech Challenge Fase 2

Para gravar a apresentação, comece por [gravacao/01-COMECE-AQUI.md](gravacao/01-COMECE-AQUI.md). A pasta reúne a fala em primeira pessoa, o teleprompter, os comandos e a conferência do ambiente. O roteiro completo da gravação está nessa pasta.

Cinco microsserviços da FIAP conteinerizados e implantados na AWS em 02/11/2026. O fluxo de avaliação até o DynamoDB foi executado; os dois HPAs escalaram de 1 para 5 réplicas.

## Estado da entrega

| Item | Resultado |
| --- | --- |
| EKS | `togglemaster-fase2`, região `us-east-2` |
| Workers | `togglemaster-workers-free`, t3.small; 3 nós usados na carga, retorno para 2 solicitado após estabilização |
| Imagens | Cinco ECR, tag imutável `fase2-v2` |
| Aplicações | Auth, flag e targeting: 1 pod; evaluation e analytics chegaram a 5 pods prontos |
| PostgreSQL | Dois RDS privados, três databases e usuários separados |
| Redis | ElastiCache privado com TLS |
| Eventos | SQS Standard -> analytics -> DynamoDB `ToggleMasterAnalytics` |
| Ingress | F5 NGINX + NLB; somente `/evaluate` exposto |
| Credenciais AWS dos pods | EKS Pod Identity, permissões por serviço |

**Desvio do enunciado:** ele pede três instâncias RDS independentes. A conta gratuita limitou a criação a duas. A adaptação aprovada mantém `auth_db` no primeiro RDS e `flags_db`/`targeting_db` em databases e usuários distintos no segundo. Funciona, mas não atende literalmente ao requisito de três RDS. Confirme a aceitação com o professor antes de entregar.

Esta é uma conta pessoal no plano gratuito, não um Learner Lab da AWS Academy. Não houve upgrade de plano.

## Testes realizados

- Smoke test: autenticação da chave interna, criação de flag e regra, avaliação `true` e evento confirmado no DynamoDB.
- Chamada HTTP pelo endereço público do NLB, a partir do CloudShell: resposta `true`.
- Carga pública: 120 segundos, 32 clientes; 40.352 respostas HTTP bem-sucedidas e 112 falhas (aproximadamente 0,28%). O teste registra quantidade de falhas, sem discriminar suas causas ou latências.
- HPAs por CPU com alvo 70%, mínimo 1 e máximo 5: ambos escalaram. Houve pods pendentes por capacidade e o grupo foi ampliado manualmente de 2 para 3 nós. Todos os 5 pods de cada serviço ficaram prontos depois.
- Lote adicional de 1.000 mensagens SQS: todos os 1.000 eventos identificados no DynamoDB.
- Total observado no DynamoDB: 41.354 eventos; fila com zero mensagens disponíveis e zero em processamento no momento da coleta.

Esses números são evidências de laboratório, não uma garantia de disponibilidade ou desempenho. A evidência da carga e o estado final estão em `infra/*-result.json` e `infra/*-evidence.json`. O Chrome local permaneceu em uma página de erro durante a tentativa de abrir o endereço; a validação HTTP bem-sucedida veio do CloudShell. Não foi concluída uma validação pelo navegador local.

Endpoint demonstrado: [http://k8s-nginxing-togglema-8f6e8dfb5a-abc942c96fbc4fd8.elb.us-east-2.amazonaws.com/evaluate?user_id=public-demo&flag_name=demo-8d8f1648](http://k8s-nginxing-togglema-8f6e8dfb5a-abc942c96fbc4fd8.elb.us-east-2.amazonaws.com/evaluate?user_id=public-demo&flag_name=demo-8d8f1648)

## Organização

- Pastas `*-service`: código de origem e Dockerfiles usados nas imagens v2.
- `docker-compose.yml`: exatamente 9 serviços para execução local.
- `local/`: SQL e criação automática da tabela DynamoDB Local.
- `k8s/`: namespaces e objetos das aplicações, sem valores de Secrets.
- `infra/`: scripts específicos desta conta, permissões IAM e evidências reais. Os JSON `k8s-*` são fotografias do estado; não substituem a instalação dos controladores com Helm.
- `docs/`: relatório editável, checklist e roteiro do vídeo.

## Executar localmente

1. Inicie o Docker Desktop com Linux containers.
2. Copie `.env.example` para `.env`. Use uma fila SQS Standard **exclusiva de desenvolvimento**, região e credenciais temporárias com permissão SQS. Inclua `AWS_SESSION_TOKEN` quando a sessão exigir.
3. Execute `docker compose config --services`: devem aparecer 9 serviços.
4. Execute `docker compose up --build -d` e confira `docker compose ps`.
5. Execute `powershell -File scripts/smoke.ps1`.
6. Confira eventos com `docker compose exec analytics-service python -c "import app; print(app.dynamodb_client.scan(TableName='ToggleMasterAnalytics')['Count'])"`.
7. Para parar: `docker compose down`. Volumes PostgreSQL permanecem; o DynamoDB Local é em memória.

O Compose usa 5 aplicações, 2 PostgreSQL, Redis e DynamoDB Local. A SQS é real e fica fora desses nove contêineres. Flags e targeting têm databases e usuários distintos no PostgreSQL compartilhado. Valores `*_local` e `dev-*` são apenas de desenvolvimento. A execução dos nove contêineres em conjunto ainda precisa ser validada: o Docker local estava indisponível. Os cinco builds e o fluxo na AWS foram validados separadamente.

## Reproduzir a implantação AWS

Os scripts `infra/` estão vinculados aos nomes, conta e região usados neste laboratório. Leia e adapte antes de usar em outra conta. Eles não provisionam toda a infraestrutura do zero e exigem AWS CLI, kubectl, Python com boto3, Helm e acesso administrativo ao cluster.

1. Provisione EKS e workers, cinco ECR, RDS privados, ElastiCache Redis com TLS, fila SQS Standard e tabela DynamoDB on-demand com partition key `event_id` (String). Para cumprir integralmente o enunciado, use três RDS independentes quando o ambiente permitir.
2. Use a mesma VPC. Libere PostgreSQL 5432 e Redis 6379 apenas da rede dos workers. Mantenha saída para ECR, SQS e DynamoDB.
3. Execute `aws eks update-kubeconfig --region us-east-2 --name togglemaster-fase2`.
4. Garanta os add-ons VPC CNI, kube-proxy, CoreDNS, Pod Identity Agent e metrics-server. Verifique `kubectl top nodes`.
5. Revise `infra/configure-access.py` antes de executar. Ele cria os papéis e associações de Pod Identity e configura acesso de rede. Evaluation só envia à fila; analytics consome a fila e escreve na tabela. O controlador AWS administra o NLB.
6. Publique as cinco imagens com `scripts/publish.ps1`. Não sobrescreva tags imutáveis: use uma nova tag ao mudar código.
7. Execute `python3 infra/bootstrap-databases.py` uma vez. Aguarde os Jobs concluírem. O script lê as credenciais mestras do Secrets Manager em memória e cria Secrets internos e databases. Se um Job já existir, confira seu estado em vez de presumir nova execução.
8. Execute `python3 infra/deploy-apps.py`. Aguarde o Job `seed-service-key` concluir e os Deployments ficarem disponíveis. Os Secrets não são exportados para o pacote.
9. Instale o AWS Load Balancer Controller com Helm (`aws-load-balancer-controller`, repositório oficial `https://aws.github.io/eks-charts`), usando o ServiceAccount associado, cluster, região e VPC. Foi usado 1 controller; integrações WAF/Shield ficaram desabilitadas porque não fazem parte do laboratório.
10. Instale F5 NGINX via `helm upgrade --install nginx oci://ghcr.io/nginx/charts/nginx-ingress --version 2.8.0 --namespace nginx-ingress --create-namespace --set controller.replicaCount=1 --set controller.service.type=ClusterIP`. O NLB é criado pelo Service separado `k8s/public-service.json`; ele usa subnets desta conta.
11. Aplique o Service público e execute `python3 infra/publish-ingress.py`. Aguarde propagação DNS e destino saudável. Somente `/evaluate` é roteado.
12. Execute `python3 infra/smoke-test.py`. O script usa port-forward para a administração interna e não imprime a chave. Ele exige permissão de leitura da tabela para conferir o evento.
13. Execute `python3 infra/load-test.py` para repetir a carga de 120 segundos. Confira a capacidade antes: dois t3.small foram insuficientes para todas as réplicas do teste. O máximo do node group não instala um autoscaler de nós.

Não aplique todos os arquivos `infra/*.json` indiscriminadamente. Existem políticas IAM, evidências e snapshots com finalidades diferentes. Para novas imagens, o caminho principal é `infra/deploy-apps.py`; `k8s/` permite revisar os objetos correspondentes. Não execute simultaneamente HPA e KEDA sobre o mesmo Deployment.

## Segurança e limitações

RDS é privado, conexões usam `sslmode=require`, Redis usa `rediss://`, pods são não-root e têm probes, requests e limits. A chave interna fica em Secret e seu hash no auth. Serviços administrativos são ClusterIP; não envie chaves pelo endpoint público HTTP. TLS público com domínio/certificado não foi configurado.

Há Secrets temporários de bootstrap no namespace `tm-setup`, com credenciais de inicialização. Depois de conferir que os Jobs concluíram, remova esses recursos temporários pelo procedimento da equipe, sem apagar os Secrets das aplicações. Eles não estão neste pacote. O node group inicial `togglemaster-workers` falhou no tipo t3.medium e foi mantido com capacidade zero; o grupo em uso é o `togglemaster-workers-free`.

As probes `/health` verificam o processo, não todas as dependências. Os eventos do evaluation são enviados em goroutines: falhas de envio podem perder eventos, pois não há outbox. Analytics usa MessageId como `event_id`, reduzindo duplicação em reentregas. O cache dura 30 segundos. Dependências antigas exigem revisão antes de uso em produção.

## O que falta para entregar

Veja `docs/CHECKLIST.md`. O repositório privado é https://github.com/AugustNasc/togglemaster-fase2. Integrante único: Augusto Nascimento de Almeida, RM 376571, Discord `thecash`. Restam a demonstração local dos 9 contêineres, liberar acesso para avaliação, gravar o vídeo de até 20 minutos, inserir seu link no relatório e confirmar a aceitação dos dois RDS. Não envie o relatório com campos pendentes. Após a carga, os dois HPAs retornaram automaticamente a uma réplica; foi solicitado o retorno do grupo para dois nós.

Os recursos AWS continuam ativos e consomem créditos. Após concluir a gravação e guardar o necessário, revise o inventário antes de desativar o ambiente. Não apague bancos sem avaliar seus dados.
