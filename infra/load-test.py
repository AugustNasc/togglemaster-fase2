import json,time,threading,concurrent.futures,urllib.request,subprocess,pathlib
r=json.loads(pathlib.Path('infra/public-result.json').read_text())
url=r['url']
end=time.monotonic()+120
counts={'ok':0,'error':0}
lock=threading.Lock()
def worker(i):
 while time.monotonic()<end:
  try:
   with urllib.request.urlopen(url+'&load='+str(i),timeout=8) as f: f.read()
   k='ok'
  except Exception: k='error'
  with lock: counts[k]+=1
snap=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=32) as pool:
 futures=[pool.submit(worker,i) for i in range(32)]
 for i in range(9):
  data=json.loads(subprocess.check_output(['kubectl','get','hpa','-A','-o','json']))
  sample={'elapsed':i*15,'hpas':[{'namespace':h['metadata']['namespace'],'name':h['metadata']['name'],'status':h.get('status',{})} for h in data['items']]}
  snap.append(sample)
  print(json.dumps(sample),flush=True)
  if i<8:time.sleep(15)
result={'requests':counts,'samples':snap,'seconds':120,'concurrency':32}
pathlib.Path('infra/load-result.json').write_text(json.dumps(result,indent=2))
print(json.dumps(counts),flush=True)
