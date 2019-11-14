import boto3
import collections
import datetime
import time

def lambda_handler(event, context):

# Break out the variables passed from the previous function:
    currenttime = event[0]
    instanceIds = event[1]
    iterations = event [3]
    totalInstances = event[4]
    instanceTags = event[5]
    

    if iterations == totalInstances:
        print(str(currenttime), "::", "SUCCESS")
        print ("Total AMIs:",(iterations))
    else:
        print(str(currenttime), "::", "FAILED: Some instances were not copied successfully...")
        print ("Total AMIs:",(iterations))
        print ("Total Instances:",(totalInstances))
