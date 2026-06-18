# ========================================================================================
# FILE: verify_deployment.py
# PURPOSE: Automated Multi-Cloud Post-Apply Validation and Assertions
# ========================================================================================

import os
import time
import boto3
from azure.identity import DefaultAzureCredential
from azure.mgmt.network import NetworkManagementClient

def test_aws_s3_replication():
    print("[TESTING] Initiating AWS Cross-Region Replication Test Loop...")
    s3_source_client = boto3.client('s3', region_name='eu-central-1')
    s3_dest_client = boto3.client('s3', region_name='us-west-1')
    
    source_bucket = "amity-s3-replication-source-bucket"
    dest_bucket = "amity-s3-replication-dest-bucket"
    test_key = "integration_test_payload.txt"
    payload_content = "TechNova Solutions Automated Infrastructure Validation Run."
    
    # Inject test file payload into source region
    s3_source_client.put_object(Bucket=source_bucket, Key=test_key, Body=payload_content)
    print(f"[INFO] Uploaded test object to: {source_bucket}")
    
    # 60-Second Polling Loop to check for regional mirror arrival
    max_attempts = 6
    polling_delay = 10
    object_replicated = False
    
    for attempt in range(1, max_attempts + 1):
        print(f"[INFO] Inspecting destination target bucket (Attempt {attempt}/{max_attempts})...")
        try:
            s3_dest_client.head_object(Bucket=dest_bucket, Key=test_key)
            print("[SUCCESS] Cross-region object replication asset successfully verified!")
            object_replicated = True
            break
        except Exception:
            print(f"[WARN] Object path unverified yet. Dormant pause for {polling_delay}s...")
            time.sleep(polling_delay)
            
    # Clean up verification assets to keep environments clear
    s3_source_client.delete_object(Bucket=source_bucket, Key=test_key)
    s3_dest_client.delete_object(Bucket=dest_bucket, Key=test_key)
    
    assert object_replicated, "CRITICAL REPLICATION FAULT: Data pipeline failed validation metrics!"

def test_azure_network_firewall():
    print("[TESTING] Auditing Azure Network Stateful Security Group Profiles...")
    credential = DefaultAzureCredential()
    subscription_id = os.environ.get("AZURE_SUBSCRIPTION_ID", "00000000-0000-0000-0000-000000000000")
    
    network_client = NetworkManagementClient(credential, subscription_id)
    resource_group = "amity-project-rg"
    nsg_name = "project-nsg"
    
    nsg = network_client.network_security_groups.get(resource_group, nsg_name)
    rules = nsg.security_rules
    
    rdp_rule_valid = False
    for rule in rules:
        if rule.name == "Allow-RDP" and rule.destination_port_range == "3389" and rule.access == "Allow":
            print("[SUCCESS] Verified matching active inbound RDP filter path.")
            rdp_rule_valid = True
            break
            
    assert rdp_rule_valid, "CRITICAL PERIMETER FAULT: Firewall configuration mismatch discovered!"

if __name__ == "__main__":
    print("=====================================================================")
    print("        TECHNOVA SOLUTIONS AUTOMATED DEPLOYMENT AUDIT RUN            ")
    print("=====================================================================")
    test_aws_s3_replication()
    test_azure_network_firewall()
    print("=====================================================================")
    print("        ALL INTEGRATION ASSERTIONS COMPLETED SUCCESSFULLY            ")
    print("=====================================================================")