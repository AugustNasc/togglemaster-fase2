"""Carga HTTP real, limitada. Nao altera requests ou simula consumo de CPU."""
import argparse
import concurrent.futures
import datetime
import json
from pathlib import Path
import subprocess
import threading
import time
import urllib.request

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--segundos',type=int,default=120,choices=range(15,121),metavar='15..120')
    ap.add_argument('--clientes',type=int,default=32,choices=range(1,33),metavar='1..32')
    ap.add_argument('--limite',type=int,default=45000,choices=range(1,45001),metavar='1..45000')
    a=ap.parse_args()
    folder=Path(__file__).resolve().parent/'evidencias-atuais'
    prepared=json.loads((folder/'preparacao-aws.json').read_text(encoding='utf-8'))
    url=prepared['url']; start=time.monotonic(); end=start+a.segundos
    counts={'tentativas':0,'respostas_esperadas':0,'falhas':0}
    errors={}; lock=threading.Lock(); samples=[]
    def worker(i):
        while time.monotonic()<end:
            with lock:
                if counts['tentativas']>=a.limite:return
                counts['tentativas']+=1
            try:
                with urllib.request.urlopen(url+'&cliente='+str(i),timeout=8) as r:
                    body=json.load(r)
                if body.get('result') is not True:raise ValueError('resultado inesperado')
                with lock:counts['respostas_esperadas']+=1
            except Exception as e:
                label=type(e).__name__
                with lock:
                    counts['falhas']+=1;errors[label]=errors.get(label,0)+1
    def observe():
        p=subprocess.run(['kubectl','get','hpa','-A','-o','json'],capture_output=True,text=True,timeout=15)
        if p.returncode:return {'segundo':round(time.monotonic()-start),'erro':'coleta de HPA indisponivel'}
        items=json.loads(p.stdout)['items']
        return {'segundo':round(time.monotonic()-start),'hpa':[{'namespace':h['metadata']['namespace'],'nome':h['metadata']['name'],'status':h.get('status',{})} for h in items if h['metadata']['namespace'].startswith('tm-')]}
    print(f'Carga de {a.segundos}s, {a.clientes} clientes, teto de {a.limite} chamadas.',flush=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=a.clientes) as pool:
        futures=[pool.submit(worker,i) for i in range(a.clientes)]
        while True:
            sample=observe();samples.append(sample)
            print(json.dumps({'segundo':sample['segundo'],'contagem':dict(counts)},ensure_ascii=False),flush=True)
            if time.monotonic()>=end or all(f.done() for f in futures):break
            time.sleep(min(15,max(0,end-time.monotonic())))
    report={'coleta':datetime.datetime.now(datetime.timezone.utc).isoformat(),'duracao_limite':a.segundos,'clientes':a.clientes,'teto':a.limite,'contagem':counts,'classes_das_falhas':errors,'amostras':samples}
    folder.mkdir(exist_ok=True)
    path=folder/('carga-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S')+'.json')
    path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(counts,ensure_ascii=False));print('Evidencia:',path)

if __name__=='__main__':main()
