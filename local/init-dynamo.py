import os,time,boto3
client=boto3.client("dynamodb",region_name=os.environ["AWS_REGION"],endpoint_url=os.environ["DYNAMODB_ENDPOINT_URL"])
for attempt in range(30):
    try:
        client.create_table(TableName="ToggleMasterAnalytics",AttributeDefinitions=[{"AttributeName":"event_id","AttributeType":"S"}],KeySchema=[{"AttributeName":"event_id","KeyType":"HASH"}],BillingMode="PAY_PER_REQUEST")
        break
    except client.exceptions.ResourceInUseException:
        break
    except Exception:
        if attempt == 29: raise
        time.sleep(2)

