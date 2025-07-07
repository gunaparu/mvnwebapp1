import boto3
import json
import gzip
import time
import re

# AWS Configurations
S3_BUCKET_NAME = "aws-cloudtrail-logs-989638200024-6a843a6e"
#OBJECT_KEY = "AWSLogs/989638200024/CloudTrail/us-east-1/2025/03/14/989638200024_CloudTrail_us-east-1_20250314T0140Z_8biw5uidZKa7aUUW.json.gz"
prefix = "AWSLogs/989638200024/CloudTrail/us-east-1/"
DYNAMODB_TABLE_NAME = "IAMThreatLogs"
SNS_TOPIC_ARN = "arn:aws:sns:us-east-1:989638200024:SecurityAlerts"
CLAUDE_MODEL_ID = "anthropic.claude-3-5-sonnet-20240620-v1:0"

# AWS Clients
s3 = boto3.client("s3")
dynamodb = boto3.resource("dynamodb")
bedrock = boto3.client("bedrock-runtime")
sns = boto3.client("sns")

paginator = s3.get_paginator("list_objects_v2")
pages = paginator.paginate(Bucket=S3_BUCKET_NAME, Prefix=prefix)
latest_log = max((obj for page in pages for obj in page.get("Contents", [])),key=lambda obj: obj["LastModified"],default=None)
if latest_log:
    print(latest_log["Key"]) 
else:
    print("No Log found")
Cloudtrail_Prefix = latest_log["Key"]
print(Cloudtrail_Prefix)

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
        print(f"Downloading {Cloudtrail_Prefix} from {S3_BUCKET_NAME}...")
        response = s3.get_object(Bucket=S3_BUCKET_NAME, Key=Cloudtrail_Prefix)
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
        prompt = f"\n\nHuman: Compare this IAM event with normal user behavior patterns. Identify any deviations that indicate suspicious activity. Score the risk on a scale of 1-10 and justify your decision and justification should be within 3 lines and tell me how the risk score is being calculated?:\n{json.dumps(log, indent=2)}\n\nAssistant:"
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

            finding = {
                "event": log["eventName"],
                "user": log.get("userIdentity", {}).get("arn", "Unknown"),
                "risk_assessment": risk_assessment
            }
            #print(finding)
            findings.append(finding)
            #print(log["eventName"], str(log.get("userIdentity", {}).get("arn", "Unknown")), risk_assessment['text'])
            score = re.search(r'Score:\s*(\d+)/\d+',risk_assessment['text'])
            if score:
                risk_score = int(score.group(1))
                print(risk_score)
            else:
                print("Risk score not found")
            # If risk is high, send alert
            #if "analysis" in risk_assessment or "standard" in risk_assessment:
            #print(findings['content'])
            #print(finding)
            if risk_score >= 2:
                print("Sending an email")
                send_alert(finding)

        except Exception as e:
            print(f"Error invoking Claude 3.5: {e}")
            findings.append({
                "event": log["eventName"],
                "user": log.get("userIdentity", {}).get("arn", "Unknown"),
                "error": str(e)
            })

    return findings

def send_alert(finding):
    """Send security alerts via AWS SNS."""
    message = f"""
    === IAM Security Alert ===
    
    Event: {finding["event"]}
    User: {finding["user"]}
    Risk Assessment: {finding["risk_assessment"]['text']}
    
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
            #print(result)
        except Exception as e:
            print(f"Error saving to DynamoDB: {e}")

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
    save_to_dynamodb(analysis_results)

    print("\n==== IAM Threat Analysis Results ====")
    print(json.dumps(analysis_results, indent=2))
    #print(str(analysis_results['event']),str(analysis_results['risk_assessment']['text']))

if __name__ == "__main__":
    main()