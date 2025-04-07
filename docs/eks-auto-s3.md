# Secure and cost-effective solution for integrating Amazon Simple Storage Service (S3) with our Amazon Elastic Kubernetes Service (EKS) Auto
As a Solution Architect, I have been tasked by management to design a secure and cost-effective solution for integrating Amazon Simple Storage Service (S3) with our Amazon Elastic Kubernetes Service (EKS) Auto Scaling cluster. 

#### The solution must adhere to the following requirements:

- **Permissions Boundary for EKS Auto Scaling Cluster:** Implement fine-grained access controls to ensure that the EKS cluster operates within defined permissions.​
- **Encryption of Data in Transit:** 
      Ensure that all data transferred to and from S3 is encrypted during transit.​
- **Block Public Access to S3 Buckets:** 
      Prevent unauthorized public access to S3 buckets.​
- **Disable ACLs for S3 Access:** 
      Manage access exclusively through policies by disabling Access Control Lists (ACLs)
- **Use S3 Bucket Policies Specific to the Product Use Case:** 
      Tailor bucket policies to align with specific application requirements.​
- **Implement Least Privilege Access:** 
      Grant only the necessary permissions required for each user or service.​
- **Encryption of Data at Rest:** 
      Ensure that data stored in S3 is encrypted.​
- **Implement S3 Object Lock for Write Once Read Many (WORM) Model:** 
      Protect objects from being deleted or overwritten for a specified retention period
- **Use S3 Versioning Only if Absolutely Required:** 
      Enable versioning selectively to manage storage costs and complexity.​
- **Evaluate S3 Bucket Naming Autogeneration Against Maintenance Ease:** 
      Consider the trade-offs between automatic naming conventions and ease of maintenance.​
- **Mutual TLS (mTLS) Access for S3:** 
      Implement mTLS to authenticate both client and server during data transfer.​
- **Manage S3 Storage Lifecycle:** 
      Define policies to transition objects between storage classes and expire them as needed
- **Audit S3 Inventory:** 
      Regularly review S3 inventory reports to monitor and manage stored objects.
- **Use Cross-Region Replication Sparingly:** 
      Limit replication to scenarios where it's absolutely necessary to control costs.​
- **Restrict Amazon S3 Access to Required VPCs:** 
      Ensure that only specific Virtual Private Clouds (VPCs) have access to S3 resources.​
- **Enable CloudWatch Metrics for S3 Bucket Access if Necessary:** 
      Monitor S3 access patterns and performance using CloudWatch.​
- **Enable CloudWatch Alerts for Critical S3 Operations:** 
      Set up alerts for operations such as data deletion or policy changes.​
- **Enable S3 Access Logs:** 
      Maintain logs of access requests to S3 for auditing and monitoring purposes.

#### Solution Overview:
To meet the above requirements, the following architecture and configurations are proposed:

- **VPC Gateway Endpoint for S3:** Establish a VPC Gateway Endpoint to enable private, secure, and cost-effective communication between the EKS cluster and S3 without traversing the public internet. This approach eliminates data transfer costs associated with NAT gateways. ​
![image](https://github.com/user-attachments/assets/b559a88e-05bc-4622-805f-6093fc653276)
 
- **IAM Roles for Service Accounts (IRSA):** Utilize IRSA to associate IAM roles with Kubernetes service accounts, granting pods the minimal permissions necessary to access S3. This aligns with the principle of least privilege and simplifies permissions management.

- **S3 Bucket Policies and ACLs:**
  - **Disable ACLs:** Set the S3 Object Ownership setting to "Bucket owner enforced" to disable ACLs and manage access exclusively through policies. ​
  - **Block Public Access:** Enable S3 Block Public Access settings to prevent unauthorized public access to S3 buckets.
  - **Custom Bucket Policies:** Define bucket policies tailored to the application's specific access requirements.

- **Data Encryption:**
 - **In Transit:** Enforce the use of HTTPS (TLS) for all data transfers to and from S3 to encrypt data in transit.
 - **At Rest:** Enable server-side encryption with Amazon S3-managed keys (SSE-S3) or AWS Key Management Service (SSE-KMS) to encrypt data stored in S3. ​
   
- **S3 Object Lock and Versioning:**
  - **Object Lock:** Implement S3 Object Lock in compliance mode to enforce a Write Once Read Many (WORM) model, protecting objects from being deleted or overwritten during a specified retention period. ​
  - **Versioning:** Enable versioning only for buckets where it is necessary to retain multiple versions of objects, considering the associated storage costs.​
- **Mutual TLS (mTLS):** Implement mTLS for services that require enhanced authentication mechanisms, ensuring both client and server verify each other's identity during data transfer.​
- **Storage Lifecycle Management:** Define S3 Lifecycle policies to automatically transition objects between storage classes (e.g., from S3 Standard to S3 Glacier) and expire objects that are no longer needed, optimizing storage costs. ​
- **Monitoring and Auditing:**
  - **CloudWatch Metrics and Alerts:** Enable CloudWatch metrics to monitor S3 access patterns and set up alerts for critical operations such as data deletions or policy changes.​
  - **S3 Access Logs:** Activate S3 server access logging to capture detailed records of requests made to the bucket, facilitating auditing and compliance.​
  - **S3 Inventory:** Use S3 Inventory reports to audit and report on the replication and encryption status of objects for compliance and cost management.​
- **Cross-Region Replication:** Implement cross-region replication only when necessary for disaster recovery or compliance requirements, as it incurs additional costs.

## Architecture Overview

The architecture comprises the following components:

- **Amazon Virtual Private Cloud (VPC):** The isolated network environment hosting the resources.
  - **Public Subnet:**
    - **Internet Gateway (IGW):** Facilitates internet access for resources within the VPC.
    - **NAT Gateway (NAT):** Allows instances in the private subnet to initiate outbound IPv4 traffic to the internet while preventing unsolicited inbound traffic.
  - **Private Subnet:**
    - **EKS Node Group:** A group of Amazon EC2 instances managed by Amazon EKS, configured for auto scaling.
    - **EKS Pods:** The Kubernetes pods running within the EKS Node Group.
  - **VPC Gateway Endpoint for S3:** Enables private connectivity between the VPC and Amazon S3 without requiring internet access.

- **Amazon S3 Bucket:** The object storage service where data is stored and accessed by the EKS Pods.
  [create_secure_s3_bucket-sh](https://gist.github.com/naren4b/10c01a1003afd391cd87959df2bfac5d#file-create_secure_s3_bucket-sh)


## Data Flow

1. **EKS Pods** initiate requests to the **Amazon S3 Bucket**.
2. These requests are routed through the **VPC Gateway Endpoint for S3**, ensuring that the traffic remains within the AWS network, enhancing security and reducing data transfer costs.
3. For any outbound internet traffic (e.g., accessing external services), **EKS Pods** route requests through the **NAT Gateway**, which then communicates via the **Internet Gateway**.


|Feature	| Description|
|---|---|
|Region Match|	EKS and S3 in same region → no data cost|
|VPC Gateway Endpoint|	Private route → no NAT gateway charges|
|IRSA|	Least privilege IAM access per pod|
|S3 Encryption + Logging|	Handled via bucket policies|

## Benefits

- **Security:** Traffic between EKS Pods and S3 does not traverse the public internet, reducing exposure to potential threats.
- **Cost Efficiency:** Utilizing the VPC Gateway Endpoint eliminates data transfer charges associated with accessing S3 over the internet.
- **Performance:** Private connectivity offers lower latency and higher throughput compared to internet-based access.

## References

- [Gateway Endpoints for Amazon S3](https://docs.aws.amazon.com/vpc/latest/privatelink/vpc-endpoints-s3.html)
- [Access S3 Buckets from AWS EKS Cluster using IRSA](https://medium.com/@umar20/access-s3-buckets-from-aws-eks-cluster-using-irsa-526cab3be48)
- [AWS Architecture Icons](https://aws.amazon.com/architecture/icons/)

