"""Executar no CloudShell. Gera sessao de uma hora, limitada a fila local."""
import datetime
import json
import os
from pathlib import Path
import time
import boto3
from botocore.exceptions import ClientError

REGION='us-east-2'
ACCOUNT='699191579246'
QUEUE='togglemaster-local-gravacao'
ROLE='ToggleMasterLocalSQS'
sts=boto3.client('sts',region_name=REGION)
iam=boto3.client('iam',region_name=REGION)
sqs=boto3.client('sqs',region_name=REGION)
who=sts.get_caller_identity()
assert who['Account']==ACCOUNT, 'Conta diferente do laboratorio'
source_role=iam.get_role(RoleName='AccountFullAccessRole')['Role']['Arn']
assert ':assumed-role/AccountFullAccessRole/' in who['Arn'], 'Sessao diferente da esperada'
url=sqs.create_queue(QueueName=QUEUE,Attributes={'SqsManagedSseEnabled':'true','ReceiveMessageWaitTimeSeconds':'20','VisibilityTimeout':'120'})['QueueUrl']
arn=sqs.get_queue_attributes(QueueUrl=url,AttributeNames=['QueueArn'])['Attributes']['QueueArn']
trust={'Version':'2012-10-17','Statement':[{'Effect':'Allow','Principal':{'AWS':source_role},'Action':'sts:AssumeRole'}]}
policy={'Version':'2012-10-17','Statement':[{'Effect':'Allow','Action':['sqs:SendMessage','sqs:ReceiveMessage','sqs:DeleteMessage','sqs:GetQueueAttributes'],'Resource':arn}]}
try:
    role=iam.get_role(RoleName=ROLE)['Role']
    assert role['AssumeRolePolicyDocument']==trust, 'O papel existente tem outra relacao de confianca'
except iam.exceptions.NoSuchEntityException:
    role=iam.create_role(RoleName=ROLE,AssumeRolePolicyDocument=json.dumps(trust),Description='Sessao temporaria dos containers locais, somente SQS de desenvolvimento',MaxSessionDuration=3600,Tags=[{'Key':'Project','Value':'togglemaster-fase2'}])['Role']
iam.put_role_policy(RoleName=ROLE,PolicyName='SomenteFilaLocal',PolicyDocument=json.dumps(policy))
for attempt in range(8):
    try:
        credentials=sts.assume_role(RoleArn=role['Arn'],RoleSessionName='gravacao-local',DurationSeconds=3600,Policy=json.dumps(policy))['Credentials']
        break
    except ClientError:
        if attempt==7:raise
        time.sleep(3)
values={'MASTER_KEY':'dev-master-key','SERVICE_API_KEY':'dev-service-key','AWS_REGION':REGION,'AWS_SQS_URL':url,'AWS_ACCESS_KEY_ID':credentials['AccessKeyId'],'AWS_SECRET_ACCESS_KEY':credentials['SecretAccessKey'],'AWS_SESSION_TOKEN':credentials['SessionToken']}
folder=Path.home()/'togglemaster-fase2'
folder.mkdir(exist_ok=True)
target=folder/'togglemaster-local.env'
target.write_text('\n'.join(k+'='+v for k,v in values.items())+'\n',encoding='utf-8')
os.chmod(target,0o600)
expires=credentials['Expiration'].astimezone(datetime.timezone.utc).isoformat()
(folder/'togglemaster-local-expira.txt').write_text(expires+'\n',encoding='utf-8')
print('Fila local:',url)
print('Arquivo para baixar:',target)
print('Validade UTC:',expires)
print('Credenciais limitadas a esta fila. Nenhuma chave foi exibida.')
