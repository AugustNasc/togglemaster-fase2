# Relat�rio de entrega - ToggleMaster

Tech Challenge - DevOps e Arquitetura Cloud - Fase 2

Status: vers�o para revis�o. Preencha os dados abaixo antes de enviar.

Participantes: PENDENTE - nome completo, RM e Discord de cada integrante.
Reposit�rio do grupo: https://github.com/AugustNasc/togglemaster-fase2 (privado; liberar acesso para avalia��o).
V�deo (at� 20 minutos): PENDENTE.
Data da execu��o: 02/11/2026.
Ambiente: conta AWS pessoal no plano gratuito, regi�o us-east-2.

## Implementa��o

Partimos dos cinco servi�os disponibilizados pela FIAP-TCs. Criamos imagens Docker com build em m�ltiplos est�gios e usu�rio sem privil�gios, corrigimos falhas de compila��o e depend�ncias e publicamos as imagens no ECR. No EKS, cada servi�o ficou em um namespace, com Service ClusterIP, ConfigMap, Secret, probes e limites de recursos.

O auth valida a chave interna. Flag e targeting armazenam configura��es em PostgreSQL. Evaluation consulta esses servi�os, usa Redis para cache e envia eventos � SQS. Analytics consome a fila e grava no DynamoDB, usando o MessageId como event_id para reentregas da mesma mensagem. Usamos Pod Identity para conceder aos dois servi�os somente as permiss�es necess�rias.

O acesso p�blico passa por um NLB e pelo F5 NGINX Ingress Controller. Apenas /evaluate est� exposto. A administra��o fica interna e � acessada pelo operador com port-forward. Os bancos s�o privados; PostgreSQL e Redis usam conex�es cifradas. O endpoint p�blico de laborat�rio usa HTTP, sem dom�nio e certificado TLS.

## Resultados observados

O teste funcional validou autentica��o, cria��o da flag e da regra, avalia��o verdadeira e chegada do evento ao DynamoDB. Uma chamada HTTP pelo NLB tamb�m retornou a avalia��o esperada a partir do CloudShell. A tentativa no Chrome local permaneceu em uma p�gina de erro; essa valida��o local ainda est� pendente.

Na carga de 120 segundos com 32 clientes, registramos 40.352 respostas HTTP bem-sucedidas e 112 falhas, cerca de 0,28%. O coletor n�o separou as causas das falhas nem mediu lat�ncias. Os HPAs de evaluation e analytics, configurados para 70% de CPU e entre 1 e 5 r�plicas, solicitaram cinco pods cada. Inicialmente houve pods pendentes por falta de capacidade. Aumentamos manualmente o grupo de dois para tr�s n�s t3.small, e os dois servi�os ficaram com cinco pods prontos. Essa amplia��o manual n�o representa autoscaling de n�s.

Al�m da carga, enviamos 1.000 mensagens sint�ticas � fila; os 1.000 eventos foram identificados no DynamoDB. A coleta final encontrou 41.354 eventos na tabela e nenhuma mensagem dispon�vel ou em processamento na SQS. Evid�ncias JSON est�o na pasta infra do projeto.

## Adapta��o dos bancos

O enunciado pede tr�s inst�ncias RDS independentes. A conta gratuita limitou a cria��o a duas. Mantivemos auth_db no primeiro RDS e flags_db e targeting_db em databases e usu�rios distintos no segundo. A separa��o l�gica preserva a execu��o dos servi�os, mas n�o equivale � independ�ncia de tr�s inst�ncias RDS. Essa adapta��o foi adotada para executar o laborat�rio e precisa ser validada com o professor antes da entrega.

## Pend�ncias e limites

O Compose cont�m exatamente nove servi�os: cinco aplica��es, dois PostgreSQL, Redis e DynamoDB Local. A SQS fica na AWS. A execu��o conjunta dos nove cont�ineres ainda precisa ser demonstrada porque o Docker local estava indispon�vel; n�o consideramos essa etapa validada s� pelos builds e pelo teste no EKS.

Os endpoints /health verificam o processo, n�o todas as depend�ncias. O envio de eventos pelo evaluation n�o tem outbox; falhas de envio podem perder eventos. O cache pode atrasar mudan�as de configura��o em at� 30 segundos. Os resultados s�o de laborat�rio e n�o comprovam uma meta de disponibilidade. O node group inicial com t3.medium falhou por restri��o da conta e foi mantido com capacidade zero. H� recursos tempor�rios de bootstrap em tm-setup a remover ap�s confer�ncia.

Faltam preencher os integrantes, liberar acesso de avalia��o ao reposit�rio, concluir a demonstra��o local, gravar o v�deo e inserir seu link. Nenhuma entrega foi enviada � FIAP. O badge Google Cloud Skills Boost � opcional e n�o foi inclu�do.

## Refer�ncias

C�digo-base: https://github.com/FIAP-TCs
Instru��es: POSTECH - Tech Challenge - Fase 2.pdf, fornecido para este projeto.
Evid�ncias: infra/smoke-result.json, infra/public-result.json, infra/load-result.json, infra/cluster-evidence.json e infra/dynamodb-evidence.json.
