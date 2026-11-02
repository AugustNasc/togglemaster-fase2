# Roteiro do vídeo - até 20 minutos

O material completo para a gravação, com fala em primeira pessoa e comandos por cena, está em [gravacao/01-COMECE-AQUI.md](../gravacao/01-COMECE-AQUI.md). Abra `gravacao/02-TELEPROMPTER.html` localmente para usar o roteiro com rolagem. Abaixo fica a referência resumida.

Fale com suas palavras e explique o que está mostrando. Evite ler o relatório inteiro.

| Tempo | O que mostrar | Explicação sugerida |
| --- | --- | --- |
| 0-2 min | Arquitetura e cinco serviços | Auth valida a chave; flag e targeting guardam configuração; evaluation decide e publica evento; analytics grava no DynamoDB. |
| 2-5 min | `docker compose config --services`, `docker compose ps`, teste local | São nove contêineres. A fila SQS é real. Só grave como funcionando após executar. |
| 5-8 min | EKS, nodes, namespaces, deployments e ClusterIP | Foram usados t3.small por restrição da conta; o terceiro nó foi adicionado manualmente durante a carga. |
| 8-10 min | NLB, Ingress e chamada `/evaluate` | Só a avaliação está pública; criação de flags/regras é interna, via port-forward. |
| 10-14 min | `infra/load-result.json`, `kubectl get hpa -A`, pods | Carga de 120 s/32 clientes; 40.352 respostas e 112 falhas. Ambos HPAs chegaram a 5. Não atribua causa aos erros sem evidência. |
| 14-17 min | SQS, `infra/dynamodb-evidence.json`, tabela | 1.000 eventos adicionais persistidos; fila drenada; 41.354 itens na coleta. |
| 17-19 min | Dois RDS e três databases; Redis | Explique a adaptação e o desvio: dois databases na mesma instância não equivalem a dois RDS independentes. |
| 19-20 min | Repositório, conclusão e limitações | Pontos pendentes, HTTP público sem TLS, garantia de entrega dos eventos e encerramento do laboratório. |

Comandos úteis, no CloudShell autenticado:

```sh
aws eks update-kubeconfig --region us-east-2 --name togglemaster-fase2
kubectl get nodes
kubectl get deploy -A
kubectl get hpa -A
kubectl top pods -n tm-evaluation
kubectl top pods -n tm-analytics
python3 infra/smoke-test.py
python3 infra/publish-ingress.py
```

Para demonstrar escala ao vivo, abra duas guias do CloudShell: uma com `kubectl get hpa -A -w`, outra com `python3 infra/load-test.py`. Execute apenas quando houver capacidade e tempo para aguardar a estabilização. Não mostre valores de Secrets, arquivos `.env` ou credenciais na gravação.
