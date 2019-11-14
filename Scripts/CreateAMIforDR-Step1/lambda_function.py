import boto3
import time
import datetime
import collections

ec = boto3.client('ec2', 'us-east-1')

def lambda_handler(event, context):
    # Variable initialization
    currenttime = datetime.datetime.now().strftime("%y-%m-%d-%H-%M-%S")#//Get time date information
    reservations = ec.describe_instances(Filters=[{'Name': 'tag:Environment','Values': ['Production','Management']}]).get('Reservations', [])#//Get instaces filtered by tag value.
    instances = sum([[i for i in r['Instances']]for r in reservations], [])#//Add up all instances
    totalInstances = len(instances)
    instanceTags = []
    instanceIds = []
    # Req for step logic
    done = 0 
    iterations = 0 
    print (str(currenttime), "::", "Found %d instances that need backing up..." % totalInstances)

    print(str(currenttime), "::", "Fetching Instance information...")
    
    # Fetch a list of tags and ids
    for instance in instances:
        instanceIds.append(instance['InstanceId'])
        instanceTags.append(instance['Tags'])
  
    
    # Pass along variables as an array to what runs this function next:
    nextstatevars = [currenttime,instanceIds,done,iterations, totalInstances,instanceTags]
    return nextstatevars