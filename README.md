
# EC2 Auto-Management System

## Overview
This project automates EC2 instance management based on **Snoozing Tags** using AWS Lambda functions. It ensures seamless automation of instance start/stop operations while maintaining a detailed log of all changes in Amazon S3.

##  Architecture
The solution consists of three AWS Lambda functions:
1. **Backup EC2 State** → Captures the current state of EC2 instances and stores the details in an S3 `.CSV` file.
2. **Start EC2 Instances** → Checks `Snoozing` tag values and starts instances accordingly while resetting the Snoozing tag value.
3. **Stop EC2 Instances & Revert Tags** → Stops only instances started during execution and restores Snoozing tags to their original values.

### **🛠 Services Used**
- **AWS Lambda** → Executes automation workflows.
- **Amazon S3** → Stores `.CSV` logs of instance states.
- **Amazon EC2** → Manages compute instances.
- **AWS EventBridge** → Triggers automation at scheduled intervals.
- **IAM Roles** → Provides Lambda access to EC2 & S3.

## CSV File Structure
Each `.CSV` file maintains logs of changes at different stages of execution.

### **Backup Log (`backup_ec2_state_YYYY-MM-DD.csv`)**
| Instance ID | Instance Name | Previous State | Snoozing Tag |
|------------|--------------|---------------|--------------|
| i-1234567890abcd | WebServer-01 | Stopped | Yes |

### **Start Log (`started_servers_YYYY-MM-DD.csv`)**
| Instance ID | Instance Name | Previous State | Previous Snoozing Tag | New State | New Snoozing Tag |
|------------|--------------|---------------|---------------------|------------|-----------------|
| i-1234567890abcd | WebServer-01 | Stopped | Yes | Started | "" |

### **Stop Log (`restored_servers_YYYY-MM-DD.csv`)**
| Instance ID | Instance Name | Previous State | Previous Snoozing Tag | New Snoozing Tag | Current State | Restored Snoozing Tag |
|------------|--------------|---------------|---------------------|-----------------|--------------|------------------|
| i-1234567890abcd | WebServer-01 | Running | Yes | "" | Stopped | Yes |

##  Deployment Steps
To deploy this automation in your AWS environment:
1. **Set Up IAM Role Permissions**
   - Grant Lambda permission to **manage EC2 instances**, **read/write to S3**, and **modify tags**.
2. **Deploy Lambda Functions**
   - Upload each function into the AWS Lambda console.
   - Set environment variables for S3 bucket names and execution settings.
3. **Schedule with EventBridge**
   - Define a recurring schedule for **weekly executions** to automate management.
4. **Verify S3 Logs**
   - Ensure logs are stored correctly in S3 for review.


##  Contributions
Feel free to submit issues, feature requests, or contribute enhancements via **Pull Requests**!
