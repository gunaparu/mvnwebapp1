import boto3
import json
import os
from collections import defaultdict
from datetime import datetime

org_client = boto3.client('organizations')
MAX_CHAR_LIMIT = 5120
MAX_SCP_FILES = 5

OUTPUT_DIR = "output"
SCP_DIR = os.path.join(OUTPUT_DIR, "scps")
REPORT_DIR = os.path.join(OUTPUT_DIR, "reports")
os.makedirs(SCP_DIR, exist_ok=True)
os.makedirs(REPORT_DIR, exist_ok=True)

def fetch_all_scp_policies():
    paginator = org_client.get_paginator('list_policies')
    policies = []
    for page in paginator.paginate(Filter='SERVICE_CONTROL_POLICY'):
        policies.extend(page['Policies'])
    return policies

def describe_policy(policy_id):
    return org_client.describe_policy(PolicyId=policy_id)['Policy']

def merge_statements_unique(statements_list):
    unique = []
    seen = set()
    for stmt in statements_list:
        key = (
            stmt.get("Effect"),
            json.dumps(stmt.get("Action", "")),
            json.dumps(stmt.get("Resource", "")),
            json.dumps(stmt.get("Condition", {}))
        )
        if key not in seen:
            seen.add(key)
            unique.append(stmt)
    return unique

def split_into_limited_scp_groups(statements, max_files=MAX_SCP_FILES):
    groups = [[] for _ in range(max_files)]
    lengths = [0] * max_files

    for stmt in sorted(statements, key=lambda s: len(json.dumps(s)), reverse=True):
        stmt_len = len(json.dumps(stmt))
        placed = False
        for i in range(max_files):
            if lengths[i] + stmt_len < MAX_CHAR_LIMIT:
                groups[i].append(stmt)
                lengths[i] += stmt_len
                placed = True
                break
        if not placed:
            raise ValueError("Statements exceed space for 5 SCPs. Manual cleanup needed.")
    return groups

def analyze_policy_issues(policies):
    issues = []
    for policy in policies:
        policy_id = policy['Id']
        policy_name = policy['Name']
        description = policy.get("Description", "")
        create_date = policy.get("CreateDate", "")
        detail = describe_policy(policy_id)
        content = json.loads(detail['Content'])
        statements = content.get("Statement", [])
        if isinstance(statements, dict):
            statements = [statements]

        if not statements:
            issues.append(f"Policy '{policy_name}' ({policy_id}) has no statements.")
            continue

        seen_actions = set()
        for stmt in statements:
            actions = stmt.get("Action", [])
            if isinstance(actions, str):
                actions = [actions]
            for act in actions:
                if act in seen_actions:
                    issues.append(f"Redundant action '{act}' found in policy '{policy_name}' ({policy_id})")
                else:
                    seen_actions.add(act)

            if stmt.get("Effect") != "Deny":
                issues.append(f"Policy '{policy_name}' ({policy_id}) has a non-Deny effect, which is discouraged.")

            if not stmt.get("Condition") and "*" in actions:
                issues.append(f"Policy '{policy_name}' ({policy_id}) has wildcard Action without condition.")

        char_len = len(json.dumps(content))
        if char_len > 5000:
            issues.append(f"Policy '{policy_name}' ({policy_id}) is nearing character size limit ({char_len}/5120)")

    return issues

def save_scp_files(scp_groups):
    for idx, group in enumerate(scp_groups, 1):
        policy = {
            "Version": "2012-10-17",
            "Statement": group
        }
        with open(os.path.join(SCP_DIR, f"scp_merged_{idx}.json"), "w") as f:
            json.dump(policy, f, indent=2)

def save_summary_file(all_statements):
    summary_policy = {
        "Version": "2012-10-17",
        "Statement": all_statements
    }
    with open(os.path.join(SCP_DIR, "scp_merged_summary.json"), "w") as f:
        json.dump(summary_policy, f, indent=2)

def save_issues_file(issues):
    with open(os.path.join(REPORT_DIR, "scp_issues.txt"), "w") as f:
        for issue in issues:
            f.write(issue + "\n")

def main():
    print("Fetching all SCPs...")
    policies = fetch_all_scp_policies()
    all_statements = []

    print("Describing and collecting statements...")
    for policy in policies:
        detail = describe_policy(policy['Id'])
        content = json.loads(detail['Content'])
        statements = content.get("Statement", [])
        if isinstance(statements, dict):
            statements = [statements]
        all_statements.extend(statements)

    print("Analyzing policy issues...")
    issues = analyze_policy_issues(policies)
    save_issues_file(issues)

    print("Merging unique statements...")
    merged = merge_statements_unique(all_statements)

    print("Saving SCP summary file...")
    save_summary_file(merged)

    print("Splitting into 5 deployable SCPs...")
    scp_groups = split_into_limited_scp_groups(merged)

    print("Saving merged SCP files...")
    save_scp_files(scp_groups)

    print("\nDone!")
    print(f"→ SCPs stored in:      {SCP_DIR}")
    print(f"→ Issues report saved: {os.path.join(REPORT_DIR, 'scp_issues.txt')}")

if __name__ == "__main__":
    main()