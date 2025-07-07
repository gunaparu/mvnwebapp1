import boto3
import json
import gzip
import time

S3_BUCKET_NAME = "aws-cloudtrail-logs-989638200024-6a843a6e"
OBJECT_KEY = "AWSLogs/989638200024/CloudTrail/us-east-1/2025/03/05/989638200024_CloudTrail_us-east-1_20250305T1815Z_kHgSmszP8BRbwsPg.json.gz"

DYNAMODB_TABLE_NAME = "IAMThreatLogs"
SNS_TOPIC_ARN = "arn:aws:sns:us-east-1:989638200024:SecurityAlerts"

CLAUDE_MODEL_ID = "anthropic.claude-3-5-sonnet-20240620-v1:0"


s3 = boto3.client("s3")
dynamodb = boto3.resource("dynamodb")
bedrock = boto3.client("bedrock-runtime")
sns = boto3.client("sns")

IAM_EVENT_NAMES = [
    "CreateUser", "DeleteUser", "AttachRolePolicy", "DetachRolePolicy",
    "PassRole", "AssumeRole", "CreateAccessKey", "DeleteAccessKey",
    "UpdateRole", "UpdateUser", "PutUserPolicy", "DeleteUserPolicy",
    "PutRolePolicy", "DeleteRolePolicy"
]

def get_latest_log_key():
    """Fetch the latest CloudTrail log file from S3."""
    try:
        response = s3.list_objects_v2(Bucket=S3_BUCKET_NAME, Prefix="AWSLogs/", Delimiter="/")
        objects = sorted(response.get("Contents", []), key=lambda obj: obj["LastModified"], reverse=True)
        return objects[0]["Key"] if objects else None
    except Exception as e:
        print(f"Error fetching latest log: {e}")
        return None

def download_and_extract_logs():
    """Download CloudTrail logs from S3 and extract JSON."""
    object_key = get_latest_log_key()
    if not object_key:
        print("No CloudTrail logs found.")
        return []

    try:
        response = s3.get_object(Bucket=S3_BUCKET_NAME, Key=object_key)
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
    """Analyze IAM logs using AWS Bedrock Claude 3.5."""
    findings = []
    
    for log in iam_logs:
        prompt = f"""
        Compare this IAM event with normal user behavior patterns. Identify any deviations that indicate suspicious activity.
        Score the risk on a scale of 1-10 and justify your decision.

        IAM Event:
        {json.dumps(log, indent=2)}
        """

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
            analysis_result = result.get("content", ["No analysis available"])[0]

            # Extract risk score from response
            risk_score = extract_risk_score(analysis_result)
            
            finding = {
                "event": log["eventName"],
                "user": log.get("userIdentity", {}).get("arn", "Unknown"),
                "risk_score": risk_score,
                "risk_assessment": analysis_result
            }
            findings.append(finding)

            # Alert if risk score is high (e.g., > 7)
            if risk_score and risk_score > 7:
                send_alert(finding)

        except Exception as e:
            print(f"Error invoking Claude 3.5: {e}")
            findings.append({
                "event": log["eventName"],
                "user": log.get("userIdentity", {}).get("arn", "Unknown"),
                "error": str(e)
            })

    return findings

def extract_risk_score(analysis_text):
    """Extract risk score from Claude's response."""
    try:
        lines = analysis_text.split("\n")
        for line in lines:
            if "risk score" in line.lower():
                score = [int(s) for s in line.split() if s.isdigit()]
                return score[0] if score else None
    except Exception as e:
        print(f"Error extracting risk score: {e}")
    return None

def send_alert(finding):
    """Send security alerts via AWS SNS."""
    message = f"""
    == IAM Security Alert ==
    
    Event: {finding["event"]}
    User: {finding["user"]}
    Risk Score: {finding["risk_score"]}
    Risk Assessment: {finding["risk_assessment"]}
    
    Please investigate immediately!
    """
    try:
        response = sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Message=message,
            Subject="AWS IAM Security Alert"
        )
        print(f"Alert sent successfully! Message ID: {response['MessageId']}")
    except Exception as e:
        print(f"Failed to send alert: {e}")

def save_to_dynamodb(analysis_results):
    """Store analysis results in DynamoDB."""
    table = dynamodb.Table(DYNAMODB_TABLE_NAME)

    for result in analysis_results:
        try:
            result["eventID"] = str(time.time())  # Generate unique event ID
            table.put_item(Item=result)
        except Exception as e:
            print(f"Error saving to DynamoDB: {e}")

def main():
    cloudtrail_events = download_and_extract_logs()
    
    if not cloudtrail_events:
        print("No CloudTrail logs found.")
        return
    
    iam_logs = filter_iam_logs(cloudtrail_events)
    
    if not iam_logs:
        print("No relevant IAM logs found.")
        return

    analysis_results = analyze_with_claude(iam_logs)
    save_to_dynamodb(analysis_results)

    print("\n==== IAM Threat Analysis Results ====")
    print(json.dumps(analysis_results, indent=2))

if __name__ == "__main__":
    main()