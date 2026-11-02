import subprocess,json,base64,time,urllib.request,urllib.error,uuid,boto3
from pathlib import Path
procs=[]
def req(port,path,method='GET',body=None,key=None):
 headers={'Content-Type':'application/json'}
 if key: headers['Authorization']='Bearer '+key
 data=json.dumps(body).encode() if body is not None else None
 with urllib.request.urlopen(urllib.request.Request('http://127.0.0.1:'+str(port)+path,data=data,headers=headers,method=method),timeout=15) as r: return json.load(r)
try:
 for ns,svc,local,remote in [('tm-auth','auth-service',18001,8001),('tm-flag','flag-service',18002,8002),('tm-targeting','targeting-service',18003,8003),('tm-evaluation','evaluation-service',18004,8004)]:
  log=open('/tmp/togglemaster-forward-'+svc+'.log','a')
  procs.append(subprocess.Popen(['kubectl','-n',ns,'port-forward','service/'+svc,str(local)+':'+str(remote)],stdout=log,stderr=log))
 for port in [18001,18002,18003,18004]:
  for attempt in range(30):
   try: req(port,'/health');break
   except Exception:
    if attempt==29: raise
    time.sleep(1)
 sec=json.loads(subprocess.check_output(['kubectl','-n','tm-evaluation','get','secret','app-secrets','-o','json']))
 key=base64.b64decode(sec['data']['SERVICE_API_KEY']).decode()
 req(18001,'/validate',key=key)
 flag='demo-'+uuid.uuid4().hex[:8]
 req(18002,'/flags','POST',{'name':flag,'description':'Teste do Tech Challenge','is_enabled':True},key)
 req(18003,'/rules','POST',{'flag_name':flag,'is_enabled':True,'rules':{'type':'PERCENTAGE','value':100}},key)
 result=req(18004,'/evaluate?user_id=demo-user&flag_name='+flag)
 assert result['result'] is True,result
 table=boto3.resource('dynamodb',region_name='us-east-2').Table('ToggleMasterAnalytics')
 for attempt in range(45):
  events=[]
  scan_args={'FilterExpression':'#f = :flag','ExpressionAttributeNames':{'#f':'flag_name'},'ExpressionAttributeValues':{':flag':flag}}
  while True:
   page=table.scan(**scan_args)
   events.extend(page['Items'])
   if events or not page.get('LastEvaluatedKey'): break
   scan_args['ExclusiveStartKey']=page['LastEvaluatedKey']
  if events: break
  time.sleep(2)
 assert events,'Evento nao chegou ao DynamoDB'
 report={'flag':flag,'evaluation':result,'dynamodb_events':len(events),'passed':True}
 Path('infra/smoke-result.json').write_text(json.dumps(report,indent=2))
 print(json.dumps(report))
finally:
 for p in procs: p.terminate()
