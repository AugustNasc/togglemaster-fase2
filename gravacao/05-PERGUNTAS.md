# Se perguntarem sobre as decisões

**Por que PostgreSQL e DynamoDB?**
As configurações e chaves têm estrutura relacional e restrições de unicidade. Os eventos de avaliação são registros independentes, escritos pelo consumidor no DynamoDB. A escolha acompanha o fluxo dos serviços fornecidos.

**Por que Redis?**
Para guardar em cache os dados usados na avaliação e reduzir consultas repetidas. O cache tem duração de 30 segundos, então uma alteração pode demorar esse intervalo para aparecer.

**Por que SQS?**
A avaliação publica o evento e o analytics pode processar depois. Isso desacopla os dois serviços. A fila Standard pode reentregar mensagens; usar o MessageId como chave evita um novo item para a reentrega da mesma mensagem. Isso não torna todas as operações do sistema exactly-once.

**Por que os dois HPAs usam CPU?**
Foi a opção aplicada no laboratório. Os dois chegaram a cinco réplicas no teste anterior. No analytics, profundidade da fila seria uma métrica mais próxima da demanda; KEDA seria uma alternativa. Não foi instalado KEDA neste ambiente.

**Os nós escalam automaticamente?**
Não. O grupo tem limites de 1 a 4, mas isso não instala um autoscaler de nós. O terceiro nó foi adicionado manualmente para dar espaço aos pods. O HPA escala pods.

**Por que só dois RDS?**
A conta não permitiu criar a terceira instância. Auth usa uma instância; flags e targeting usam databases e usuários separados na outra. É uma adaptação funcional, mas diferente das três instâncias independentes exigidas. A aceitação dessa mudança depende do professor.

**O que fica público?**
Só `/evaluate`, passando por NLB e NGINX. Os endpoints de administração ficam em ClusterIP, acessados pelo operador com port-forward. O endpoint público do laboratório é HTTP e não tem certificado TLS.

**Onde estão as credenciais?**
As credenciais de banco e a chave interna ficam nos Secrets do Kubernetes. O acesso AWS dos serviços usa Pod Identity, com permissões separadas. Os arquivos do repositório só têm referências; os valores reais não estão no pacote de gravação.

**A probe garante acesso ao banco?**
Não. `/health` mostra que o processo responde. O teste funcional é que verifica o fluxo entre os serviços e a chegada de um evento à tabela.

**O teste passou sem erro?**
Não. No teste anterior houve 40.352 respostas HTTP bem-sucedidas e 112 falhas. O coletor antigo não registrou a causa dessas falhas. O roteiro não trata esse resultado como garantia de disponibilidade.

**Qual melhoria faria primeiro?**
Garantia de publicação de eventos com uma estratégia como outbox, TLS no endpoint público e escala do analytics orientada à fila. Também separar o terceiro RDS quando o ambiente permitir, para atender ao desenho pedido.
