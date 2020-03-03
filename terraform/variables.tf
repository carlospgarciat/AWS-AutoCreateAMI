//IAM Roles and Policies
variable "aim_role_policy_name" {
  default = "ami-backup"
  description = "set name of role policy given to lambda functions role"
}
variable "aim_role_name" {
  default = "ami-backup"
  description = "set name for role applied to lambda functions"
}
//Lambda Functions
variable "backup_function_name" {
  default = "ami_backup"
  description = "set name for the lambda backup function"
}
variable "cleanup_function_name" {
  default = "ami_cleanup"
  description = "set name for the lambda cleanup function"
}
variable "region" {
  description = "set aws region for python script"
}
//CloudWatch Alerts / Targets
variable "backup_schedule" {
  description = "cloudwatch rule schedule to trigger backups The scheduling expression. (e.g. cron(0 20 * * ? *) [minute hour * * ? *] or rate(5 minutes)"
}
variable "cleanup_schedule" {
  description = "cloudwatch rule schedule to trigger cleaups The scheduling expression. (e.g. cron(0 20 * * ? *) [minute hour * * ? *] or rate(5 minutes)"
}