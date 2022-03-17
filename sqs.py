import boto3
def main():
    profiles = boto3.session.Session().available_profiles   
    list_queues1()
def list_queues1():
    zero=0
    client = boto3.client('sqs')
    response = client.list_queues()
    for q1 in response['QueueUrls']:
        print("URL is:",q1,"\n")
        response1= client.get_queue_attributes(QueueUrl=q1, AttributeNames=['SqsManagedSseEnabled'])
        if len(client.get_queue_attributes(QueueUrl=q1, AttributeNames=['KmsMasterKeyId'])) == 0:
            print('encrypted queue',q1)
        print(response1['Attributes']['SqsManagedSseEnabled'])
if __name__ == "__main__":
    main()