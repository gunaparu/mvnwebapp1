import os
import pandas as pd
cwd = os.path.abspath('') 
files = os.listdir(cwd)  

## Method 1 gets the first sheet of a given file
df = pd.DataFrame()
for file in files:
    if file.endswith('.xlsx'):
        df = df.append(pd.read_excel(file), ignore_index=True) 
df.head() 
df.to_excel('total_sales.xlsx')



## Method 2 gets all sheets of a given file
df_total = pd.DataFrame()
for file in files:                         # loop through Excel files
    if file.endswith('.xlsx'):
        excel_file = pd.ExcelFile(file)
        sheets = excel_file.sheet_names
        for sheet in sheets:               # loop through sheets inside an Excel file
            df = excel_file.parse(sheet_name = sheet)
            df_total = df_total.append(df)
df_total.to_excel('combined_file1.xlsx')


import boto3
from botocore.exceptions import ClientError
import pandas as pd

def main():
    # Get available profiles
    session = boto3.session.Session()
    profiles = session.available_profiles

    # Initialize CSV file and DataFrame
    with open("testwrite.csv", 'w') as f:
        f.write("Role Name,Policy Name,S3 Allow,S3 Deny,ec2 Allow,ec2 Deny,AccountNum\n")
    cols = ["Role Name", "Policy Name", "S3 Allow", "S3 Deny", "ec2 Allow", "ec2 Deny", "AccountNum"]
    df = pd.DataFrame(columns=cols)

    try:
        # Switch to account profile and retrieve IAM client
        session = boto3.Session(profile_name='EXPN-NA-DEV-SEC-OPS-DEV')
        iam_client = session.client('iam', region_name="us-east-1")
        account_num = session.client('sts').get_caller_identity().get('Account')
        print("Switching to account:", account_num)

        # Paginate through roles
        paginator = iam_client.get_paginator("list_roles")
        for response in paginator.paginate(PaginationConfig={'MaxItems': 1000}):
            for role in response['Roles']:
                role_name = role["RoleName"]

                # Initialize lists for permissions
                s3_allow, s3_deny, ec2_allow, ec2_deny = [], [], [], []

                # List attached policies
                attached_policies = iam_client.list_attached_role_policies(RoleName=role_name)['AttachedPolicies']

                # Process inline policies
                inline_policy_names = iam_client.list_role_policies(RoleName=role_name)['PolicyNames']
                for policy_name in inline_policy_names:
                    role_policy = iam_client.get_role_policy(RoleName=role_name, PolicyName=policy_name)
                    policy_document = role_policy['PolicyDocument']
                    for statement in policy_document.get('Statement', []):
                        process_statement(statement, s3_allow, s3_deny, ec2_allow, ec2_deny)

                # Process attached policies
                for policy in attached_policies:
                    policy_document = iam_client.get_policy(PolicyArn=policy['PolicyArn'])['Policy']['DefaultVersionId']
                    response = iam_client.get_policy_version(PolicyArn=policy['PolicyArn'], VersionId=policy_document)
                    docum = response['PolicyVersion']['Document']
                    for statement in docum.get('Statement', []):
                        process_statement(statement, s3_allow, s3_deny, ec2_allow, ec2_deny)

                # Write to CSV and DataFrame
                with open("testwrite.csv", 'a') as f:
                    f.write(f"{role_name},{set(attached_policies)},{set(s3_allow)},{set(s3_deny)},{set(ec2_allow)},{set(ec2_deny)},{account_num}\n")
                df = df.append({"Role Name": role_name, "Policy Name": set(attached_policies),
                                "S3 Allow": set(s3_allow), "S3 Deny": set(s3_deny),
                                "ec2 Allow": set(ec2_allow), "ec2 Deny": set(ec2_deny),
                                "AccountNum": account_num}, ignore_index=True)
    except ClientError as e:
        print("Error:", e)

    # Write DataFrame to CSV
    df.to_csv("testwrite.csv", index=False, mode='a', header=False)

def process_statement(statement, s3_allow, s3_deny, ec2_allow, ec2_deny):
    effect = statement.get('Effect', 'N/A')
    actions = statement.get('Action', [])
    resources = statement.get('Resource', [])

    if isinstance(actions, str):
        actions = [actions]
    if isinstance(resources, str):
        resources = [resources]

    for action in actions:
        if effect == 'Allow':
            if action.startswith('s3:'):
                s3_allow.append(action)
            elif action.startswith('ec2:'):
                ec2_allow.append(action)
        elif effect == 'Deny':
            if action.startswith('s3:'):
                s3_deny.append(action)
            elif action.startswith('ec2:'):
                ec2_deny.append(action)

if __name__ == "__main__":
    main()

