# Roteiro do v�deo - at� 20 minutos

Fale com suas palavras e explique o que est� mostrando. Evite ler o relat�rio inteiro.

| Tempo | O que mostrar | Explica��o sugerida |
| --- | --- | --- |
| 0-2 min | Arquitetura e cinco servi�os | Auth valida a chave; flag e targeting guardam configura��o; evaluation decide e publica evento; analytics grava no DynamoDB. |
| 2-5 min | `docker compose config --services`, `docker compose ps`, teste local | S�o nove cont�ineres. A fila SQS � real. S� grave como funcionando ap�s executar. |
| 5-8 min | EKS, nodes, namespaces, deployments e ClusterIP | Foram usados t3.small por restri��o da conta; o terceiro n� foi adicionado manualmente durante a carga. |
| 8-10 min | NLB, Ingress e chamada `/evaluate` | S� a avalia��o est� p�blica; cria��o de flags/regras � interna, via port-forward. |
| 10-14 min | `infra/load-result.json`, `kubectl get hpa -A`, pods | Carga de 120 s/32 clientes; 40.352 respostas e 112 falhas. Ambos HPAs chegaram a 5. N�o atribua causa aos erros sem evid�ncia. |
| 14-17 min | SQS, `infra/dynamodb-evidence.json`, tabela | 1.000 eventos adicionais persistidos; fila drenada; 41.354 itens na coleta. |
| 17-19 min | Dois RDS e tr�s databases; Redis | Explique a adapta��o e o desvio: dois databases na mesma inst�ncia n�o equivalem a dois RDS independentes. |
| 19-20 min | Reposit�rio, conclus�o e limita��es | Pontos pendentes, HTTP p�blico sem TLS, garantia de entrega dos eventos e encerramento do laborat�rio. |

Comandos �teis, no CloudShell autenticado:

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

Para demonstrar escala ao vivo, abra duas guias do CloudShell: uma com `kubectl get hpa -A -w`, outra com `python3 infra/load-test.py`. Execute apenas quando houver capacidade e tempo para aguardar a estabiliza��o. N�o mostre valores de Secrets, arquivos `.env` ou credenciais na grava��o.
