import json,subprocess,time,urllib.request
from pathlib import Path
s=json.loads(subprocess.check_output(['kubectl','-n','nginx-ingress','get','svc','togglemaster-public','-o','json']))
host=s['status']['loadBalancer']['ingress'][0]['hostname']
o={'apiVersion':'networking.k8s.io/v1','kind':'Ingress','metadata':{'name':'evaluation-public','namespace':'tm-evaluation'},'spec':{'ingressClassName':'nginx','rules':[{'host':host,'http':{'paths':[{'path':'/evaluate','pathType':'Exact','backend':{'service':{'name':'evaluation-service','port':{'number':8004}}}}]}}]}}
Path('infra/public-ingress.json').write_text(json.dumps(o,indent=2));subprocess.run(['kubectl','apply','-f','infra/public-ingress.json'],check=True)
flag=json.loads(Path('infra/smoke-result.json').read_text())['flag']
url='http://'+host+'/evaluate?user_id=public-demo&flag_name='+flag
for attempt in range(30):
 try:
  with urllib.request.urlopen(url,timeout=10) as r: result=json.load(r)
  assert result['result'] is True
  Path('infra/public-result.json').write_text(json.dumps({'url':url,'result':result},indent=2));print(json.dumps({'url':url,'result':result}));break
 except Exception:
  if attempt==29: raise
  time.sleep(2)
