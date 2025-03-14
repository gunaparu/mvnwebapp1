def get_latest_log():
    """Fetches the most recent CloudTrail log from an S3 bucket using pagination."""
    paginator = s3.get_paginator("list_objects_v2")
    pages = paginator.paginate(Bucket=S3_BUCKET_NAME, Prefix=CLOUDTRAIL_PREFIX)

    latest_log = max(
        (obj for page in pages for obj in page.get("Contents", [])),
        key=lambda obj: obj["LastModified"],
        default=None
    )

    return latest_log["Key"] if latest_log else None