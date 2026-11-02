# Relatório de entrega - ToggleMaster

Tech Challenge - DevOps e Arquitetura Cloud - Fase 2

Status: versão para revisão. Preencha os dados abaixo antes de enviar.

Integrante único: Augusto Nascimento de Almeida.
RM: 376571.
E-mail FIAP: rm376571@fiap.com.br.
Discord: thecash (nome de exibição: TheCash).
Repositório do grupo: https://github.com/AugustNasc/togglemaster-fase2 (privado; liberar acesso para avaliação).
Vídeo (até 20 minutos): PENDENTE.
Data da execução: 02/11/2026.
Ambiente: conta AWS pessoal no plano gratuito, região us-east-2.

## Implementação

Usei os cinco serviços disponibilizados pela FIAP-TCs. Preparei as imagens Docker com build em múltiplos estágios e usuário sem privilégios, ajustei falhas de compilação e dependências e publiquei as imagens no ECR. No EKS, cada serviço ficou em um namespace, com Service ClusterIP, ConfigMap, Secret, probes e limites de recursos.

O auth valida a chave interna. Flag e targeting armazenam configurações em PostgreSQL. Evaluation consulta esses serviços, usa Redis para cache e envia eventos à SQS. Analytics consome a fila e grava no DynamoDB, usando o MessageId como event_id para reentregas da mesma mensagem. Configurei Pod Identity com permissões separadas para os dois serviços.

O acesso público passa por um NLB e pelo F5 NGINX Ingress Controller. Apenas /evaluate está exposto. A administração fica interna e é acessada pelo operador com port-forward. Os bancos são privados; PostgreSQL e Redis usam conexões cifradas. O endpoint público de laboratório usa HTTP, sem domínio e certificado TLS.

## Resultados observados

O teste funcional validou autenticação, criação da flag e da regra, avaliação verdadeira e chegada do evento ao DynamoDB. Uma chamada HTTP pelo NLB também retornou a avaliação esperada a partir do CloudShell. A tentativa no Chrome local permaneceu em uma página de erro; essa validação local ainda está pendente.

Na carga de 120 segundos com 32 clientes, registrei 40.352 respostas HTTP bem-sucedidas e 112 falhas, cerca de 0,28%. O coletor não separou as causas das falhas nem mediu latências. Os HPAs de evaluation e analytics, configurados para 70% de CPU e entre 1 e 5 réplicas, solicitaram cinco pods cada. Inicialmente houve pods pendentes por falta de capacidade. Aumentei manualmente o grupo de dois para três nós t3.small, e os dois serviços ficaram com cinco pods prontos. Essa ampliação manual não representa autoscaling de nós.

Além da carga, enviei 1.000 mensagens sintéticas à fila; os 1.000 eventos foram identificados no DynamoDB. Aquela coleta encontrou 41.354 eventos na tabela e nenhuma mensagem disponível ou em processamento na SQS. Evidências JSON estão na pasta infra do projeto. Na preparação para a gravação, às 19:48 de 02/11, o teste funcional completo passou novamente, com três nós Ready. Um ensaio adicional do script fez dez chamadas, todas com a resposta esperada. As evidências dessa preparação estão em gravacao/evidencias-atuais.

## Adaptação dos bancos

O enunciado pede três instâncias RDS independentes. A conta gratuita limitou a criação a duas. Mantive auth_db no primeiro RDS e flags_db e targeting_db em databases e usuários distintos no segundo. A separação lógica preserva a execução dos serviços, mas não equivale à independência de três instâncias RDS. Adotei essa adaptação para executar o laboratório; ela precisa ser validada com o professor antes da entrega.

## Pendências e limites

O Compose contém exatamente nove serviços: cinco aplicações, dois PostgreSQL, Redis e DynamoDB Local. A SQS fica na AWS. A execução conjunta dos nove contêineres ainda precisa ser demonstrada; não considerei essa etapa validada só pelos builds e pelo teste no EKS.

Os endpoints /health verificam o processo, não todas as dependências. O envio de eventos pelo evaluation não tem outbox; falhas de envio podem perder eventos. O cache pode atrasar mudanças de configuração em até 30 segundos. Os resultados são de laboratório e não comprovam uma meta de disponibilidade. O node group inicial com t3.medium falhou por restrição da conta e foi mantido com capacidade zero. Há recursos temporários de bootstrap em tm-setup a remover após conferência.

Faltam liberar acesso de avaliação ao repositório, concluir a demonstração local, gravar o vídeo e inserir seu link. Nenhuma entrega foi enviada à FIAP. O badge Google Cloud Skills Boost é opcional e não foi incluído.

## Referências

Código-base: https://github.com/FIAP-TCs
Instruções: POSTECH - Tech Challenge - Fase 2.pdf, fornecido para este projeto.
Evidências: infra/smoke-result.json, infra/public-result.json, infra/load-result.json, infra/cluster-evidence.json e infra/dynamodb-evidence.json.
