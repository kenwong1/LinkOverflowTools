#
# Helper functions for interacting with Django, running on one or more EC2 instances.
#
import os

from fabric import api

#
# Copy a full django project over to a set of EC2 instances. On error, this
# whole function will abort. TODO: fix this to instead throw an exception
# to the caller.
#
def deployProject(keyFile, djangoProjPath, ipList):
    '''Copy a full Django project over to a set of EC2 instances.'''
    
    api.env.user = "centos"
    api.env.hosts = ipList
    api.env.key_filename = keyFile
    results = api.execute(__deployprojecttask__, djangoProjPath)

def __deployprojecttask__(djangoProjPath):
    '''Private fabric task, for installing a Django project on a node'''

    #
    # Copy all the files (with their correct access mode) from our local
    # working directory into the remote instance's local directory. This
    # will automatically overwrite any existing files.
    # TODO: this operation will not remove "deleted" files from the target
    # instance. This will need to be fixed to avoid stale files sitting around.
    api.put(djangoProjPath, '', mirror_local_mode=True)

#
# Given a list of IP addresses and the path to a Django project, start up the
# Django project's internal web server. On error, this whole function will
# abort. TODO: fix this to instead throw an exception to the caller.
#
def runProject(keyFile, djangoProjectPath, ipList):
    '''Start a Django web project running on a set of EC2 instances.'''
    
    api.env.user = "centos"
    api.env.hosts = ipList
    api.env.key_filename = keyFile
    results = api.execute(__runprojecttask__, djangoProjectPath)
    
def __runprojecttask__(djangoProjPath):
    '''Private fabric task, for running a Django project web server on a node'''
    
    #
    # Create (migrate) the underlying database (in our case, SQLite), then start the default
    # web server running. Note that we need to disconnect stdin/stdout/stderr so that Fabric
    # can run the server in the background. TODO: fix this so we can capture log/error output
    # in a file.
    #
    remoteDir = os.path.basename(djangoProjPath)
    api.run("cd " + remoteDir + " && python manage.py migrate")
    api.run("cd " + remoteDir + " && (nohup python manage.py runserver 0.0.0.0:8080 >& /dev/null </dev/null &)", pty=False)
    
    # TODO: there is surely more to do here, but I'm running out of spare time :-(
    

