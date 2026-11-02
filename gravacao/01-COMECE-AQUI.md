# Gravação - ToggleMaster

Augusto Nascimento de Almeida · RM 376571 · Discord thecash

Abra `02-TELEPROMPTER.html` em uma janela separada da janela que será gravada. A fala está dividida em cenas; os comandos ficam em `04-COMANDOS.md`. Não precisa decorar. Leia uma vez e explique acompanhando as telas.

## Antes de apertar gravar

1. No Chrome, mantenha as abas do repositório, EKS, RDS, SQS, DynamoDB e CloudShell.
2. No CloudShell, entre na pasta do projeto e execute `python3 gravacao/preparar_aws.py --funcional --nos 3`. A configuração usa a conta e o cluster já existentes. Não cria outro cluster nem novos bancos. Três nós dão espaço para os pods que os HPAs criarem.
3. Abra a URL mostrada pelo teste. O retorno precisa ser JSON com `result: true`. As rotas de administração precisam continuar retornando 404 externamente.
4. Confira `gravacao/evidencias-atuais/preparacao-aws.json`. Esse arquivo só existe depois de uma conferência bem-sucedida. Os JSON da pasta `infra` são evidências anteriores; não são o estado atual automaticamente.
5. No Windows, execute `powershell -File gravacao/validar_local.ps1 -Iniciar` na cópia do projeto, com Docker e `.env` já configurados. O `.env` usa credenciais AWS temporárias limitadas e uma fila SQS exclusiva local. Senha de login da AWS não serve como access key. Não compartilhe a fila do EKS com o teste local: os consumidores disputariam as mensagens.
6. Para comprovar persistência local, confira o comando do DynamoDB Local em `04-COMANDOS.md`. Não diga que essa parte passou antes de ver o evento.
7. Faça um teste curto de microfone. No gravador, selecione só a janela ou tela que você vai apresentar. O teleprompter fica fora da captura. Não inicie a gravação com senhas, `.env`, console de Secrets ou conversas na tela.

A conferência de 02/11 às 19:48 (horário de São Paulo) passou na AWS com três nós Ready e teste funcional completo. O ensaio dos comandos fez dez chamadas, com dez respostas esperadas e nenhuma falha. A abertura automática da URL pelo Chrome controlado retornou `ERR_BLOCKED_BY_CLIENT`; a requisição HTTP no CloudShell respondeu corretamente. Abra manualmente a URL antes de gravar. Não mude proteções do navegador só para esconder um erro.

## Ordem das cenas

| Cena | Tela | Tempo com a demonstração |
| --- | --- | --- |
| 1 | Repositório e arquitetura | 1 min |
| 2 | Dockerfiles, Compose e terminal local | 3 min |
| 3 | EKS, namespaces, pods e configuração | 3 min |
| 4 | RDS, Redis e permissões | 2 min |
| 5 | Teste funcional e URL pública | 2 min |
| 6 | HPA e carga real | 3 min |
| 7 | SQS e DynamoDB | 2 min |
| 8 | Conclusão e limitações | 1 min |

Reserve até 18 minutos, deixando margem até o limite de 20. A cena de Compose é obrigatória para demonstrar o requisito local. Se ela estiver bloqueada, o vídeo completo ainda não está pronto; a fala tem uma alternativa honesta para um ensaio parcial.

## O que continua diferente do enunciado

Dois RDS hospedam três databases. Isso não equivale a três instâncias independentes. A fala menciona essa adaptação. Ela precisa ser aceita pelo professor ou corrigida em um ambiente que permita a terceira instância.

## Ao terminar

Espere os HPAs voltarem a uma réplica. Execute `python3 gravacao/preparar_aws.py --nos 2` para reduzir novamente o grupo. Não apague bancos nem Secrets durante a gravação. Guarde o vídeo, teste o link de acesso e preencha o relatório antes da entrega. O repositório está privado: ainda será necessário conceder acesso de avaliação ou decidir sua publicação.

## Arquivos de apoio

- `03-FALA.txt`: texto em primeira pessoa, sem comandos misturados à fala.
- `04-COMANDOS.md`: o que executar em cada momento.
- `05-PERGUNTAS.md`: respostas curtas sobre as decisões técnicas.
- `preparar_aws.py`: checagem e teste funcional antes de gravar.
- `carga_gravacao.py`: teste de até 120 segundos, no máximo 32 clientes e 45 mil chamadas.
- `mostrar_aws.sh`: mostra os recursos sem revelar valores de Secrets.
- `validar_local.ps1`: verifica os nove serviços e executa o teste HTTP local.
- `evidencias-atuais/`: resultados de novos testes, quando executados.

No pacote separado, o código completo está em `projeto/`, o relatório em `entrega/` e as evidências anteriores em `evidencias-anteriores/`.
