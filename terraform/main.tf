###########################
# IAM - Role and Policies #
###########################
//Generates IAM policy document using JSON to be used by resources below
data "aws_iam_policy_document" "default" { 
  statement = {
    sid = ""

    principals = {
      type = "Service"

      identifiers = [
        "lambda.amazonaws.com",
      ]
    }

    actions = [
      "sts:AssumeRole",
    ]
  }
}
//Generates IAM policy document using JSON to be used by resources below
data "aws_iam_policy_document" "ami_backup" { 
  statement = {
    actions = [
      "logs:*",
    ]

    resources = [
      "arn:aws:logs:*:*:*",
    ]
  }

  statement {
    actions = [
      "ec2:DescribeInstances",
      "ec2:CreateImage",
      "ec2:DescribeImages",
      "ec2:DeregisterImage",
      "ec2:DescribeSnapshots",
      "ec2:DeleteSnapshot",
      "ec2:CreateTags",
    ]

    resources = [
      "*",
    ]
  }
}
//Creates new role and applies the "default" policy create above
resource "aws_iam_role" "ami_backup" {
  name               = "${var.aim_role_name}"
  assume_role_policy = "${data.aws_iam_policy_document.default.json}"
}
//Creates new role policy and applies it to the role crelate above
resource "aws_iam_role_policy" "ami_backup" {
  name   = "${var.aim_role_policy_name}"
  role   = "${aws_iam_role.ami_backup.id}"
  policy = "${data.aws_iam_policy_document.ami_backup.json}"
}



################################################
# LAMBDA functions to backup and clean up AMIs #
################################################
data "aws_caller_identity" "current" {} //fetches the information needed for ownerID variable
//Creates Lambda function to backup AMI using python script
resource "aws_lambda_function" "ami_backup" {
  filename         = "${path.module}/ami_backup.zip" //zip file with python file
  function_name    = "${var.backup_function_name}"
  description      = "Automatically backup EC2 instance (create AMI)"
  role             = "${aws_iam_role.ami_backup.arn}"
  timeout          = 60
  handler          = "ami_backup.lambda_handler"
  source_code_hash = "${filebase64sha256("${path.module}/ami_backup.zip")}" //keeps track of changes
  runtime          = "python2.7"

  # Can use os library "import os"
  # and call within the python script as os.environ['region']

  environment = {
    variables = {
      region = "${var.region}"
    }
  }
}
//Creates Lambda function to backup AMI using python script
resource "aws_lambda_function" "ami_cleanup" {
  filename         = "${path.module}/ami_cleanup.zip" //zip file with python file
  function_name    = "${var.cleanup_function_name}"
  description      = "Automatically remove AMIs that have expired (delete AMI)"
  role             = "${aws_iam_role.ami_backup.arn}"
  timeout          = 60
  handler          = "ami_cleanup.lambda_handler"
   source_code_hash = "${filebase64sha256("${path.module}/ami_cleanup.zip")}" //keeps track of changes
  runtime          = "python2.7"
  environment = {
    variables = {
      region = "${var.region}"
      ownerID = "${data.aws_caller_identity.current.account_id}"
    }
  }
}

###########################################################
# CloudWatch rules to trigger lambda functions (schedule)
###########################################################
// Creates CloudWatch rules / schedules
resource "aws_cloudwatch_event_rule" "ami_backup" {
  name                = "ami_backup"
  description         = "Schedule for AMI snapshot backups"
  schedule_expression = "${var.backup_schedule}"
}
resource "aws_cloudwatch_event_rule" "ami_cleanup" {
  name                = "ami_cleanup"
  description         = "Schedule for AMI snapshot cleanup"
  schedule_expression = "${var.cleanup_schedule}"
 
}
// Links rules to targets (Lambda functions)
resource "aws_cloudwatch_event_target" "ami_backup" {
  rule      = "${aws_cloudwatch_event_rule.ami_backup.name}"
  arn       = "${aws_lambda_function.ami_backup.arn}"
}
resource "aws_cloudwatch_event_target" "ami_cleanup" {
  rule      = "${aws_cloudwatch_event_rule.ami_cleanup.name}"
  arn       = "${aws_lambda_function.ami_cleanup.arn}"
}

//Creates a Lambda permission to allow external sources invoking the Lambda function
resource "aws_lambda_permission" "ami_backup" {
  action        = "lambda:InvokeFunction"
  function_name = "${aws_lambda_function.ami_backup.function_name}"
  principal     = "events.amazonaws.com"
  source_arn    = "${aws_cloudwatch_event_rule.ami_backup.arn}"
}
resource "aws_lambda_permission" "ami_cleanup" {
  action        = "lambda:InvokeFunction"
  function_name = "${aws_lambda_function.ami_cleanup.function_name}"
  principal     = "events.amazonaws.com"
  source_arn    = "${aws_cloudwatch_event_rule.ami_cleanup.arn}"
}