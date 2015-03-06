#!/usr/bin/env python2.7
#
# "launch.py" is a tool for deploying applications onto the AWS cloud.
#
import sys

# local modules
import config, aws, puppet, djangoutils

#
# Start by fetching/validating the command-line arguments, and ensuring that the configuration files
# are present and contain the necessary settings (AWS keys, etc). If we receive an Exception,
# we don't have a valid configuration and we'll simply abort the launch.
#
# KW: Test with valid and invalid arguments. Invalid argument types can be found in config.py
#
try:
    (numServers, djangoProj, awsConfigDict, instanceConfigDict) = config.validateConfig()
except Exception as mesg:
    print >>sys.stderr, "Error:", mesg
    sys.exit(1)

#
# At this point, we know our configuration is good. 
#
print "\nCreating", numServers, "EC2 instances"
print "- In AWS Availability Zone:", awsConfigDict['EC2_AvailabilityZone']
print "- Using EC2 Instance Image:", instanceConfigDict['EC2_ImageID']
print "- And EC2 Instance Type:", instanceConfigDict['EC2_InstanceType']
print "- Loading Django project from:", djangoProj

#
# Now, launch the VMs on EC2. This will return a list of the external IP addresses
# of the new instances, or an exception if there's a problem.
#
print "\nPlease wait for EC2 instances to start up... (may take several minutes)\n"

try:
    ipList = aws.launchEC2Instances(awsConfigDict['EC2_AccessKeyID'],
                       awsConfigDict['EC2_SecretAccessKey'],
                       numServers,
                       awsConfigDict['EC2_AvailabilityZone'],
                       instanceConfigDict['EC2_ImageID'],
                       instanceConfigDict['EC2_InstanceType'],
                       awsConfigDict['EC2_SSHKeyPair'])

# handle error case
except Exception as mesg:
    print >>sys.stderr, "Error:", mesg
    sys.exit(1)

#
# We've installed the base OS image on these instances, but have not installed custom packages.
# We use Puppet for this purpose. First we must install the puppet tool itself, and then copy
# over the puppet configuration file. Finally, we run the puppet tool to apply the changes.
# TODO: this is *serialized* and needs to be made parallel.
#
# KW: We should output the username and hostname after Fabric has connected to the remote systems to help debug in case there are problems.
#
try:
    puppet.installPuppet(awsConfigDict['EC2_SSHKeyPairFile'], instanceConfigDict['Puppet_PuppetURL'], ipList)
    puppet.applyConfig(awsConfigDict['EC2_SSHKeyPairFile'], instanceConfigDict['Puppet_PuppetConfigFile'], ipList)
except Exception as mesg:
    print >>sys.stderr, "Error: ", mesg    
    sys.exit(1)
    
#
# Now, deploy the Django project to each node, and start the server running.
#
djangoutils.deployProject(awsConfigDict['EC2_SSHKeyPairFile'], djangoProj, ipList)
djangoutils.runProject(awsConfigDict['EC2_SSHKeyPairFile'], djangoProj, ipList)

#
# we got a list of IP addresses, display them for the user and tell them how to SSH
#
print "\nIP Addresses of newly created instances:"
for ip in ipList:
    print " ", ip
print "\nTo connect to these servers, use:\n  ssh -i {0} centos@<ip-address>".format(awsConfigDict['EC2_SSHKeyPairFile'])
print "Or point your web browser to http://<ip-address>:8080\n"


