"""Conferencia do laboratorio. Executar no CloudShell, a partir do projeto."""
import argparse
import datetime
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import urllib.request
import urllib.error

REGION = 'us-east-2'
ACCOUNT = '699191579246'
CLUSTER = 'togglemaster-fase2'
GROUP = 'togglemaster-workers-free'
ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)
os.environ['AWS_PAGER'] = ''

def run(*args, timeout=120):
    p = subprocess.run(args, text=True, capture_output=True, timeout=timeout)
    if p.returncode:
        raise RuntimeError('Falha em ' + ' '.join(args[:3]) + '. Confira a sessao AWS e o acesso ao cluster.')
    return p.stdout

def obj(*args):
    return json.loads(run(*args))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--funcional', action='store_true', help='Cria uma flag de teste e confirma o evento no DynamoDB')
    parser.add_argument('--nos', type=int, choices=[2, 3], help='Ajusta a capacidade do grupo existente antes/depois da gravacao')
    a = parser.parse_args()
    who = obj('aws', 'sts', 'get-caller-identity')
    if who['Account'] != ACCOUNT:
        raise RuntimeError('Conta diferente da conta deste laboratorio. Nada foi alterado.')
    run('aws', 'eks', 'update-kubeconfig', '--region', REGION, '--name', CLUSTER)
    if a.nos:
        group = obj('aws', 'eks', 'describe-nodegroup', '--region', REGION, '--cluster-name', CLUSTER, '--nodegroup-name', GROUP)['nodegroup']
        if a.nos == 2:
            for ns in ['tm-evaluation', 'tm-analytics']:
                d = obj('kubectl', '-n', ns, 'get', 'deployment', ns[3:]+'-service', '-o', 'json')
                if d['spec'].get('replicas', 1) > 1:
                    raise RuntimeError('Aguarde os HPAs voltarem a uma replica antes de reduzir os nos.')
        if group['scalingConfig']['desiredSize'] != a.nos:
            run('aws', 'eks', 'update-nodegroup-config', '--region', REGION, '--cluster-name', CLUSTER,
                '--nodegroup-name', GROUP, '--scaling-config', f'minSize=1,maxSize=4,desiredSize={a.nos}')
        if a.nos == 3:
            print('Aguardando tres nos Ready...', flush=True)
            deadline = time.monotonic() + 420
            while True:
                nodes = obj('kubectl', 'get', 'nodes', '-o', 'json')['items']
                ready = sum(any(c['type']=='Ready' and c['status']=='True' for c in n['status']['conditions']) for n in nodes)
                if ready >= 3: break
                if time.monotonic() > deadline: raise RuntimeError('Os tres nos ainda nao estao Ready.')
                time.sleep(5)
    for name in ['auth', 'flag', 'targeting', 'evaluation', 'analytics']:
        run('kubectl', '-n', 'tm-'+name, 'rollout', 'status', 'deployment/'+name+'-service', '--timeout=90s')
    if a.funcional:
        p = subprocess.run([sys.executable, 'infra/smoke-test.py'], timeout=240)
        if p.returncode: raise RuntimeError('O teste funcional falhou. Nao iniciar a gravacao.')
    nodes = obj('kubectl', 'get', 'nodes', '-o', 'json')['items']
    deps = obj('kubectl', 'get', 'deployment', '-A', '-o', 'json')['items']
    hpas = obj('kubectl', 'get', 'hpa', '-A', '-o', 'json')['items']
    svc = obj('kubectl', '-n', 'nginx-ingress', 'get', 'svc', 'togglemaster-public', '-o', 'json')
    host = svc['status']['loadBalancer']['ingress'][0]['hostname']
    flag = json.loads((ROOT/'infra/smoke-result.json').read_text())['flag']
    url = 'http://'+host+'/evaluate?user_id=gravacao&flag_name='+flag
    with urllib.request.urlopen(url, timeout=20) as response:
        evaluated = json.load(response)
    if evaluated.get('result') is not True: raise RuntimeError('A avaliacao publica nao retornou true.')
    internal = {}
    for path in ['/flags', '/rules', '/auth/admin/keys']:
        try:
            with urllib.request.urlopen('http://'+host+path, timeout=10) as r: internal[path] = r.status
        except urllib.error.HTTPError as e: internal[path] = e.code
    if any(code != 404 for code in internal.values()):
        raise RuntimeError('Uma rota administrativa respondeu de forma inesperada. Revise o Ingress.')
    report = {
        'coleta': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'conta': ACCOUNT, 'regiao': REGION, 'cluster': CLUSTER,
        'nos': [{'nome': n['metadata']['name'], 'ready': any(c['type']=='Ready' and c['status']=='True' for c in n['status']['conditions'])} for n in nodes],
        'servicos': [{'namespace':d['metadata']['namespace'], 'nome':d['metadata']['name'], 'desejado':d['spec'].get('replicas',1), 'pronto':d['status'].get('readyReplicas',0)} for d in deps if d['metadata']['namespace'].startswith('tm-')],
        'hpa': [{'namespace':h['metadata']['namespace'], 'nome':h['metadata']['name'], 'status':h.get('status',{})} for h in hpas if h['metadata']['namespace'].startswith('tm-')],
        'url': url, 'avaliacao': evaluated, 'rotas_internas': internal,
        'funcional_executado_agora': a.funcional,
        'ressalvas': ['Dois RDS; o enunciado pede tres.', 'Compose local precisa de validacao separada.']}
    folder = ROOT/'gravacao/evidencias-atuais'
    folder.mkdir(parents=True, exist_ok=True)
    (folder/'preparacao-aws.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    (folder/'url-publica.txt').write_text(url+'\n', encoding='utf-8')
    print('\nAMBIENTE AWS CONFERIDO')
    print('URL:', url)
    print(run('kubectl','get','nodes'))
    print(run('kubectl','get','hpa','-A'))
    print('Evidencia: gravacao/evidencias-atuais/preparacao-aws.json')

if __name__ == '__main__':
    try: main()
    except Exception as e:
        print('PREPARACAO INTERROMPIDA:', str(e), file=sys.stderr)
        sys.exit(1)
