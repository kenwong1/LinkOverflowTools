import sys, boto.ec2, os, argparse, ConfigParser

''' This will create the command line argument parser and return it '''
def create_parser():
    defaultSettingsFile = os.path.expanduser("~/.aws.settings")
    parser = argparse.ArgumentParser(
                        prog="showstate.py",
                        usage="%(prog)s [-h] [--aws-config <file>]",
                        description="Tool for showing state of EC2 instances") 
    parser.add_argument('--aws-settings',
                        default=defaultSettingsFile,
                        help="Specify the location of the per-user AWS configuration "
                            "(default is '.aws.settings' in the user's home directory). These settings contain "
                            "important keys and should be kept secret at all times.")   
    return parser

''' This will check the AWS settings file and return the dictionary '''
def validateConfig():
    parser = create_parser()
    parsedArgs = parser.parse_args()
    awsConfigDict = {}
    try:
        awsConfigParser = ConfigParser.RawConfigParser()
        awsConfigParser.read(parsedArgs.aws_settings)
        awsConfigDict['EC2_AccessKeyID'] = awsConfigParser.get("EC2", "AccessKeyID")
        awsConfigDict['EC2_SecretAccessKey'] = awsConfigParser.get("EC2", "SecretAccessKey")
        awsConfigDict['EC2_AvailabilityZone'] = awsConfigParser.get("EC2", "AvailabilityZone")

    except (ConfigParser.Error) as mesg:
        raise Exception("AWS settings file ({0}): {1}".format(parsedArgs.aws_settings, mesg))

    return awsConfigDict        

''' This will get the ip address and state of each EC2 instance '''
def getEC2InstanceStates(accessKeyId, secretAccessKey, availabilityZone):
    try:
        ec2 = boto.ec2.connect_to_region(availabilityZone, aws_access_key_id=accessKeyId, aws_secret_access_key=secretAccessKey)
    except boto.exception.EC2ResponseError as mesg:
        raise Exception("Unable to connect to EC2")
    
    if ec2 is None:
        raise Exception("Unable to connect to EC2")

    stateList = []
    ipList = []
    instances = ec2.get_only_instances()
    for instance in instances:
        stateList.append(instance.state)
        ipList.append(instance.ip_address)

    return (ipList, stateList)

''' Once we have a list of ip addresses and states, iterate over each one and display them to the user '''
try:
    awsConfigDict = validateConfig()

    (ipList, stateList) = getEC2InstanceStates(awsConfigDict['EC2_AccessKeyID'],
                   awsConfigDict['EC2_SecretAccessKey'],
                   awsConfigDict['EC2_AvailabilityZone'])
except Exception as mesg:
    print >>sys.stderr, "Error:", mesg
    sys.exit(1)

print "\nIP Address and State of all instances:\n"
for x in range(1, len(ipList)):
    print "\n", ipList[x], " - ", stateList[x], "\n"
