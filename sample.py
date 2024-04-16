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
import pandas as pd

# AWS IAM credentials
ACCESS_KEY = 'your_access_key'
SECRET_KEY = 'your_secret_key'
REGION_NAME = 'your_region_name'

# Role names to tag
ROLES_TO_TAG = ['rds-monitoring-role', 'CloudabilityRole', 'WizAccess-Role', 'Okta-Idp-cross-account-role', 'stacksets-ехес-с1с1605357571231990026442703']

# Tag details
TAG_KEY = 'role_type'
TAG_VALUE = 'core/service'

# Excel file details
EXCEL_FILE = 'roles.xlsx'
SHEET_NAME = 'Sheet1'

def assume_role_and_tag(role_name, tag_key, tag_value, access_key, secret_key, region_name):
    sts_client = boto3.client('sts', aws_access_key_id=access_key, aws_secret_access_key=secret_key, region_name=region_name)
    try:
        response = sts_client.assume_role(RoleArn=f"arn:aws:iam::YOUR_ACCOUNT_ID:role/{role_name}", RoleSessionName='AssumeRoleSession')
        credentials = response['Credentials']

        # Create a new session using the temporary credentials
        session = boto3.Session(
            aws_access_key_id=credentials['AccessKeyId'],
            aws_secret_access_key=credentials['SecretAccessKey'],
            aws_session_token=credentials['SessionToken'],
            region_name=region_name
        )

        # Get existing tags of the role
        iam = session.client('iam')
        response = iam.list_role_tags(RoleName=role_name)
        existing_tags = response.get('Tags', [])

        # Check if the new tag already exists
        tag_exists = any(tag['Key'] == tag_key for tag in existing_tags)
        if not tag_exists:
            # Add the new tag along with existing tags
            updated_tags = existing_tags + [{'Key': tag_key, 'Value': tag_value}]
            iam.tag_role(RoleName=role_name, Tags=updated_tags)
            print(f"Tag '{tag_key}:{tag_value}' added to IAM role '{role_name}' successfully.")
        else:
            print(f"Tag '{tag_key}:{tag_value}' already exists for IAM role '{role_name}'.")

    except Exception as e:
        print(f"Error tagging IAM role '{role_name}': {e}")

if __name__ == "__main__":
    # Read role names from Excel sheet
    df = pd.read_excel(EXCEL_FILE, sheet_name=SHEET_NAME)
    roles_from_excel = df['RoleName'].tolist()

    # Assume each role and tag it
    for role_name in roles_from_excel:
        if role_name in ROLES_TO_TAG:
            assume_role_and_tag(role_name, TAG_KEY, TAG_VALUE, ACCESS_KEY, SECRET_KEY, REGION_NAME)
        else:
            print(f"Role '{role_name}' not in the list of roles to tag.")








import boto3
import pandas as pd

# AWS IAM credentials
ACCESS_KEY = 'your_access_key'
SECRET_KEY = 'your_secret_key'
REGION_NAME = 'your_region_name'

# Role ARNs to tag
ROLE_ARNS_TO_TAG = [
    'arn:aws:iam::YOUR_ACCOUNT_ID:role/rds-monitoring-role',
    'arn:aws:iam::YOUR_ACCOUNT_ID:role/CloudabilityRole',
    'arn:aws:iam::YOUR_ACCOUNT_ID:role/WizAccess-Role',
    'arn:aws:iam::YOUR_ACCOUNT_ID:role/Okta-Idp-cross-account-role',
    'arn:aws:iam::YOUR_ACCOUNT_ID:role/stacksets-ехес-с1с1605357571231990026442703'
]

# Tag details
TAG_KEY = 'role_type'
TAG_VALUE = 'core/service'

# Excel file details
EXCEL_FILE = 'roles.xlsx'
SHEET_NAME = 'Sheet1'
ROLE_ARN_COLUMN = 'RoleArn'

def assume_role_and_tag(role_arn, tag_key, tag_value, access_key, secret_key, region_name):
    sts_client = boto3.client('sts', aws_access_key_id=access_key, aws_secret_access_key=secret_key, region_name=region_name)
    try:
        response = sts_client.assume_role(RoleArn=role_arn, RoleSessionName='AssumeRoleSession')
        credentials = response['Credentials']

        # Create a new session using the temporary credentials
        session = boto3.Session(
            aws_access_key_id=credentials['AccessKeyId'],
            aws_secret_access_key=credentials['SecretAccessKey'],
            aws_session_token=credentials['SessionToken'],
            region_name=region_name
        )

        # Get existing tags of the role
        iam = session.client('iam')
        role_name = role_arn.split('/')[-1]
        response = iam.list_role_tags(RoleName=role_name)
        existing_tags = response.get('Tags', [])

        # Check if the new tag already exists
        tag_exists = any(tag['Key'] == tag_key for tag in existing_tags)
        if not tag_exists:
            # Add the new tag along with existing tags
            updated_tags = existing_tags + [{'Key': tag_key, 'Value': tag_value}]
            iam.tag_role(RoleName=role_name, Tags=updated_tags)
            print(f"Tag '{tag_key}:{tag_value}' added to IAM role '{role_name}' successfully.")
        else:
            print(f"Tag '{tag_key}:{tag_value}' already exists for IAM role '{role_name}'.")

    except Exception as e:
        print(f"Error tagging IAM role '{role_name}': {e}")

if __name__ == "__main__":
    # Read role ARNs from Excel sheet
    df = pd.read_excel(EXCEL_FILE, sheet_name=SHEET_NAME)
    role_arns_from_excel = df[ROLE_ARN_COLUMN].tolist()

    # Assume each role and tag it
    for role_arn in role_arns_from_excel:
        if role_arn in ROLE_ARNS_TO_TAG:
            assume_role_and_tag(role_arn, TAG_KEY, TAG_VALUE, ACCESS_KEY, SECRET_KEY, REGION_NAME)
        else:
            print(f"Role ARN '{role_arn}' not in the list of roles to tag.")