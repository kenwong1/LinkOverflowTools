#
# Helper functions for interacting with Puppet, running on one or more EC2 instances.
#
import os

from fabric import api

#
# Ensure that the specified list of EC2 instances has Puppet installed.
#
# KW: [Test] Verify valid/correct puppetURL and throw some error if it is incorrect.
#     [Test] Also verify that Puppet files are installed at the expected file location. 
#
def installPuppet(keyFile, puppetURL, ipList):
    '''Install the Puppet application on the specified list of Linux instances, if it's not already installed'''
    
    api.env.user = "centos"
    api.env.hosts = ipList
    api.env.key_filename = keyFile
    results = api.execute(__installpuppettask__, puppetURL)

def __installpuppettask__(puppetURL):
    '''Private fabric task, for installing the puppet package on the remote node.'''
    api.run("sudo rpm -i --force --quiet " + puppetURL)
    api.run("sudo yum -y -q install puppet")


#
# Install and apply a puppet configuration onto a list of remote nodes. The "applyConfig" function
# is the main entry point that you should call, and "__applyConfigTask__" is a private task that's
# called by the Fabric framework (not directly by a caller)
#
# KW: [Process] We should display any exceptions or errors thrown by Puppet after applying the configuration.
#     
def applyConfig(keyFile, configFileName, ipList):
    '''Apply a puppet configuration (configFileName) to the nodes listed in ipList.'''

    # set up the Fabric configuration parameters, then invoke the task for each node.
    api.env.user = "centos"
    api.env.hosts = ipList
    api.env.key_filename = keyFile
    results = api.execute(__applyConfigTask__, configFileName)
    
def __applyConfigTask__(configFileName):
    '''Private fabric task, for installing and applying the puppet configuration on each node.'''
       
    # copy puppet configuration to home directory of centos user.
    baseName = os.path.basename(configFileName)
    result = api.put(configFileName, baseName)
    if len(result.failed) != 0:
        raise Exception("Failed to copy puppet configuration file {0} to remote node.".format(configFileName))
    
    # as root, apply the configuration
    api.run("sudo puppet apply {0}".format(baseName))
