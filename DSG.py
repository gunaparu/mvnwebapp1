import boto3

def remove_default_security_group_rules():
    regions = boto3.Session().get_available_regions('ec2')

    for region in regions:
        print(f"Processing region: {region}")
        ec2_client = boto3.client('ec2', region_name=region)

        try:
            default_security_group = ec2_client.describe_security_groups(
                Filters=[{'Name': 'group-name', 'Values': ['default']}]
            )['SecurityGroups'][0]

            # Revoke all inbound rules from the default security group
            ec2_client.revoke_security_group_ingress(
                GroupId=default_security_group['GroupId'],
                IpPermissions=default_security_group['IpPermissions']
            )

            # Revoke all outbound rules from the default security group
            ec2_client.revoke_security_group_egress(
                GroupId=default_security_group['GroupId'],
                IpPermissions=default_security_group['IpPermissionsEgress']
            )

            print(f"Rules removed from the default security group in {region}")
        except Exception as e:
            print(f"Error removing rules in {region}: {e}")

if __name__ == "__main__":
    remove_default_security_group_rules()
