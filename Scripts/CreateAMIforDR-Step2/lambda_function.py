import boto3
import collections
import datetime
import time

ec = boto3.client('ec2', 'us-east-1')
#ec = boto3.client('ec2')

def lambda_handler(event, context):
    
    # Break out the variables passed from the previous function:
    currenttime = event[0]
    instanceIds = event[1]
    iterations = event [3]
    totalInstances = event[4]
    instanceTags = event[5]
    
    print(str(currenttime), "::", "CurrentTime from previous step: ", (currenttime))
    print(str(currenttime), "::", "Total Number of Instances from last step: ", (totalInstances))
    print(str(currenttime), "::", "Instance Ids from previous step:", (instanceIds))
    print(str(currenttime), "::", "Current iterations:", (iterations))
    print(str(currenttime), "::", "Instance Tags:", (instanceTags))
    
   
    # For loop compares the total count of instances found with the filter to the total number of iterations.
    # the iteration serves as an index indicator to go through the instance list until the condition is met.
    for iterations < totalInstances:
        to_tag = collections.defaultdict(list)
        instId = instanceIds[iterations]

         # Get each instance's Name tag value
        for t in instanceTags[iterations]:
            if t['Key'] == 'Name':
                instName = t['Value']
            
            # Get retention value. note: additional functions need to be added for AMI cleanup
            # Retention value default is 1 day
            try:
                retention_days = [
                int(t.get('Value')) for t in instance['Tags']
                if t['Key'] == 'Retention'][0]
            except IndexError:
                retention_days = 1
            except ValueError:
                retention_days = 1
            except Exception as e:    
                retention_days = 1
            
            finally:
                create_time = datetime.datetime.now()
                create_fmt = create_time.strftime('%d-%m-%Y.%H.%M.%S')
        try: 
            # Create AMI fron instance
            print(str(currenttime), "::", "Creating AMI from: ", (instName))
            ami_id = ec.create_image(InstanceId=instId, Name="Lambda - " + instName + " - " + " From " + create_fmt + " - " + instId, Description="Lambda created AMI of instance " + instId)
    
            print(str(currenttime), "::", ami_id)
            AMIID = ami_id['ImageId']
            print(str(currenttime), "::", "Newly created AMI ", AMIID, "made from ", instId, "will complete in a few minutes...")
        
            # Add the tags from the instance to the AMI
            ec.create_tags(
            Resources=[ami_id['ImageId']],
            Tags= instanceTags[iterations]
            )
            
            # Retention value for the AMI
            print ("Retaining AMI %s of instance %s for %d days" % (
                    ami_id['ImageId'],
                    instId,
                    retention_days,
                ))

            # Deletion value for the AMI. note: part of the AMI cleanup
            for retention_days in to_tag.keys():
                delete_date = datetime.date.today() + datetime.timedelta(days=retention_days)
                delete_fmt = delete_date.strftime('%d-%m-%Y')
                print ("Will delete %d AMIs on %s" % (len(to_tag[retention_days]), delete_fmt))
                
                #To create a tag to an AMI when it can be deleted after retention period expires
                ec.create_tags(
                    Resources=to_tag[retention_days],
                    Tags=[
                        {'Key': 'DeleteOn', 'Value': delete_fmt},
                        ]
                    )
        except IndexError as e:
            print ("Unexpected error")
        
        #While loop compotent
        iterations +=1
    #------- while loop END 

    if iterations == totalInstances:
        done = 1
    else:
        done = 0
    
    # Pass along variables as an array to what runs this function next:
    nextstatevars = [currenttime,instanceIds,done,iterations, totalInstances, instanceTags]
    return nextstatevars
