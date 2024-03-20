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
from datetime import date
from botocore.exceptions import ClientError
import pandas as pd
import csv
def main():
    profiles = boto3.session.Session().available_profiles
    with open("finalreport"+'.csv','w') as f:
        f.write("Role Name"+","+"Policy Name"+","+"S3 Allow"+","+"S3 Deny"+","+"ec2_allow"+","+"ec2_deny"+","+"AccountNum\n")
        try:
            session = boto3.Session(profile_name='EXPN-NA-DEV-SEC-OPS-DEV')
            client=session.client('iam',region_name="us-east-1")
            account_num = session.client('sts').get_caller_identity().get('Account')
            print("Switching to ", account_num)
            paginator = client.get_paginator("list_roles")
            for response in paginator.paginate(PaginationConfig={'MaxItems': 1000}):
                for role in response['Roles']:
                    s3_perms_allow = ['s3:*','s3:CreateBucket']
                    ec2_perms_allow = ["ec2:*",'ec2:CreateInstance','ec2:StartInstance']
                    s3_perms_deny = ['s3:DeleteBucket']
                    ec2_perms_deny = ['ec2:StopInstance','ec2:AttachInternetGateway','ec2:DetachNetworkInterface','iam:Create*']
                    policy_name =[]
                    policy_list = []
                    s3_allow = []
                    s3_deny = []
                    ec2_allow = []
                    ec2_deny = []
                    role_name =role["RoleName"] 
                    listpolicy = client.list_role_policies(RoleName=role["RoleName"])
                    print("Role name:",role["RoleName"])
                    innoofpolicies = len(listpolicy['PolicyNames'])
                    for policies in listpolicy['PolicyNames']:
                        role_policy = client.get_role_policy(RoleName=role["RoleName"],PolicyName=policies)
                        policy_document = role_policy['PolicyDocument']
                        policy_name.append(policies)
                        for idx, statement in enumerate(policy_document.get('Statement', []), start=1):
                            try:
                                effect = statement.get('Effect', 'N/A')
                                actions = statement.get('Action', 'N/A')
                                resources = statement.get('Resource', 'N/A')
                                conditions = statement.get('Condition', 'N/A')
                                if effect == 'Allow':
                                    for s3_perm_allow in s3_perms_allow:
                                        if s3_perm_allow in actions:
                                            print(f"\nStatement {idx}:")
                                            print(f"Actions: {actions}")
                                            action = str(actions).replace(",","$")
                                            s3_allow.append(s3_perm_allow)
                                            print(s3_allow)
                                    for ec2_perm_allow in ec2_perms_allow:    
                                        if ec2_perm_allow in actions:
                                            print(f"\nStatement {idx}:")
                                            print(f"Actions: {actions}")
                                            action = str(actions).replace(",","$")
                                            ec2_allow.append(ec2_perm_allow)
                                            resource = str(resources).replace(",","$")
                                            print(ec2_allow)
                                if effect == "Deny":
                                    for s3_perm_deny in s3_perms_deny:
                                        if s3_perm_deny in actions:
                                            print(f"\nStatement {idx}:")
                                            print(f"Effect: {effect}")
                                            print(f"Actions: {actions}")
                                            action = str(actions).replace(",","$")
                                            s3_deny.append(s3_perm_deny)
                                            resource = str(resources).replace(",","$")
                                            print(s3_deny)
                                    for ec2_perm_deny in ec2_perms_deny:    
                                        if ec2_perm_deny in actions:
                                            print(f"\nStatement {idx}:")
                                            print(f"Effect: {effect}")
                                            print(f"Actions: {actions}")
                                            action = str(actions).replace(",","$")
                                            ec2_deny.append(ec2_perm_deny)
                                            resource = str(resources).replace(",","$")
                                            print()
                            except Exception as e1:
                                print(e1,role['RoleName'],"has an issue",policy_document)
                                pass
                    policies_list = str(policy_name).replace(",","$")
                    response = client.list_attached_role_policies(RoleName=role['RoleName'])
                    attached_policies = response['AttachedPolicies']
                    policy_name1 = []
                    policy_list1 = []
                    s3_allow1 = []
                    s3_deny1 = []
                    ec2_allow1 = []
                    ec2_deny1 = []
                    cusnoofpolicies = len(attached_policies)
                    for policy in attached_policies:
                        policy_document = client.get_policy(PolicyArn=policy['PolicyArn'])['Policy']['DefaultVersionId']
                        response = client.get_policy(PolicyArn=policy['PolicyArn'])
                        policy_version = client.get_policy_version(PolicyArn = policy['PolicyArn'], VersionId = response['Policy']['DefaultVersionId'] )
                        docum = policy_version['PolicyVersion']['Document']
                        policy_name1.append(policy['PolicyName'])
                        for idx, statement in enumerate(docum.get('Statement',[]),start=1):
                            try:
                                effect = statement.get('Effect', 'N/A')
                                actions = statement.get('Action', 'N/A')
                                resources = statement.get('Resource', 'N/A')
                                conditions = statement.get('Condition', 'N/A')
                                if effect == 'Allow':
                                    for s3_perm_allow in s3_perms_allow:
                                        if s3_perm_allow in actions:
                                            print(f"\nStatement {idx}:")
                                            print(f"Effect: {effect}")
                                            print(f"Actions: {actions}")
                                            action = str(actions).replace(",","$")
                                            s3_allow1.append(s3_perm_allow)
                                            print(s3_allow1)
                                    for ec2_perm_allow in ec2_perms_allow:    
                                        if ec2_perm_allow in actions:
                                            print(f"\nStatement {idx}:")
                                            print(f"Effect: {effect}")
                                            print(f"Actions: {actions}")
                                            action = str(actions).replace(",","$")
                                            ec2_allow1.append(ec2_perm_allow)
                                            resource = str(resources).replace(",","$")
                                            print(ec2_allow1)
                                elif effect == 'Deny':
                                    for s3_perm_deny in s3_perms_deny:
                                        if s3_perm_deny in actions:
                                            print(f"\nStatement {idx}:")
                                            print(f"Effect: {effect}")
                                            print(f"Actions: {actions}")
                                            action = str(actions).replace(",","$")
                                            s3_deny1.append(s3_perm_deny)
                                            resource = str(resources).replace(",","$")
                                            s3_deny1.append(s3_perm_deny)
                                            print(s3_deny1)
                                    for ec2_perm_deny in ec2_perms_deny:    
                                        if ec2_perm_deny in actions:
                                            print(f"\nStatement {idx}:")
                                            print(f"Effect: {effect}")
                                            print(f"Actions: {actions}")
                                            action = str(actions).replace(",","$")
                                            ec2_deny1.append(ec2_perm_deny)
                                            resource = str(resources).replace(",","$")
                                            ec2_deny1.append(ec2_perm_deny)
                                            print(ec2_deny1)                   
                            except Exception as e1:
                                print(e1,role['RoleName'],"has an issue",policy_document)
                                pass 
                    policies_list1 = str(policy_name1).replace(",","$")
                    final_policies = policy_name + policy_name1
                    final_policies_list = str(final_policies).replace(",","$")
                    final_s3_allow = s3_allow + s3_allow1
                    final_s3_allow_list = str(final_s3_allow).replace(",","$")
                    final_s3_deny = s3_deny + s3_deny1
                    final_s3_deny_list = str(final_s3_deny).replace(",","$")
                    final_ec2_allow = ec2_allow + ec2_allow1
                    final_ec2_allow_list = str(final_ec2_allow).replace(",","$")
                    final_ec2_deny = ec2_deny + ec2_deny1
                    final_ec2_deny_list = str(final_ec2_deny).replace(",","$")
                    f.write(role_name+","+str(final_policies_list)+","+str(final_s3_allow_list)+","+str(final_s3_deny_list)+","+str(final_ec2_allow_list)+","+str(final_ec2_deny_list)+","+account_num+"\n")
                    print(role_name,"---->", final_policies,final_s3_allow,final_s3_deny,final_ec2_allow,final_ec2_deny,account_num)
        except Exception as e:
            print("Error",e)
            pass
if __name__ == "__main__":
    main()










import boto3
from botocore.exceptions import ClientError
import csv

def main():
    try:
        session = boto3.Session(profile_name='EXPN-NA-DEV-SEC-OPS-DEV')
        client = session.client('iam', region_name="us-east-1")
        account_num = session.client('sts').get_caller_identity().get('Account')
        print("Switching to", account_num)

        s3_perms_allow = ['s3:*', 's3:CreateBucket']
        ec2_perms_allow = ['ec2:*', 'ec2:CreateInstance', 'ec2:StartInstance']
        s3_perms_deny = ['s3:DeleteBucket']
        ec2_perms_deny = ['ec2:StopInstance', 'ec2:AttachInternetGateway', 'ec2:DetachNetworkInterface', 'iam:Create*']

        with open("finalreport.csv", 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Role Name", "Policy Name", "S3 Allow", "S3 Deny", "ec2_allow", "ec2_deny", "AccountNum"])

            paginator = client.get_paginator("list_roles")
            for response in paginator.paginate(PaginationConfig={'MaxItems': 1000}):
                for role in response['Roles']:
                    role_name = role["RoleName"]
                    print("Role name:", role_name)

                    # Fetch policies attached to the role
                    attached_policies = client.list_attached_role_policies(RoleName=role['RoleName'])['AttachedPolicies']
                    policies_list = []
                    s3_allow_list = []
                    s3_deny_list = []
                    ec2_allow_list = []
                    ec2_deny_list = []

                    for policy in attached_policies:
                        policy_document = client.get_policy(PolicyArn=policy['PolicyArn'])['Policy']['DefaultVersionId']
                        policy_version = client.get_policy_version(PolicyArn=policy['PolicyArn'],
                                                                   VersionId=policy_document)['PolicyVersion']['Document']

                        for idx, statement in enumerate(policy_version.get('Statement', []), start=1):
                            effect = statement.get('Effect', 'N/A')
                            actions = statement.get('Action', 'N/A')

                            if effect == 'Allow':
                                for s3_perm_allow in s3_perms_allow:
                                    if s3_perm_allow in actions:
                                        s3_allow_list.append(s3_perm_allow)

                                for ec2_perm_allow in ec2_perms_allow:
                                    if ec2_perm_allow in actions:
                                        ec2_allow_list.append(ec2_perm_allow)

                            elif effect == 'Deny':
                                for s3_perm_deny in s3_perms_deny:
                                    if s3_perm_deny in actions:
                                        s3_deny_list.append(s3_perm_deny)

                                for ec2_perm_deny in ec2_perms_deny:
                                    if ec2_perm_deny in actions:
                                        ec2_deny_list.append(ec2_perm_deny)

                        policies_list.append(policy['PolicyName'])

                    # Fetch inline policies attached to the role
                    inline_policies = client.list_role_policies(RoleName=role['RoleName'])['PolicyNames']
                    for policy_name in inline_policies:
                        policy_version = client.get_role_policy(RoleName=role['RoleName'], PolicyName=policy_name)['PolicyDocument']

                        for idx, statement in enumerate(policy_version.get('Statement', []), start=1):
                            effect = statement.get('Effect', 'N/A')
                            actions = statement.get('Action', 'N/A')

                            if effect == 'Allow':
                                for s3_perm_allow in s3_perms_allow:
                                    if s3_perm_allow in actions:
                                        s3_allow_list.append(s3_perm_allow)

                                for ec2_perm_allow in ec2_perms_allow:
                                    if ec2_perm_allow in actions:
                                        ec2_allow_list.append(ec2_perm_allow)

                            elif effect == 'Deny':
                                for s3_perm_deny in s3_perms_deny:
                                    if s3_perm_deny in actions:
                                        s3_deny_list.append(s3_perm_deny)

                                for ec2_perm_deny in ec2_perms_deny:
                                    if ec2_perm_deny in actions:
                                        ec2_deny_list.append(ec2_perm_deny)

                        policies_list.append(policy_name)

                    writer.writerow([role_name,
                                     ','.join(policies_list),
                                     ','.join(s3_allow_list),
                                     ','.join(s3_deny_list),
                                     ','.join(ec2_allow_list),
                                     ','.join(ec2_deny_list),
                                     account_num])

                    print(role_name, "---->", policies_list, s3_allow_list, s3_deny_list, ec2_allow_list, ec2_deny_list, account_num)

    except ClientError as e:
        print("Error:", e)

if __name__ == "__main__":
    main()