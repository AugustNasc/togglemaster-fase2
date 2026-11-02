# Checklist para entregar

## Concluído e registrado

- [x] Cinco Dockerfiles, imagens construídas e publicadas no ECR.
- [x] EKS, workers e cinco serviços disponíveis.
- [x] PostgreSQL com três databases; Redis com TLS; SQS e DynamoDB.
- [x] Namespaces, ClusterIP, Secrets, ConfigMaps, probes e limites.
- [x] Ingress NGINX e chamada HTTP pública pelo CloudShell.
- [x] Smoke test completo até o DynamoDB.
- [x] HPAs por CPU de evaluation e analytics, escala 1 -> 5 observada.
- [x] Registro dos 112 erros da carga, sem ocultar falhas.
- [x] Lote adicional com 1.000 eventos persistidos; fila drenada.

## Você precisa concluir

- [ ] Iniciar Docker e executar os nove serviços do Compose; gravar `docker compose ps` e o teste local.
- [ ] Confirmar com o professor a adaptação de dois RDS; o requisito literal é três instâncias independentes.
- [x] Criar o repositório privado https://github.com/AugustNasc/togglemaster-fase2.
- [ ] Liberar acesso ao repositório para avaliação e conferir o conteúdo publicado.
- [x] Integrante único: Augusto Nascimento de Almeida; RM 376571; e-mail rm376571@fiap.com.br; Discord `thecash` (exibição: TheCash).
- [ ] Gravar o vídeo (até 20 minutos), seguindo `ROTEIRO-VIDEO.md`, e copiar o link acessível.
- [ ] Preencher links do repositório e do vídeo, revisar e gerar a versão final do relatório PDF.
- [ ] Validar abertura do endpoint pela rede usada na gravação; houve resposta pública no CloudShell, mas o Chrome local apresentou erro.
- [ ] Conferir permissões de acesso do vídeo/repositório e enviar pela plataforma da FIAP.

## Após a apresentação

- [ ] Remover os recursos temporários de bootstrap de `tm-setup` após conferência.
- [ ] Guardar evidências e dados necessários e revisar os recursos AWS ativos antes do encerramento.

O PDF incluso é uma versão revisável. Não o envie com campos PENDENTE.
