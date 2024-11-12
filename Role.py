import boto3
from datetime import date
import csv
import openpyxl
from botocore.exceptions import ClientError

def main():
    # Assume the IAM Automation Role to start
    sts_client = boto3.client('sts')
    assumed_role_object = sts_client.assume_role(
        RoleArn='arn:aws:iam::528150397796:role/IAM_Automation',
        RoleSessionName="iamautomation",
        ExternalId="UZZCWIWGSY"
    )
    credentials = assumed_role_object['Credentials']
    client = boto3.client(
        'sts',
        aws_access_key_id=credentials['AccessKeyId'],
        aws_secret_access_key=credentials['SecretAccessKey'],
        aws_session_token=credentials['SessionToken']
    )
    
    # Get the root account number
    root_acc = client.get_caller_identity().get('Account')
    print("Root Account:", root_acc)
    
    # Open CSV file for writing
    with open("roles_report.csv", 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["RoleName", "RoleArn", "LastUsedDate", "AccountNumber"])
        
        # Call the function to assume and gather roles information from Excel
        assumerole_iam(client, writer, sts_client)

def assumerole_iam(client, writer, sts_client):
    # Load the Excel file and sheet
    fname = 'roles-dev.xlsx'
    wb = openpyxl.load_workbook(fname)
    sheet = wb['Sheet1']
    
    # Loop through the specified range of cells for role ARNs
    for row in sheet['A71':'A110']:
        for cell in row:
            role_arn = cell.value
            if role_arn:
                try:
                    # Assume role for each ARN found in the Excel sheet
                    assumed_role_object = sts_client.assume_role(
                        RoleArn=role_arn,
                        RoleSessionName="AssumeRoleSession1"
                    )
                    credentials = assumed_role_object['Credentials']
                    
                    iam_client = boto3.client(
                        'iam',
                        aws_access_key_id=credentials['AccessKeyId'],
                        aws_secret_access_key=credentials['SecretAccessKey'],
                        aws_session_token=credentials['SessionToken']
                    )
                    
                    sts_client1 = boto3.client(
                        'sts',
                        aws_access_key_id=credentials['AccessKeyId'],
                        aws_secret_access_key=credentials['SecretAccessKey'],
                        aws_session_token=credentials['SessionToken']
                    )
                    
                    account_num = sts_client1.get_caller_identity().get('Account')
                    print(f"Switching to Account: {account_num}")
                    
                    # Collect role data and write to CSV
                    iam_roles(iam_client, writer, account_num)
                
                except ClientError as error:
                    print(f"Error assuming role for {role_arn}: {error}")
                    continue

def iam_roles(iam_client, writer, account_num):
    paginator = iam_client.get_paginator("list_roles")
    
    for page in paginator.paginate(PaginationConfig={'MaxItems': 1000}):
        for listed_role in page["Roles"]:
            role_name = listed_role["RoleName"]
            role_arn = listed_role["Arn"]
            last_used = listed_role.get("RoleLastUsed", {}).get("LastUsedDate")
            
            # Write the required information to CSV
            writer.writerow([role_name, role_arn, last_used if last_used else "N/A", account_num])

if __name__ == "__main__":
    main()