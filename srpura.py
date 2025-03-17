import boto3
from datetime import datetime, timedelta

def get_s3_bucket_sizes(session):
    s3_client = session.client('s3')
    cw_client = session.client('cloudwatch', region_name='us-east-1')

    total_bytes = 0
    bucket_sizes = {}

    try:
        buckets = s3_client.list_buckets()['Buckets']
        for bucket in buckets:
            bucket_name = bucket['Name']
            try:
                response = cw_client.get_metric_statistics(
                    Namespace='AWS/S3',
                    MetricName='BucketSizeBytes',
                    Dimensions=[
                        {'Name': 'BucketName', 'Value': bucket_name},
                        {'Name': 'StorageType', 'Value': 'StandardStorage'}
                    ],
                    StartTime=datetime.utcnow() - timedelta(days=2),
                    EndTime=datetime.utcnow(),
                    Period=86400,
                    Statistics=['Average']
                )

                datapoints = response.get('Datapoints', [])
                if datapoints:
                    size_bytes = datapoints[-1]['Average']
                    bucket_sizes[bucket_name] = size_bytes / (1024 ** 3)  # Convert to GB
                    total_bytes += size_bytes

            except Exception as e:
                print(f"Error fetching size for bucket {bucket_name}: {e}")
                continue

        total_gb = total_bytes / (1024 ** 3)
        return bucket_sizes, total_gb

    except Exception as e:
        print(f"Error listing buckets: {e}")
        return {}, 0

# Example usage
session = boto3.Session(region_name="us-east-1")
bucket_sizes, total_storage_gb = get_s3_bucket_sizes(session)

for bucket, size in bucket_sizes.items():
    print(f"Bucket: {bucket}, Size: {size:.2f} GB")

print(f"\nTotal Storage Used: {total_storage_gb:.2f} GB")