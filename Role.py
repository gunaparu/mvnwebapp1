import boto3

def list_resources_associated_with_role(role_name):
    # Create a Boto3 IAM client and a Boto3 resource client
    iam_client = boto3.client('iam')
    resource_client = boto3.client('resourcegroupstaggingapi')

    try:
        # Get the IAM role's ARN
        response = iam_client.get_role(RoleName=role_name)
        role_arn = response['Role']['Arn']

        # Use Resource Groups Tagging API to find resources associated with the role
        resources_response = resource_client.get_resources(TagFilters=[{'Key': 'iam:role', 'Values': [role_arn]}])
        if 'ResourceTagMappingList' in resources_response:
            for resource in resources_response['ResourceTagMappingList']:
                resource_arn = resource['ResourceARN']
                print(f"Associated Resource: {resource_arn}")
        else:
            print(f"No associated resources found for IAM role: {role_name}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Replace 'YOUR_ROLE_NAME' with the name of the IAM role you want to check.
    role_name = 'YOUR_ROLE_NAME'
    list_resources_associated_with_role(role_name)
