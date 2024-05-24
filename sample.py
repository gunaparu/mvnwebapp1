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
            
            
            
            
            
            
            
            
            
            
            import boto3

def add_tags_to_iam_role(role_name, additional_tags):
    # Initialize IAM client
    iam_client = boto3.client('iam')
    
    # Get the current tags associated with the IAM role
    response = iam_client.list_role_tags(RoleName=role_name)
    current_tags = response['Tags']
    
    # Add additional tags to the existing ones
    updated_tags = current_tags + additional_tags
    
    # Update tags for the IAM role
    iam_client.tag_role(RoleName=role_name, Tags=updated_tags)
    print(f"Additional tags added to IAM role {role_name} successfully.")

# Example usage:
if __name__ == "__main__":
    # IAM role name
    role_name = 'your-role-name'

    # Additional tags to add (format: {'Key': 'Value'})
    additional_tags = [{'Key': 'NewTag', 'Value': 'NewValue'}]

    # Call the function
    add_tags_to_iam_role(role_name, additional_tags)
    
    
    
    Certainly! Here's the revised text that incorporates the specific Active Directory (AD) group information:

---

### Importance of Maintaining Active Directory Groups Across All AWS Accounts

Active Directory (AD) groups are crucial for managing access control, enforcing security policies, and streamlining user management within an organization. In the context of AWS accounts, it is imperative that certain AD groups are consistently available and maintained across all accounts for the following reasons:

**Mandatory AD Groups for Every AWS Account**:
Every AWS account should be configured with the following AD groups and integrated into IDC to ensure proper access management and security:

1. **APP-eec-aws#<accnum>#BUAdministrator AccessRole**:
   - **Purpose**: Provisioned to the platform team and security team.
   - **Role**: Provides administrator-level access for managing the AWS environment.

2. **APP-eec-aws#<accnum>#ViewOnlyAccessRole**:
   - **Purpose**: Provisioned to respective PD teams.
   - **Role**: Grants view-only access for monitoring and oversight without the ability to make changes.

3. **APP-eec-aws#<accnum>#ReadOnlyAccessRole**:
   - **Purpose**: Provisioned to respective PD teams.
   - **Role**: Similar to the ViewOnlyAccessRole, it allows read-only access to ensure secure oversight.

4. **APP-eec-aws#<accnum>#BURoleForDeveloper**:
   - **Purpose**: Provisioned to respective PD teams.
   - **Role**: Provides necessary permissions for developers to perform their tasks while maintaining security.

5. **APP-eec-aws#<accnum>#DBA**:
   - **Purpose**: Provisioned to DBA teams.
   - **Role**: Grants access required for database administration tasks.

6. **APP-eec-aws#<accnum>#Financial-Analyst-Role**:
   - **Purpose**: Provisioned to financial analysts.
   - **Role**: Allows financial analysts to access necessary financial data and reports.

### Benefits of Maintaining These AD Groups

1. **Centralized Access Management**:
   - **Streamlined Access Control**: AD groups enable centralized management of permissions and access rights, ensuring that users have appropriate access to resources across all AWS accounts.
   - **Consistency in Policy Enforcement**: By maintaining consistent AD groups, security policies and compliance requirements are uniformly enforced across the organization.

2. **Enhanced Security**:
   - **Minimized Risk of Unauthorized Access**: Regularly updated and maintained AD groups help in preventing unauthorized access by ensuring that only authenticated users have access to critical resources.
   - **Efficient Role-Based Access Control (RBAC)**: AD groups facilitate the implementation of RBAC, where users are granted permissions based on their role, thereby enhancing security and operational efficiency.

3. **Operational Efficiency**:
   - **Simplified User Management**: With AD groups, user management becomes more efficient, reducing the administrative overhead of managing individual user permissions across multiple AWS accounts.
   - **Automated Provisioning and Deprovisioning**: Automating the provisioning and deprovisioning of users within AD groups ensures that access is granted and revoked promptly, aligning with the organizational policies and reducing the risk of stale accounts.

4. **Compliance and Auditing**:
   - **Regulatory Compliance**: Maintaining consistent AD groups helps in meeting regulatory compliance requirements by ensuring that access controls are consistently applied and audited.
   - **Audit Trails and Reporting**: Centralized AD groups provide clear audit trails, making it easier to track and report on access control changes, thereby supporting compliance and security audits.

5. **Scalability and Flexibility**:
   - **Scalable Access Management**: As the organization grows, maintaining AD groups across all AWS accounts ensures scalable access management without the need for extensive reconfiguration.
   - **Flexibility in Resource Access**: Consistent AD groups provide the flexibility to quickly grant or revoke access to resources as organizational needs evolve.

### Conclusion

Maintaining specified Active Directory groups across all AWS accounts, including the critical roles such as BUAdministrator, ViewOnlyAccess, ReadOnlyAccess, BURoleForDeveloper, DBA, and Financial-Analyst, is not just a best practice but a necessity for ensuring robust security, operational efficiency, and regulatory compliance. By implementing consistent AD group policies, organizations can achieve centralized control, enhance security, and support scalable and flexible access management.

---

This text integrates the specific AD group information into the overall context, highlighting their necessity and benefits.