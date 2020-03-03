import boto3
import time
import datetime
import collections

region = 'us-east-1'
client = boto3.client('ec2', region)

class AmiException(Exception):
    pass

def lambda_handler(event, context):
    ##
    currenttime = datetime.datetime.now().strftime("%y-%m-%d-%H-%M-%S")
    instanceTags = []
    instanceIds = []
    iterations = 0 
    pending_backups = 0
    ##

    # Pagination
    paginator = client.get_paginator('describe_instances')
    response =[]
    response_iterator = paginator.paginate(Filters=[{'Name': 'tag:Environment','Values': ['Production','Management']}])
    for page in response_iterator:
        for item in page.get('Reservations'):
            response.append(item)
    
    ##
    instances = sum([[i for i in r['Instances']]for r in response], [])
    totalInstances = len(instances)
    print (str(currenttime), "::", "Found %d instances that need backing up..." % totalInstances)
    
    ##
    for instance in instances:
        instanceIds.append(instance['InstanceId'])
        instanceTags.append(instance['Tags'])

    while iterations < totalInstances:
        to_tag = collections.defaultdict(list)
        instId = instanceIds[iterations]

        ##
        for t in instanceTags[iterations]:
            if t['Key'] == 'Name':
                instName = t['Value']
            else:
                instName = " "

            #
            try:
                retention_days = [
                int(t.get('Value')) for t in instance['Tags']
                if t['Key'] == 'Retention'][0]
            except IndexError:
                retention_days = 7
            except ValueError:
                retention_days = 7
            finally:
                create_time = datetime.datetime.now()
                create_fmt = create_time.strftime('%m-%d-%Y.%H.%M.%S')
        ##
        try: 
            #
            print(str(currenttime), "::", "Creating AMI from: ", (instName))
            ami_id = client.create_image(InstanceId=instId, Name="Lambda - " + instName + " - " + " From " + create_fmt + " - " + instId, Description="Lambda created AMI of instance " + instId)
            #
            print(str(currenttime), "::", ami_id)
            AMIID = ami_id['ImageId']
            to_tag[retention_days].append(AMIID)
            print(str(currenttime), "::", "Newly created AMI ", AMIID, "made from ", instId, "will complete in a few minutes...")
            #
            client.create_tags(
            Resources=[AMIID],
            Tags= instanceTags[iterations]
            )
            #
            print ("Retaining AMI %s of instance %s for %d days" % (
                    ami_id['ImageId'],
                    instId,
                    retention_days,
                ))
            
            #
            for retention_days in to_tag.keys():
                delete_date = datetime.date.today() + datetime.timedelta(days=retention_days)
                delete_fmt = delete_date.strftime('%m-%d-%Y')
                print ("Will delete %d AMIs on %s" % (len(to_tag[retention_days]), delete_fmt))
                client.create_tags(Resources=to_tag[retention_days],Tags=[{'Key': 'DeleteOn', 'Value': delete_fmt},{'Key': 'Origin', 'Value': 'TestFn'}])
            #        
            iterations +=1
        except Exception as e:
            pending_backups += 1
        
        if pending_backups > 0:
            log_message = 'Could not back up every instance.'
            raise AmiException(log_message)

if __name__ == '__main__':
    lambda_handler(None, None)