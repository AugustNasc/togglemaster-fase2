# Checklist para entregar

## Conclu�do e registrado

- [x] Cinco Dockerfiles, imagens constru�das e publicadas no ECR.
- [x] EKS, workers e cinco servi�os dispon�veis.
- [x] PostgreSQL com tr�s databases; Redis com TLS; SQS e DynamoDB.
- [x] Namespaces, ClusterIP, Secrets, ConfigMaps, probes e limites.
- [x] Ingress NGINX e chamada HTTP p�blica pelo CloudShell.
- [x] Smoke test completo at� o DynamoDB.
- [x] HPAs por CPU de evaluation e analytics, escala 1 -> 5 observada.
- [x] Registro dos 112 erros da carga, sem ocultar falhas.
- [x] Lote adicional com 1.000 eventos persistidos; fila drenada.

## Voc� precisa concluir

- [ ] Iniciar Docker e executar os nove servi�os do Compose; gravar `docker compose ps` e o teste local.
- [ ] Confirmar com o professor a adapta��o de dois RDS; o requisito literal � tr�s inst�ncias independentes.
- [x] Criar o reposit�rio privado https://github.com/AugustNasc/togglemaster-fase2.
- [ ] Liberar acesso ao reposit�rio para avalia��o e conferir o conte�do publicado.
- [ ] Preencher nome completo, RM e Discord de todos os integrantes em `RELATORIO.md`.
- [ ] Gravar o v�deo (at� 20 minutos), seguindo `ROTEIRO-VIDEO.md`, e copiar o link acess�vel.
- [ ] Preencher links do reposit�rio e do v�deo, revisar e gerar a vers�o final do relat�rio PDF.
- [ ] Validar abertura do endpoint pela rede usada na grava��o; houve resposta p�blica no CloudShell, mas o Chrome local apresentou erro.
- [ ] Conferir permiss�es de acesso do v�deo/reposit�rio e enviar pela plataforma da FIAP.

## Ap�s a apresenta��o

- [ ] Remover os recursos tempor�rios de bootstrap de `tm-setup` ap�s confer�ncia.
- [ ] Guardar evid�ncias e dados necess�rios e revisar os recursos AWS ativos antes do encerramento.

O PDF incluso � uma vers�o revis�vel. N�o o envie com campos PENDENTE.
