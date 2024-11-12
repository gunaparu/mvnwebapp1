from multiprocessing.sharedctypes import Value
import boto3
from datetime import date
import xlwings as xw
import openpyxl
import botocore
import pandas as pd
import json
from botocore.exceptions import ClientError
def main():
    sts_client = boto3.client('sts')
    #file_name= 'Accesskeys_'+str(date.today())+".csv"
    with open("roles_report.csv",'w') as f: 
        f.write("RoleName"+","+"RoleId"+","+"Arn"+","+"CreateDate"+","+"LastUsedDate"+","+"PolicyNames"+","+"Trust Relationship"+","+"PolicyDocument"+","+"AccountNumber\n")
        #f.write("RoleName"+","+"RoleId"+","+"Arn"+","+"CreateDate"+","+"LastUsedDate"+","+"Role Age"+","+"AccountNumber\n")
        assumed_role_object = sts_client.assume_role(RoleArn='arn:aws:iam::528150397796:role/IAM_Automation',RoleSessionName="iamautomation",ExternalId="UZZCWIWGSY")
        credentials=assumed_role_object['Credentials']
        client=boto3.client('sts',aws_access_key_id=credentials['AccessKeyId'],aws_secret_access_key=credentials['SecretAccessKey'],aws_session_token=credentials['SessionToken'])
        root_acc = client.get_caller_identity().get('Account')
        print(root_acc)
        assumerole_iam(client,f,sts_client)
def assumerole_iam(client,f,sts_client):
        assumed_role_object = sts_client.assume_role(RoleArn="arn:aws:iam::528150397796:role/528150397796-Devops-Admin-Role",RoleSessionName="iamautomation")
        credentials=assumed_role_object['Credentials']
        iam_client=boto3.client('iam',aws_access_key_id=credentials['AccessKeyId'],aws_secret_access_key=credentials['SecretAccessKey'],
        aws_session_token=credentials['SessionToken'])
        sts_clientroot1=boto3.client('sts',aws_access_key_id=credentials['AccessKeyId'],aws_secret_access_key=credentials['SecretAccessKey'],aws_session_token=credentials['SessionToken'])
        root_acc = sts_clientroot1.get_caller_identity()
        print(root_acc)
        fname = 'roles-dev.xlsx'
        wb = openpyxl.load_workbook(fname)
        sheet = wb.get_sheet_by_name('Sheet1')
        for rowOfCellObjects in sheet['A71':'A110']:
            try:
                for cellObj in rowOfCellObjects:
                    #print(cellObj.coordinate, cellObj.value)
                    v1 = cellObj.value
                    assumed_role_object = sts_clientroot1.assume_role(RoleArn=v1,RoleSessionName="AssumeRoleSession1")
                    credentials=assumed_role_object['Credentials']
                    iam_client=boto3.client('iam',aws_access_key_id=credentials['AccessKeyId'],aws_secret_access_key=credentials['SecretAccessKey'],
                    aws_session_token=credentials['SessionToken'])
                    sts_client1=boto3.client('sts',aws_access_key_id=credentials['AccessKeyId'],aws_secret_access_key=credentials['SecretAccessKey'],
                    aws_session_token=credentials['SessionToken'])
                    account_num = sts_client1.get_caller_identity().get('Account')
                    #acc_name =   boto3.client('organizations').describe_account(AccountId=account_num).get('Account').get('Name')
                    users = iam_client.list_users()["Users"]
                    print("Switching to",account_num)
                    iam_roles(iam_client,client,f,account_num)
            except botocore.exceptions.ClientError as error: 
                print(error)
                continue
def iam_roles(iam_client,client,f,account_num):    
    paginator = iam_client.get_paginator("list_roles")
    for page in paginator.paginate(PaginationConfig={'MaxItems': 1000}):
        for listed_role in page["Roles"]:
            role_name = listed_role["RoleName"]
            role_id = listed_role["RoleId"]
            role_arn = listed_role["Arn"]
            role = iam_client.get_role(RoleName=role_name)["Role"]
            last_used = role.get("RoleLastUsed", {}).get("LastUsedDate")
            role_doc= role.get('AssumeRolePolicyDocument')
            assume_document = str(role_doc).replace(",","$")
            lastuseddate = str(last_used)
            created = listed_role["CreateDate"].date()
            currentdate = date.today()
            roleage = currentdate - created
            #print(roleage.days)
            createddate = str(created)
            policy = iam_client.list_role_policies(RoleName=role_name)['PolicyNames']
            for policy_name in policy:
              role_policy = iam_client.get_role_policy(RoleName=role_name,PolicyName=policy_name)
              print(role_policy)
              policy_document = role_policy['PolicyDocument']
              policy_docum = str(policy_document).replace(",","$")
              f.write(role_name+","+role_id+","+role_arn+","+createddate+","+lastuseddate+","+policy_name+","+assume_document+","+policy_docum+","+account_num+"\n")
            policy_name = str(policy)
            #print(policy)
            policy_names = policy_name.replace(",","$")
            cus_managed = iam_client.list_attached_role_policies(RoleName=role_name)['AttachedPolicies']
            length = len(cus_managed)
            try:
                for i in range(length):   
                    polarn = cus_managed[i]["PolicyArn"]
                    polname = cus_managed[i]['PolicyName']
                    response = iam_client.get_policy(PolicyArn=polarn)
                    policy_version = iam_client.get_policy_version( PolicyArn = polarn, VersionId = response['Policy']['DefaultVersionId'] )
                    
					#Hashed earlier f.write(json.dumps(policy_version['PolicyVersion']['Document']))
                    docum = policy_version['PolicyVersion']['Document']
                    document = str(docum).replace(",","$")
                    
                    f.write(role_name+","+role_id+","+role_arn+","+createddate+","+lastuseddate+","+polname+","+assume_document+","+document+","+account_num+"\n")
                    #f.write(role_name+","+role_id+","+role_arn+","+createddate+","+lastuseddate+","+str(roleage.days)+","+account_num+"\n")
                    
                    #print(json.dumps(policy_version['PolicyVersion']['Document']['Statement']))
            except Exception as e:
                print(e)
                continue
if __name__ == "__main__":
    main()
