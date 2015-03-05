This repository contains tools to support deployment of the LinkOverflow project.


Overview
--------

The approach I've taken to implement the "launch.py" script is as follows:

  - Use Python's argparser library to parse command line arguments.
  - Use Python's ConfigParser library to parse two separate configuration files:
     ~/.aws.settings - secret keys and other parameters that are private to each user.
         (not to be version controlled - ever)
     instance.config - configuration parameters that are specific to the product
         (and should be kept under version control)
  - Once the command line arguments and configuration parameters are validated, the
    AWS "boto" library is used to create EC2 instances, then wait until they're fully
    up and running. This is when we obtain the external IP address for each, and the
    associated SSH key pair.
  - Next, the Python Fabric library is used to connect to each instance. Upon connecting,
    we ensure that the Puppet tool is installed (using yum).
  - Once Puppet is installed, we copy over and apply a Puppet configuration file, to
    bring all other packages (e.g. Python, Django) up to their desired levels.
  - Finally, we copy over the necessary Django project files to each instance and start
    the default web server running (using the default SQLite database)
  
Environment
-----------

I developed this software using the following environment. Hopefully you'll have no
trouble checking out the code and running it on your own Linux systems.

  - OpenSuSE 12.2 (a personal VM I have at home), as well as RHEL 7.x (from AWS)
  - Python 2.7
  - boto - as downloaded via the link on the AWS web site (http://boto.readthedocs.org/en/latest/)
  - python-Fabric version 1.4.2 (part of the SuSE/RHEL distribution)
  - Various other standard Python libraries, which you should already have.
  
You will also need to manage your own SSH Key Pair via the AWS console. I assume you know the
name of the existing Key Pair, and also have saved-away the private key in a safe place.
    
.aws-settings file
------------------

Since the launch.py utility relies on user-specific values, such as AWS and SSH keys, as well as prefered
availability zones, these values are extracted into a per-user .aws.settings file. This file is
not (and should not) be versioned controlled, since it contains secret information. Note that this
file is different from the "instance.config" file which should be version-controlled.

The following is a template .aws.settings file for you to start with:

    #
    # This configuration file is used by the launch.py utility. These settings
    # are either per-user (and can't be shared), or are secret and should not be
    # checked-into source control.
    #

    [EC2]
    # The AccessKeyId and SecretAccessKey are used to connect to
    # the AWS EC2 service. They can be obtained from the EC2
    # web interface.
    AccessKeyId = <insert your own key ID - from AWS console>
    SecretAccessKey = <insert your own secret access key - from AWS console>

    # Which availability zone we should create the instances in
    # This is configurable depending on user preferences.
    AvailabilityZone = us-west-2

    # The name of the SSH Key Pair to use when creating the EC2 instances
    SSHKeyPair = LinkOverflow-keys

    # The local file containing the SSH key pair
    SSHKeyPairFile = /home/<user>/LinkOverflow-keys.pem


Future Additions
----------------

Although this was a fun exercise, I was not able to do everything I would have liked to have done. Here
are some future improvements I'd like to make:

- Although the creation of AWS instances runs in parallel, the invocation of Fabric/Puppet is currently done
  one host at a time. This should be changed so that all hosts are configured in parallel, making the start-up
  process much faster.
  
- In fact, rather than using Fabric/Puppet at boot-up time, I'd prefer to create a new AMI based off the
  original Centos image. This would still involve using Puppet to custom-create a suitable AMI, but this would
  happen offline. At a later time (when the VMs are created) this new AMI would be used to create fully-prepared
  instances, without the need to install additional software at boot-time.

- I don't handle the case where less than N instances start up. Right now, any failure in launching N instances
  causes the whole script to abort (rather than continuing with fewer instances)

- When EC2 instances are destroyed (via the AWS Console), the underlying volumes must be manually destroyed
  as well. The necessary "destroy volume on instance destruction" flag needs to be set within EC2.

- Rather than creating N instances on EC2 with each of them having an external IP address, we should create
  a load balancer (with an external IP) that can redirect traffic to each of the internal (private) instances.

- I'm sure there's a lot more to do to have a perfectly-stable Django application running...

- Of course, there's always monitoring and performance tuning to be done (well into the future)


Test Cases
----------

If I had more time, I'd prefer to automate testing of this tool, but for now I've relied on manual testing.
Here are the test cases I've followed:

- Execute launch.py with no arguments - ensure that meaningful error message is shown.
- Execute launch.py with too many arguments - ensure that meaningful error message is shown.
- Execute launch.py -h, and validate help information.
- Execute "launch.py myproj 0" and "launch.py myproj 6" - should receive an error about having an invalid number of instances.
- Execute "launch.py invalid 1" - should receive an error about "invalid not being a Django project".
- Rename the .aws.settings file as ".aws.hide", and run "launch.py myproj 1" - should receive an error message.
- Use the "--aws-settings .aws.hide" - the file should now be located correctly.
- Rename the file back to .aws.settings, but set permissions to 000. Launch should report a message about unreadable file.
- Set permissions to 644, and launch should report that the file is readable by other users (an error)
- In the .aws-settings file:
-   Remove the [EC2] tag (error)
-   Change [EC2] to [EC3] (error)
-   Change AccessKeyId to AccessId (error)
-   Change the access key value slightly to create an invalid key (error from EC2)
-   Change the SSHKeyPairFile to an invalid location (error)
-   Set permissions on your SSH key pair file to 644 (error)
-   Set permissions back to 400 (should be successful)
-   Set an invalid AWS Key Pair name.
- For the instance.config file:
-   Remove the EC2 tag (error)
-   Change the [EC2] tag to [Foo] (error)
-   Change the ImageID tag to ImogeId (error)
-   Change the ImageID value (ami-c7d092f7) to ami-c7d092f7xxx (error)
-   Change the InstanceType to t100.enormous (error)
-   Change PuppetURL to an invalid URL (http://bleh.com) - will report error once it reaches puppet install phase.
-   Change PuppetConfigFile to an invalid path (/invalid) - will report error immediately
- Launch 1 instance, once complete
-   Use the AWS console to validate the VM size and external IP addresses (compare with output from script)
-   Manually ssh using the IP address and key pair
-   Validate that it's Centos.
-   Validate that the correct versions of Python and Django are installed.
-   Validate that browsing to IP:8080 provides a basic Django landing page.
- Launch 5 instances, and repeat tests from previous step.



