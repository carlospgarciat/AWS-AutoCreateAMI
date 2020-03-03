# Auto-Create Ami for Disaster Recovery

AWS CloudFormation template that deploys:

- State Machine
- Lambda with Python scripts
- CloudWatch Event 
- Roles & Policies

...to enable the auto-creation of AMIs for all instances with tag:Environment value:Production.

CloudFormation parameter for cron job dictates how often this StepFunction runs.
