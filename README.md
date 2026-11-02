# ToggleMaster

Tech Challenge - Fase 2

Aplicação de feature flags com cinco microsserviços, usando o código-base da [FIAP-TCs](https://github.com/FIAP-TCs).

- **auth:** valida as chaves de acesso.
- **flag:** mantém as flags.
- **targeting:** mantém as regras de avaliação.
- **evaluation:** avalia a flag, usa cache e publica o evento na SQS.
- **analytics:** consome os eventos e grava no DynamoDB.

## Execução local

Copiar `.env.example` para `.env` e preencher a região, uma fila SQS exclusiva de desenvolvimento e as credenciais temporárias de acesso.

```powershell
docker compose up --build -d
docker compose ps
powershell.exe -NoProfile -ExecutionPolicy RemoteSigned -File scripts/smoke.ps1
```

O Compose tem nove serviços: cinco aplicações, dois PostgreSQL, Redis e DynamoDB Local. A SQS fica na AWS. O teste local de 02/11/2026 confirmou os nove contêineres em execução, a avaliação verdadeira e o evento no DynamoDB Local.

No Windows, `INICIAR-FASE2.ps1` reúne a inicialização e a validação dos nove contêineres, da avaliação e do evento no DynamoDB Local. A fila local usa acesso temporário restrito à SQS; a configuração preenchida não entra no Git.

## AWS

O ambiente usa EKS na região `us-east-2`, imagens no ECR, PostgreSQL no RDS, ElastiCache Redis, SQS Standard e DynamoDB. O acesso público passa pelo NLB e pelo NGINX, expondo apenas `/evaluate`. A comunicação interna usa Services ClusterIP.

Os manifestos estão em `k8s/`. Os scripts de implantação e as evidências dos testes ficam em `infra/`. As credenciais ficam nos Secrets do cluster; os serviços acessam a AWS por Pod Identity.

## Testes

O teste funcional confirmou a avaliação e a chegada do evento ao DynamoDB. Na carga de 120 segundos, os HPAs de evaluation e analytics chegaram a cinco réplicas. Foram 40.352 respostas HTTP bem-sucedidas e 112 falhas; o coletor daquela execução não separou as causas.

## Limitações

Foram usados dois RDS: um para auth e outro com databases e usuários distintos para flags e targeting. Essa adaptação é diferente das três instâncias independentes pedidas no enunciado.

O endpoint público do laboratório usa HTTP. O envio de eventos pelo evaluation ainda não tem outbox, e o cache pode atrasar alterações em até 30 segundos. O aumento da quantidade de nós foi manual; o HPA escala apenas os pods.
