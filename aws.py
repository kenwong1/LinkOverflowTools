#
# Helper functions for issuing requests to EC2
#
import sys, boto.ec2, time

#
# Launch a specified number of EC2 instances, with the provided parameters.
#
def launchEC2Instances(accessKeyId, secretAccessKey, numServers, availabilityZone, amiImage, instanceType, keyPairName):

    #
    # Create a connection to EC2. This can fail for several different reasons. Make sure we provide a helpful
    # error message if possible.
    #
    # KW: We should remove the "probably due to..." section of the error messages since there could be other reasons for failure.
    try:
        ec2 = boto.ec2.connect_to_region(availabilityZone, aws_access_key_id=accessKeyId, aws_secret_access_key=secretAccessKey)
    except boto.exception.EC2ResponseError as mesg:
        raise Exception("Unable to connect to EC2, probably due to incorrect access key.\nDetailed message from server was {0}".format(mesg))

    if ec2 is None:
        raise Exception("Unable to connect to EC2, probably due to incorrect availability zone: {0}".format(availabilityZone))

    #
    # Validate that the requested KeyPair is defined.
    #
    keyPair = ec2.get_key_pair(keyPairName)
    if keyPair is None:
        raise Exception("AWS KeyPair {0} is not defined. Use the AWS console to create it.".format(keyPairName))

    #
    # Ask EC2 to launch instances. There are numerous possible failures here, so the best we can do
    # is display the raw error message from EC2.
    #
    try:
        reservation = ec2.run_instances(amiImage, min_count=numServers, max_count=numServers,
                                        instance_type=instanceType, key_name=keyPairName)
    except boto.exception.EC2ResponseError as mesg:
        raise Exception("Unable to launch EC2 instances.\nDetailed message from server was {0}".format(mesg))

    #
    # For each instance, determine the external IP address. IP addresses will typically be assigned to the instance
    # within 10 seconds, but we wait until the VM has fully passed status checks, which might take many minutes.
    # The end user shouldn't be permitted to connect to it with SSH until it's fully running, so this is where we need to wait.
    # Note that even though this algorithm looks to be serialized, there's a good chance that the second (third, etc) instances
    # will be ready immediately after the first instance is ready, since they're booting up in parallel. However, if one of
    # the instances doesn't start up, this algorithm will fail (TODO: fix this)
    #
    # KW: We can refactor the while loop by checking for instance_status.status != "ok" instead of True.
    #     Once instance_status equals "ok", the loop will break.
    #
    #   for instance in reservation.instances:
    #       statusSet = "initializing"
    #       while statusSet != "ok":
    #           time.sleep(5)
    #           newStatus = ec2.get_all_instance_status(instance_ids=[instance.id])
    #           if len(newStatus) != 0:
    #               statusSet = newStatus[0].instance_status.status
    #       instance.update()
    #       ipList.append(instance.ip_address)
    #
    ipList = []
    for instance in reservation.instances:
        while True:
            statusSet = ec2.get_all_instance_status(instance_ids=[instance.id])
            if len(statusSet) != 0:
                if statusSet[0].instance_status.status == "ok":
                    break;
                # TODO: need a timeout mechanism here, in case of failure.
            time.sleep(5)
        instance.update()
        ipList.append(instance.ip_address)
    
    #
    # On success, we know that all instances are alive. Return the list of IP addresses.
    #
    return ipList
