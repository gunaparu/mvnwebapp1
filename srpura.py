import requests
import boto3
import json
import time
from datetime import datetime

# 🟢 CONFIGURATIONS
WIZ_API_URL = "https://api.wiz.io/graphql"
WIZ_API_KEY = "your-wiz-api-key"  # Replace with your Wiz API key
S3_BUCKET_NAME = "your-s3-bucket"  # Replace with your S3 bucket
DYNAMODB_TABLE_NAME = "CSPMIssueTracker"

# AWS Clients
s3 = boto3.client("s3")
dynamodb = boto3.resource("dynamodb")

# 🟢 GraphQL Query to Fetch CSPM Issues
QUERY = """
{
  issues {
    edges {
      node {
        id
        title
        riskLevel
        createdAt
        entities { name }
      }
    }
  }
}
"""

# 🟢 Function to Fetch Issues from Wiz API
def fetch_cspm_issues():
    headers = {"Authorization": f"Bearer {WIZ_API_KEY}", "Content-Type": "application/json"}
    response = requests.post(WIZ_API_URL, json={"query": QUERY}, headers=headers)

    if response.status_code == 200:
        data = response.json().get("data", {}).get("issues", {}).get("edges", [])
        return [
            {
                "issue_id": item["node"]["id"],
                "title": item["node"]["title"],
                "resource_name": item["node"]["entities"][0]["name"] if item["node"]["entities"] else "Unknown",
                "risk_level": item["node"]["riskLevel"],
                "reported_date": item["node"]["createdAt"],
            }
            for item in data
        ]
    else:
        print(f"⚠️ API Error: {response.status_code} - {response.text}")
        return []

# 🟢 Function to Store Issues in S3
def store_in_s3(data):
    timestamp = datetime.utcnow().strftime("%Y-%m-%d-%H-%M-%S")
    s3_key = f"wiz_cspm_issues/{timestamp}.json"

    try:
        s3.put_object(Bucket=S3_BUCKET_NAME, Key=s3_key, Body=json.dumps(data))
        print(f"✅ Issues saved to S3: {s3_key}")
    except Exception as e:
        print(f"⚠️ Failed to store in S3: {e}")

# 🟢 Function to Track Issue Status in DynamoDB
def update_issue_status(issues):
    table = dynamodb.Table(DYNAMODB_TABLE_NAME)

    for issue in issues:
        issue_id = issue["issue_id"]
        reported_date = issue["reported_date"]
        resource_name = issue["resource_name"]

        # Check if issue exists in DynamoDB
        response = table.get_item(Key={"issue_id": issue_id})
        existing_issue = response.get("Item")

        if existing_issue:
            # Issue already exists → Status remains "Yet to be Fixed"
            table.update_item(
                Key={"issue_id": issue_id},
                UpdateExpression="SET last_seen = :last_seen",
                ExpressionAttributeValues={":last_seen": reported_date},
            )
        else:
            # New issue → Mark as "Yet to be Fixed"
            table.put_item(
                Item={
                    "issue_id": issue_id,
                    "title": issue["title"],
                    "resource_name": resource_name,
                    "risk_level": issue["risk_level"],
                    "reported_date": reported_date,
                    "status": "Yet to be Fixed",
                    "last_seen": reported_date,
                }
            )

    # Check for fixed issues (issues that no longer appear in Wiz API response)
    scan_response = table.scan()
    for item in scan_response.get("Items", []):
        if not any(i["issue_id"] == item["issue_id"] for i in issues):
            # Mark issue as "Fixed"
            table.update_item(
                Key={"issue_id": item["issue_id"]},
                UpdateExpression="SET status = :status",
                ExpressionAttributeValues={":status": "Fixed"},
            )

# 🟢 Main Function
def main():
    print("🚀 Fetching CSPM issues from Wiz.io...")
    issues = fetch_cspm_issues()

    if not issues:
        print("⚠️ No issues found.")
        return

    print(f"✅ Retrieved {len(issues)} issues. Storing in S3 and updating DynamoDB...")
    store_in_s3(issues)
    update_issue_status(issues)

    print("\n==== CSPM Issue Report ====")
    print("| Issue ID  | Title                | Resource Name      | Risk Level | Status          |")
    print("|-----------|----------------------|--------------------|------------|-----------------|")
    for issue in issues:
        print(f"| {issue['issue_id']} | {issue['title']} | {issue['resource_name']} | {issue['risk_level']} | Yet to be Fixed |")

if __name__ == "__main__":
    main()
    
    
import requests
import boto3
import json
import os

# 🟢 Wiz API Credentials (Use AWS Secrets Manager for security in production)
WIZ_CLIENT_ID = os.environ["WIZ_CLIENT_ID"]
WIZ_CLIENT_SECRET = os.environ["WIZ_CLIENT_SECRET"]
WIZ_AUTH_URL = "https://auth.wiz.io/oauth/token"  # Authentication endpoint
WIZ_API_URL = "https://api.wiz.io/graphql"

# 🟢 AWS S3 Configuration
S3_BUCKET_NAME = os.environ["S3_BUCKET_NAME"]

# 🟢 AWS Clients
s3 = boto3.client("s3")

def get_wiz_access_token():
    """Authenticate and get Wiz API access token."""
    payload = {
        "client_id": WIZ_CLIENT_ID,
        "client_secret": WIZ_CLIENT_SECRET,
        "audience": "wiz-api",
        "grant_type": "client_credentials"
    }
    
    response = requests.post(WIZ_AUTH_URL, json=payload)
    
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"⚠️ Failed to authenticate with Wiz API: {response.text}")
        return None

def fetch_cspm_issues():
    """Fetch CSPM issues from Wiz API."""
    access_token = get_wiz_access_token()
    if not access_token:
        return []

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    QUERY = """
    {
      issues {
        edges {
          node {
            id
            title
            riskLevel
            createdAt
            entities { name }
          }
        }
      }
    }
    """
    
    response = requests.post(WIZ_API_URL, json={"query": QUERY}, headers=headers)

    if response.status_code == 200:
        data = response.json().get("data", {}).get("issues", {}).get("edges", [])
        return [
            {
                "issue_id": item["node"]["id"],
                "title": item["node"]["title"],
                "resource_name": item["node"]["entities"][0]["name"] if item["node"]["entities"] else "Unknown",
                "risk_level": item["node"]["riskLevel"],
                "reported_date": item["node"]["createdAt"],
            }
            for item in data
        ]
    else:
        print(f"⚠️ API Error: {response.status_code} - {response.text}")
        return []