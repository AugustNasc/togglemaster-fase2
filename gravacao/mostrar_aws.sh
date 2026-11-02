#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export AWS_PAGER=''
printf '\nNOS\n'
kubectl get nodes
printf '\nAPLICACOES\n'
for n in tm-auth tm-flag tm-targeting tm-evaluation tm-analytics; do
  kubectl -n "$n" get deploy,pods,svc
done
printf '\nHPA\n'
kubectl get hpa -A
printf '\nINGRESS\n'
kubectl -n tm-evaluation get ingress
printf '\nSECRETS: SOMENTE NOMES\n'
kubectl -n tm-evaluation get secrets
printf '\nCONFIGURACAO E PROBES\n'
kubectl -n tm-evaluation get deployment evaluation-service -o jsonpath='{.spec.template.spec.containers[0].resources}{"\n"}{.spec.template.spec.containers[0].readinessProbe}{"\n"}'
