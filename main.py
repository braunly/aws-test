import datetime
import socket
import urllib.request
import urllib.error

import boto3


A_DOMAIN = "a.braunly-test.pp.ua"
B_DOMAIN = "b.braunly-test.pp.ua"
C_DOMAIN = "c.braunly-test.pp.ua"

ec2 = boto3.client('ec2')


def is_online(hostname=None):
    """Check server online status."""
    if hostname is not None:
        # HTTP verification
        url = 'http://{}'.format(hostname)
        try:
            http_code = urllib.request.urlopen(url).getcode()
        except urllib.error.URLError:
            http_code = -1

        # TCP verification
        ip = socket.gethostbyname(hostname)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connect_result = sock.connect_ex((ip, 22))

        if http_code == 200 or connect_result == 0:
            return True
    return False


def print_instances():
    """Print instances table."""

    print('Instance name\tInstance state')
    for instance in ec2.describe_instances(Filters=[{'Name': 'key-name', 'Values': ['denysiuk']}])['Reservations']:
        name = instance['Instances'][0]['Tags'][0]['Value']
        state = instance['Instances'][0]['State']['Name']
        print("{}\t{}".format(name, state))


def main():
    """Main script function."""
    for hostname in (A_DOMAIN, B_DOMAIN, C_DOMAIN):
        if not is_online(hostname):
            # Get stopped instance
            instance = ec2.describe_instances(Filters=[{'Name': 'key-name', 'Values': ['denysiuk']},
                                                       {'Name': 'instance-state-name', 'Values': ['stopped']}])
            # Get instance ID and name
            instance_id = instance['Reservations'][0]['Instances'][0]['InstanceId']
            instance_name = instance['Reservations'][0]['Instances'][0]['Tags'][0]['Value']
            # Create AMI of the stopped instance
            cur_date = datetime.datetime.now().strftime('%d.%m.%y_%H-%M')
            image_id = ec2.create_image(InstanceId=instance_id, Name='{}_{}'.format(instance_name, cur_date))['ImageId']
            # Add tag
            ec2.create_tags(Resources=[image_id],
                            Tags=[{
                                'Key': 'Description',
                                'Value': '{}_{}'.format(instance_name, cur_date)}
                            ])
            # Terminate stopped EC2 after AMI creation.
            ec2.terminate_instances(InstanceIds=[instance_id])

            # Clean up AMIs older than 7 days
            response = ec2.describe_images()
            time_limit = datetime.datetime.now() - datetime.timedelta(days=7)
            today = time_limit.isoformat()
            for data in response["Images"]:
                image_created_time = data["CreationDate"]
                if image_created_time < today:
                    image_id = data["ImageId"]
                    ec2.deregister_image(ImageId=image_id)
    print_instances()


if __name__ == '__main__':
    main()
