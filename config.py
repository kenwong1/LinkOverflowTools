#
# Helper functions for the launch.py utility, to parse and validate the command-line arguments
# and configuration settings. In our context "configuration" is held in a couple of files:
#   - ".aws.settings" file (per-user/private configuration)
#   - "instance.config" file (describing the VM instance(s) te be created)
# Although these files have default names/locations, the user can overide them on the command line.
#
import sys, argparse, os, ConfigParser

# Constant: maximum number of EC2 instances we're prepared to create. This only exists for
# the purposes of limiting the money spent :-)
MAX_EC2_INSTANCES = 5


#
# Helper function for validating whether a file is only accessible to the owner of the file.
# This is an important check for private key files. Return None on success, or a string error message
# if there's a failure.
#
def checkFileIsPrivate(fileName):
    try:
        stat = os.stat(fileName)
    except OSError:
        return "({0}) is missing.".format(fileName)
    if (stat.st_mode & 0400 == 0):
        return "({0}) is not readable.".format(fileName)
    if (stat.st_mode & 0077 != 0):
        return "({0}) is readable/writable by other users.".format(fileName)
    return None


#
# Validate our command line arguments, and configuration files. Return a tuple containing the following
# things:
#
#   (Number of instances, AWS settings dict, Instance Configuration dict)
#
#
# Where:
#   Number of instances - An integer > 1, stating the number of EC2 instances to create.
#   AWS settings - A dictionary containing AWS settings (typically private to each user. This includes the
#      standard AWS connection keys, as well as the user's selected availability zone.
#   Instance Configuration - A dictionary containing information about the VM instances we're going to create
#      (such as AMI type, etc). This information is *not* per-user and should be version-controlled along
#      with the product's source code, so the platform and the product will remain in-sync.
# 
# We throw an exception if an error is encountered.
#
#   KW: [Process] Missing "djangoProj" return value in comment and description above
#
def validateConfig():
    '''Parse and validate command-line arguments, and ensure the expected configuration files are present
    and contain the required configuration values'''
        
    #
    # Parse command-line arguments. This uses the standard Python argparse module to collect and validate
    # input parameters.
    #
    defaultSettingsFile = os.path.expanduser("~/.aws.settings")
    parser = argparse.ArgumentParser(
                        prog="launch.py",
                        usage="%(prog)s [-h] [--aws-config <file>] [--system-config <file>] <django_proj> <num_servers>",
                        description="Deployment tool for creating multiple AWS instances, then running "
                            "a Django application on all of them.")	
    parser.add_argument('--aws-settings',
                        default=defaultSettingsFile,
                        help="Specify the location of the per-user AWS configuration "
                            "(default is '.aws.settings' in the user's home directory). These settings contain "
                            "important keys and should be kept secret at all times.")	
    parser.add_argument('--instance-config',
                        default='instance.config',
                        help="Specify the location of the instance configuration file, which is the version-controlled "
                            "configuration of the AWS EC2 instances to be created (default is 'instance.config' in the current directory)")  	
    parser.add_argument('django_proj',
                        type=str,
                        help="Path to the Django project (the directory containing manage.py)")	
    parser.add_argument('num_servers',
                        type=int,
                        help="The number of AWS instances to create and install the application on.")
    parsedArgs = parser.parse_args()
    
    #
    # The number of instances to be created must be at least 1 (and for now, we limit to small maximum value - MAX_EC2_INSTANCES)
    #
    # KW: [Test] Verify num_servers with values of -1, 0, 1, 5, 6
    #
    numServers = parsedArgs.num_servers
    if (numServers < 1) or (numServers > MAX_EC2_INSTANCES):
        raise Exception("Invalid number of EC2 instances requested: {0}".format(numServers))

    #
    # Validate that "django_proj" is a directory that contains a manage.py file.
    #
    # KW: [Test] Verify invalid directory path, path with no manage.py, and path with invalid manage.py
    #
    djangoProj = parsedArgs.django_proj
    if not os.path.isfile(djangoProj + "/manage.py"):
        raise Exception("Directory {0} does not appear to be a valid Django project.".format(djangoProj))

    #
    # The AWS settings file must exist, and must be accessible *only* by the current user. This file contains
    # security keys and must remain protected.
    #
    # KW: [Test] Verify settings file permission that is accessible by everyone, by owner only, and not by owner. 	
    #
    error = checkFileIsPrivate(parsedArgs.aws_settings)
    if error != None:
        raise Exception("AWS settings file " + error)

    #
    # now, read the key/values from the AWS settings file into the dictionary we'll return to our caller.
    #
    # KW: [Test] Also verify if settings file is not present and invalid (e.g. contains missing properties).
    #
    awsConfigDict = {}
    try:
        awsConfigParser = ConfigParser.RawConfigParser()
        awsConfigParser.read(parsedArgs.aws_settings)
        awsConfigDict['EC2_AccessKeyID'] = awsConfigParser.get("EC2", "AccessKeyID")
        awsConfigDict['EC2_SecretAccessKey'] = awsConfigParser.get("EC2", "SecretAccessKey")
        awsConfigDict['EC2_AvailabilityZone'] = awsConfigParser.get("EC2", "AvailabilityZone")
        awsConfigDict['EC2_SSHKeyPair'] = awsConfigParser.get("EC2", "SSHKeyPair")
        awsConfigDict['EC2_SSHKeyPairFile'] = awsConfigParser.get("EC2", "SSHKeyPairFile")

    except (ConfigParser.Error) as mesg:
        raise Exception("AWS settings file ({0}): {1}".format(parsedArgs.aws_settings, mesg))
    
    #
    # The SSH key file must exist and only be accessible to the owner.
    #
    # KW: [Test] Verify if SSH file is missing, accessible by everyone, by owner only, and not by owner.
    #
    error = checkFileIsPrivate(awsConfigDict['EC2_SSHKeyPairFile'])
    if error != None:
        raise Exception("SSH private key file " + error)
    
    #
    # The instance config file must exist and be readable.
    #
    # KW: [Test] Verify if config file is missing and not accessible by owner.
    #
    if not os.access(parsedArgs.instance_config, os.R_OK):
        raise Exception("Instance configuration file ({0}) is either missing or unreadable".format(parsedArgs.instance_config))
    
    #
    # Read the key/values from the instance config file into the dictionary we'll return to our caller.
    #
    # KW: [Test] Verify missing properties in configuration file (e.g. no Puppet_PuppetURL).
    #
    instanceConfigDict = {}
    try:
        instanceConfigParser = ConfigParser.RawConfigParser()
        instanceConfigParser.read(parsedArgs.instance_config)
        instanceConfigDict['EC2_ImageID'] = instanceConfigParser.get("EC2", "ImageID")
        instanceConfigDict['EC2_InstanceType'] = instanceConfigParser.get("EC2", "InstanceType")
        instanceConfigDict['Puppet_PuppetURL'] = instanceConfigParser.get("Puppet", "PuppetURL")
        instanceConfigDict['Puppet_PuppetConfigFile'] = instanceConfigParser.get("Puppet", "PuppetConfigFile")
    except (ConfigParser.Error) as mesg:
        raise Exception("Instance configuration file ({0}): {1}".format(parsedArgs.instance_config, mesg))
    
    # check for existence of puppet file (validity can only be checked later)
    # KW: [Test] Verify missing and invalid Puppet file
    #
    if not os.path.isfile(instanceConfigDict['Puppet_PuppetConfigFile']):
        raise Exception("PuppetConfigFile field does not provide a valid file name.")

    # All is good - return configuration to the caller in a tuple.
    return (numServers, djangoProj, awsConfigDict, instanceConfigDict)

