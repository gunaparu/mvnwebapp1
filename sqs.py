import boto3
import json
import gzip
import time

# AWS Configurations
S3_BUCKET_NAME = "your-cloudtrail-log-bucket"
OBJECT_KEY = "AWSLogs/123456789012/CloudTrail/us-east-1/2025/03/06/log-file.json.gz"

DYNAMODB_TABLE_NAME = "IAMThreatLogs"
CLAUDE_MODEL_ID = "anthropic.claude-3-5-sonnet-20240620-v1:0"

# AWS Clients
s3 = boto3.client("s3")
dynamodb = boto3.resource("dynamodb")
bedrock = boto3.client("bedrock-runtime")

# IAM-related events to filter
IAM_EVENT_NAMES = [
    "CreateUser", "DeleteUser", "AttachRolePolicy", "DetachRolePolicy",
    "PassRole", "AssumeRole", "CreateAccessKey", "DeleteAccessKey",
    "UpdateRole", "UpdateUser", "PutUserPolicy", "DeleteUserPolicy",
    "PutRolePolicy", "DeleteRolePolicy"
]

def download_and_extract_logs():
    """Download CloudTrail logs from S3 and extract JSON."""
    try:
        print(f"Downloading {OBJECT_KEY} from {S3_BUCKET_NAME}...")
        response = s3.get_object(Bucket=S3_BUCKET_NAME, Key=OBJECT_KEY)
        log_data = gzip.decompress(response["Body"].read()).decode("utf-8")
        return json.loads(log_data).get("Records", [])
    except Exception as e:
        print(f"Error downloading logs: {e}")
        return []

def filter_iam_logs(cloudtrail_events):
    """Filter CloudTrail logs for IAM-related events."""
    iam_logs = [log for log in cloudtrail_events if log.get("eventName", "") in IAM_EVENT_NAMES]
    print(f"Total IAM logs found: {len(iam_logs)}")
    return iam_logs

def analyze_with_claude(iam_logs):
    """Analyze IAM logs using AWS Bedrock Claude 3.5 Sonnet."""
    findings = []
    
    for log in iam_logs:
        prompt = f"\n\nHuman: Analyze this IAM event for security risks:\n{json.dumps(log, indent=2)}\n\nAssistant:"
        payload = {
            "anthropic_version": "bedrock-2023-05-31",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 300
        }

        try:
            response = bedrock.invoke_model(
                modelId=CLAUDE_MODEL_ID,
                contentType="application/json",
                accept="application/json",
                body=json.dumps(payload)
            )
            result = json.loads(response["body"].read().decode("utf-8"))
            risk_assessment = result.get("content", ["No analysis available"])[0]

            findings.append({
                "event": log["eventName"],
                "user": log.get("userIdentity", {}).get("arn", "Unknown"),
                "risk_assessment": risk_assessment
            })
        except Exception as e:
            print(f"Error invoking Claude 3.5: {e}")
            findings.append({
                "event": log["eventName"],
                "user": log.get("userIdentity", {}).get("arn", "Unknown"),
                "error": str(e)
            })

    return findings

def main():
    """Main function to execute the analysis pipeline."""
    cloudtrail_events = download_and_extract_logs()
    
    if not cloudtrail_events:
        print("No CloudTrail logs found.")
        return
    
    iam_logs = filter_iam_logs(cloudtrail_events)
    
    if not iam_logs:
        print("No relevant IAM logs found.")
        return

    analysis_results = analyze_with_claude(iam_logs)

    print("\n==== IAM Threat Analysis Results ====")
    print(json.dumps(analysis_results, indent=2))

if __name__ == "__main__":
    main()