import boto3

# Function to get total S3 storage in GB
def get_s3_size(session):
    s3_client = session.client("s3")
    total_size = 0

    try:
        response = s3_client.list_buckets()
        for bucket in response["Buckets"]:
            bucket_name = bucket["Name"]
            try:
                # Paginate through all objects in the bucket
                paginator = s3_client.get_paginator("list_objects_v2")
                for page in paginator.paginate(Bucket=bucket_name):
                    if "Contents" in page:
                        for obj in page["Contents"]:
                            total_size += obj["Size"]
            except Exception as e:
                print(f"Error accessing bucket {bucket_name}: {e}")
                continue

        # Convert bytes to GB
        return total_size / (1024 ** 3)

    except Exception as e:
        print(f"Failed to get S3 bucket sizes: {e}")
        return 0

# Example usage
session = boto3.Session(region_name="us-east-1")
size_gb = get_s3_size(session)
print(f"Total S3 storage used: {size_gb:.2f} GB")