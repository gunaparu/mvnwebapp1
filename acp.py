import boto3
import json
from collections import defaultdict

org_client = boto3.client('organizations')
MAX_CHAR_LIMIT = 5120
MAX_SCP_FILES = 5

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

def save_scp_files(scp_groups):
    for idx, group in enumerate(scp_groups, 1):
        policy = {
            "Version": "2012-10-17",
            "Statement": group
        }
        with open(f"scp_merged_{idx}.json", "w") as f:
            json.dump(policy, f, indent=2)

def generate_summary(scp_groups):
    with open("scp_merged_summary.txt", "w") as f:
        for idx, group in enumerate(scp_groups, 1):
            f.write(f"\nSCP #{idx}\n")
            f.write("=" * 60 + "\n")
            total_chars = len(json.dumps(group))
            f.write(f"Total Statements: {len(group)}\n")
            f.write(f"Approx. Characters: {total_chars} / {MAX_CHAR_LIMIT}\n\n")
            for stmt in group:
                sid = stmt.get("Sid", "(no Sid)")
                effect = stmt.get("Effect", "N/A")
                actions = stmt.get("Action", [])
                actions = actions if isinstance(actions, list) else [actions]
                resources = stmt.get("Resource", [])
                resources = resources if isinstance(resources, list) else [resources]
                condition = stmt.get("Condition", {})

                f.write(f"- Sid: {sid}\n")
                f.write(f"  Effect: {effect}\n")
                f.write(f"  Actions: {', '.join(actions)}\n")
                f.write(f"  Resources: {', '.join(resources)}\n")
                if condition:
                    f.write(f"  Condition: {json.dumps(condition)}\n")
                f.write("\n")

def generate_scp_issues(policies):
    with open("scp_issues.txt", "w") as f:
        f.write("SCP Issues Summary\n")
        f.write("=" * 60 + "\n")

        for policy in policies:
            policy_id = policy['Id']
            name = policy['Name']
            description = policy.get('Description', 'No description')

            detail = describe_policy(policy_id)
            content = json.loads(detail['Content'])
            statements = content.get("Statement", [])
            if isinstance(statements, dict):
                statements = [statements]

            char_count = len(json.dumps(content))
            f.write(f"\nPolicy Name: {name}\n")
            f.write(f"Policy ID: {policy_id}\n")
            f.write(f"Description: {description}\n")
            f.write(f"Characters Used: {char_count} / 5120\n")
            f.write(f"Number of Statements: {len(statements)}\n")
            f.write("Issues:\n")

            if char_count > 4900:
                f.write(" - [!] Policy size is near the limit\n")

            actions_seen = set()
            for stmt in statements:
                effect = stmt.get("Effect", "")
                actions = stmt.get("Action", [])
                actions = actions if isinstance(actions, list) else [actions]
                condition = stmt.get("Condition", {})

                for act in actions:
                    if act in actions_seen:
                        f.write(f" - [!] Redundant action detected: {act}\n")
                    actions_seen.add(act)

                if condition == {}:
                    f.write(" - [!] Empty condition block found\n")

                if stmt.get("Resource") == "*" and actions == ["*"]:
                    f.write(" - [!] Overly permissive: Effect=Allow/Deny on all actions and resources\n")

            f.write("-" * 60 + "\n")

def main():
    print("Fetching SCP policies...")
    policies = fetch_all_scp_policies()

    all_statements = []
    for policy in policies:
        detail = describe_policy(policy['Id'])
        content = json.loads(detail['Content'])
        statements = content.get("Statement", [])
        if isinstance(statements, dict):  # if Statement is a single dict
            statements = [statements]
        all_statements.extend(statements)

    print("Merging and de-duplicating policy statements...")
    merged = merge_statements_unique(all_statements)

    print("Splitting into ≤5 deployable SCPs...")
    scp_groups = split_into_limited_scp_groups(merged)

    print("Saving SCP files...")
    save_scp_files(scp_groups)

    print("Generating SCP summary...")
    generate_summary(scp_groups)

    print("Analyzing policy issues...")
    generate_scp_issues(policies)

    print("\nDone! The following files are generated:")
    print(" - scp_merged_1.json to scp_merged_5.json")
    print(" - scp_merged_summary.txt")
    print(" - scp_issues.txt")

if __name__ == "__main__":
    main()