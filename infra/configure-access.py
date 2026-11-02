import boto3,json
from pathlib import Path
reg='us-east-2';cluster='togglemaster-fase2';account='699191579246'
iam=boto3.client('iam');eks=boto3.client('eks',region_name=reg);ec=boto3.client('ec2',region_name=reg)
trust=Path('infra/pod-trust.json').read_text()
roles=[('ToggleMasterCNI','kube-system','aws-node','arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy',None),('ToggleMasterEvaluation','tm-evaluation','evaluation-service',None,'infra/evaluation-policy.json'),('ToggleMasterAnalytics','tm-analytics','analytics-service',None,'infra/analytics-policy.json'),('ToggleMasterLoadBalancer','kube-system','aws-load-balancer-controller',None,'infra/load-balancer-policy.json')]
iam.attach_role_policy(RoleName='AmazonEKSRoleManager-us-east-2-Node',PolicyArn='arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy')
for name,ns,sa,managed,local in roles:
 try: iam.create_role(RoleName=name,AssumeRolePolicyDocument=trust,Tags=[{'Key':'Project','Value':'ToggleMaster-Fase2'}])
 except iam.exceptions.EntityAlreadyExistsException: pass
 if managed: iam.attach_role_policy(RoleName=name,PolicyArn=managed)
 if local: iam.put_role_policy(RoleName=name,PolicyName='ToggleMasterAccess',PolicyDocument=Path(local).read_text())
 existing=eks.list_pod_identity_associations(clusterName=cluster,namespace=ns,serviceAccount=sa)['associations']
 if not existing: eks.create_pod_identity_association(clusterName=cluster,namespace=ns,serviceAccount=sa,roleArn='arn:aws:iam::'+account+':role/'+name)
for port in [5432,6379]:
 try: ec.authorize_security_group_ingress(GroupId='sg-00e598fd8e2ebd65c',IpPermissions=[{'IpProtocol':'tcp','FromPort':port,'ToPort':port,'UserIdGroupPairs':[{'GroupId':'sg-00646ad2204b8d97f','Description':'ToggleMaster EKS workloads'}]}])
 except ec.exceptions.ClientError as e:
  if e.response['Error']['Code']!='InvalidPermission.Duplicate': raise
rds=boto3.client('rds',region_name=reg)
for db in ['togglemaster-auth','togglemaster-flags']: rds.modify_db_instance(DBInstanceIdentifier=db,VpcSecurityGroupIds=['sg-00e598fd8e2ebd65c'],ApplyImmediately=True)
print('Permissoes e rede configuradas')