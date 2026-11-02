import boto3,json,secrets,base64,subprocess
from pathlib import Path
from urllib.parse import quote
reg='us-east-2';rds=boto3.client('rds',region_name=reg);sm=boto3.client('secretsmanager',region_name=reg)
def apply(obj):
 p=subprocess.run(['kubectl','apply','--server-side','-f','-'],input=json.dumps(obj),text=True,capture_output=True)
 if p.returncode: raise RuntimeError('Falha ao aplicar '+obj['kind']+' '+obj['metadata']['name'])
 print(obj['kind'],obj['metadata']['name'])
for ns in ['tm-auth','tm-flag','tm-targeting','tm-evaluation','tm-analytics','tm-setup']: apply({'apiVersion':'v1','kind':'Namespace','metadata':{'name':ns}})
apps={}
for name,ns,db,user,instance in [('auth','tm-auth','auth_db','auth_app','togglemaster-auth'),('flag','tm-flag','flags_db','flags_app','togglemaster-flags'),('targeting','tm-targeting','targeting_db','targeting_app','togglemaster-flags')]:
 d=rds.describe_db_instances(DBInstanceIdentifier=instance)['DBInstances'][0];host=d['Endpoint']['Address']
 old=subprocess.run(['kubectl','-n',ns,'get','secret','app-secrets','-o','json'],capture_output=True,text=True)
 vals={k:base64.b64decode(v).decode() for k,v in json.loads(old.stdout)['data'].items()} if old.returncode==0 else {}
 pw=vals.get('DB_PASSWORD') or secrets.token_hex(24)
 vals.update(DATABASE_URL='postgres://'+user+':'+quote(pw)+'@'+host+':5432/'+db+'?sslmode=require',DB_PASSWORD=pw)
 if name=='auth': vals['MASTER_KEY']=vals.get('MASTER_KEY') or secrets.token_hex(32)
 apply({'apiVersion':'v1','kind':'Secret','metadata':{'name':'app-secrets','namespace':ns},'type':'Opaque','data':{k:base64.b64encode(v.encode()).decode() for k,v in vals.items()}})
 apps[name]=(db,user,pw)
for inst,names in [('togglemaster-auth',['auth']),('togglemaster-flags',['flag','targeting'])]:
 d=rds.describe_db_instances(DBInstanceIdentifier=inst)['DBInstances'][0]
 master=json.loads(sm.get_secret_value(SecretId=d['MasterUserSecret']['SecretArn'])['SecretString'])
 sql=''
 for name in names:
  db,user,pw=apps[name]
  sql+=f"DO $$ BEGIN IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname='{user}') THEN CREATE ROLE {user} LOGIN PASSWORD '{pw}'; END IF; END $$;\n"
  sql+=f"GRANT {user} TO postgres;\n"
  sql+=f"SELECT 'CREATE DATABASE {db} OWNER {user}' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname='{db}');\n\\gexec\n"
  sql+=f"ALTER DATABASE {db} OWNER TO {user}; REVOKE ALL ON DATABASE {db} FROM PUBLIC; GRANT CONNECT ON DATABASE {db} TO {user};\n\\connect {db}\nSET ROLE {user};\n"
  sql+=Path({'auth':'auth-service','flag':'flag-service','targeting':'targeting-service'}[name]+'/db/init.sql').read_text()
  sql+='\nRESET ROLE; REVOKE CREATE ON SCHEMA public FROM PUBLIC;\n\\connect postgres\n'
 job='init-'+inst
 env={'PGHOST':d['Endpoint']['Address'],'PGUSER':master['username'],'PGPASSWORD':master['password'],'PGDATABASE':'postgres','PGSSLMODE':'require'}
 apply({'apiVersion':'v1','kind':'Secret','metadata':{'name':job,'namespace':'tm-setup'},'type':'Opaque','data':{k:base64.b64encode(v.encode()).decode() for k,v in env.items()}})
 apply({'apiVersion':'v1','kind':'Secret','metadata':{'name':job+'-sql','namespace':'tm-setup'},'data':{'init.sql':base64.b64encode(sql.encode()).decode()}})
 apply({'apiVersion':'batch/v1','kind':'Job','metadata':{'name':job,'namespace':'tm-setup'},'spec':{'backoffLimit':3,'template':{'spec':{'restartPolicy':'OnFailure','containers':[{'name':'psql','image':'postgres:16-alpine','command':['psql','-v','ON_ERROR_STOP=1','-f','/sql/init.sql'],'envFrom':[{'secretRef':{'name':job}}],'volumeMounts':[{'name':'sql','mountPath':'/sql'}],'resources':{'requests':{'cpu':'50m','memory':'64Mi'},'limits':{'cpu':'250m','memory':'128Mi'}}}],'volumes':[{'name':'sql','secret':{'secretName':job+'-sql'}}]}}}})
print('Inicializacao solicitada; credenciais mantidas em Secrets internos')
