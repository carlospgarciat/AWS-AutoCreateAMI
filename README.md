# Auto-Create Ami for Disaster Recovery

AWS CloudFormation template that deploys:

- State Machine
- Lambda with Python scripts
- CloudWatch Event 
- Roles & Policies

...to enable the auto-creation of AMIs for all instances with tag:Environment value:Production.

CloudFormation parameter for cron job dictates how often this StepFunction runs.

##Use:
1) Compress and rename the compressed file as "lambda_function"
2) Upload each zip file with renamed file to the designated bucket
3) Deploy the CloudFormation template
