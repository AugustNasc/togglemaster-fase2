import json,base64,secrets,subprocess,hashlib
from pathlib import Path
REG='us-east-2';REGISTRY='699191579246.dkr.ecr.us-east-2.amazonaws.com'
def apply(o):
 p=subprocess.run(['kubectl','apply','--server-side','-f','-'],input=json.dumps(o),text=True,capture_output=True)
 if p.returncode: raise RuntimeError('Falha ao aplicar '+o['kind']+' '+o['metadata']['name'])
 print(o['kind'],o['metadata']['name'])
def getsecret(ns):
 p=subprocess.run(['kubectl','-n',ns,'get','secret','app-secrets','-o','json'],capture_output=True,text=True)
 return {k:base64.b64decode(v).decode() for k,v in json.loads(p.stdout)['data'].items()} if p.returncode==0 else {}
def secret(ns,vals): apply({'apiVersion':'v1','kind':'Secret','metadata':{'name':'app-secrets','namespace':ns},'type':'Opaque','data':{k:base64.b64encode(v.encode()).decode() for k,v in vals.items()}})
ev=getsecret('tm-evaluation');key=ev.get('SERVICE_API_KEY') or 'tm_key_'+secrets.token_hex(32)
ev.update(REDIS_URL='rediss://master.togglemaster-redis.ngzkvx.use2.cache.amazonaws.com:6379',SERVICE_API_KEY=key,AWS_SQS_URL='https://sqs.us-east-2.amazonaws.com/699191579246/togglemaster-events');secret('tm-evaluation',ev)
secret('tm-analytics',{'AWS_SQS_URL':ev['AWS_SQS_URL']})
sql="\\connect auth_db\nSET ROLE auth_app;\nINSERT INTO api_keys (name,key_hash) VALUES ('evaluation-service','"+hashlib.sha256(key.encode()).hexdigest()+"') ON CONFLICT (key_hash) DO NOTHING;\n"
apply({'apiVersion':'v1','kind':'Secret','metadata':{'name':'seed-service-key','namespace':'tm-setup'},'data':{'seed.sql':base64.b64encode(sql.encode()).decode()}})
apply({'apiVersion':'batch/v1','kind':'Job','metadata':{'name':'seed-service-key','namespace':'tm-setup'},'spec':{'backoffLimit':3,'template':{'spec':{'restartPolicy':'Never','containers':[{'name':'psql','image':'postgres:16-alpine','command':['psql','-v','ON_ERROR_STOP=1','-f','/sql/seed.sql'],'envFrom':[{'secretRef':{'name':'init-togglemaster-auth'}}],'volumeMounts':[{'name':'sql','mountPath':'/sql'}],'resources':{'requests':{'cpu':'50m','memory':'64Mi'},'limits':{'cpu':'250m','memory':'128Mi'}}}],'volumes':[{'name':'sql','secret':{'secretName':'seed-service-key'}}]}}}})
for i,name in enumerate(['auth','flag','targeting','evaluation','analytics']):
 ns='tm-'+name;svc=name+'-service';port=8001+i
 env={'PORT':str(port)}
 if name in ['flag','targeting']: env['AUTH_SERVICE_URL']='http://auth-service.tm-auth.svc.cluster.local:8001'
 if name=='evaluation': env.update(FLAG_SERVICE_URL='http://flag-service.tm-flag.svc.cluster.local:8002',TARGETING_SERVICE_URL='http://targeting-service.tm-targeting.svc.cluster.local:8003',AWS_REGION=REG)
 if name=='analytics': env.update(AWS_REGION=REG,AWS_DYNAMODB_TABLE='ToggleMasterAnalytics')
 apply({'apiVersion':'v1','kind':'ServiceAccount','metadata':{'name':svc,'namespace':ns}})
 apply({'apiVersion':'v1','kind':'ConfigMap','metadata':{'name':'app-config','namespace':ns},'data':env})
 container={'name':'app','image':REGISTRY+'/'+svc+':fase2-v2','ports':[{'containerPort':port}],'envFrom':[{'configMapRef':{'name':'app-config'}},{'secretRef':{'name':'app-secrets'}}],'resources':{'requests':{'cpu':('25m' if name=='analytics' else '100m'),'memory':'128Mi'},'limits':{'cpu':'500m','memory':'256Mi'}},'startupProbe':{'httpGet':{'path':'/health','port':port},'failureThreshold':30,'periodSeconds':5},'readinessProbe':{'httpGet':{'path':'/health','port':port},'periodSeconds':10},'livenessProbe':{'httpGet':{'path':'/health','port':port},'periodSeconds':20},'securityContext':{'allowPrivilegeEscalation':False,'capabilities':{'drop':['ALL']}}}
 apply({'apiVersion':'apps/v1','kind':'Deployment','metadata':{'name':svc,'namespace':ns},'spec':{'replicas':1,'selector':{'matchLabels':{'app':svc}},'template':{'metadata':{'labels':{'app':svc}},'spec':{'serviceAccountName':svc,'securityContext':{'runAsNonRoot':True,'runAsUser':10001,'fsGroup':65534},'containers':[container]}}}})
 apply({'apiVersion':'v1','kind':'Service','metadata':{'name':svc,'namespace':ns},'spec':{'type':'ClusterIP','selector':{'app':svc},'ports':[{'port':port,'targetPort':port}]}})
 if name in ['evaluation','analytics']:
  apply({'apiVersion':'autoscaling/v2','kind':'HorizontalPodAutoscaler','metadata':{'name':name,'namespace':ns},'spec':{'scaleTargetRef':{'apiVersion':'apps/v1','kind':'Deployment','name':svc},'minReplicas':1,'maxReplicas':5,'metrics':[{'type':'Resource','resource':{'name':'cpu','target':{'type':'Utilization','averageUtilization':70}}}]}})
print('Workloads aplicados; aguarde a verificacao funcional')