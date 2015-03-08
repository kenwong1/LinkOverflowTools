import unittest, aws, test_utils, ConfigParser

class ConfigSetup(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        # This will setup valid AWS connection variables that we will use for all the tests
        #
        # Read the values from .aws.settings file
        #
        awsConfigDict = {}
        try:
            awsConfigParser = ConfigParser.RawConfigParser()
            awsConfigParser.read(test_utils.getAWSSettings())
            awsConfigDict['EC2_AccessKeyID'] = awsConfigParser.get("EC2", "AccessKeyID")
            awsConfigDict['EC2_SecretAccessKey'] = awsConfigParser.get("EC2", "SecretAccessKey")
            awsConfigDict['EC2_AvailabilityZone'] = awsConfigParser.get("EC2", "AvailabilityZone")
            awsConfigDict['EC2_SSHKeyPair'] = awsConfigParser.get("EC2", "SSHKeyPair")

        except (ConfigParser.Error) as mesg:
            raise Exception("AWS settings file ({0}): {1}".format(test_utils.getAWSSettings(), mesg))

        # Read the values from instance.config file
        #
        instanceConfigDict = {}
        try:
            instanceConfigParser = ConfigParser.RawConfigParser()
            instanceConfigParser.read(test_utils.getInstanceConfig())
            instanceConfigDict['EC2_ImageID'] = instanceConfigParser.get("EC2", "ImageID")
            instanceConfigDict['EC2_InstanceType'] = instanceConfigParser.get("EC2", "InstanceType")

        except (ConfigParser.Error) as mesg:
            raise Exception("AWS settings file ({0}): {1}".format(test_utils.getInstanceConfig(), mesg))


        accessKeyId = awsConfigDict['EC2_AccessKeyID']
        secretAccessKey = awsConfigDict['EC2_SecretAccessKey']
        availabilityZone = awsConfigDict['EC2_AvailabilityZone']
        amiImage = instanceConfigDict['EC2_ImageID']
        instanceType = instanceConfigDict['EC2_InstanceType']
        keyPairName = awsConfigDict['EC2_SSHKeyPair']
        cls.accessKeyId = accessKeyId
        cls.secretAccessKey = secretAccessKey
        cls.availabilityZone = availabilityZone
        cls.amiImage = amiImage
        cls.instanceType = instanceType
        cls.keyPairName = keyPairName


class ValidateAWS(ConfigSetup):
    
    def test_invalid_launchEC2Instances(self):

        # Test launching EC2 instances with invalid access key
        #
        with self.assertRaisesRegexp(Exception, "Unable to connect to EC2*"):
            ipList = aws.launchEC2Instances('accessKeyId', 'secretAccessKey', 1, 'availabilityZone', 'amiImage', 'instanceType', 'keyPairName')
        
    def test_keyPair_none(self):

        # Test passing an invalid keyPairName
        #
        with self.assertRaisesRegexp(Exception, ".*is not defined. Use the AWS console to create it."):
            ipList = aws.launchEC2Instances(self.accessKeyId, self.secretAccessKey, 1, self.availabilityZone, self.amiImage, self.instanceType, 'keyPairName')        

    def test_invalid_reservation(self):

        # Test passing an invalid instanceType
        #
        with self.assertRaisesRegexp(Exception, "Unable to launch EC2 instances*"):
            ipList = aws.launchEC2Instances(self.accessKeyId, self.secretAccessKey, 1, self.availabilityZone, self.amiImage, 'instanceType', self.keyPairName)        

    def test_valid_scenario(self):        

        # Test launching EC2 instance with valid arguments
        #
        ipList = aws.launchEC2Instances(self.accessKeyId, self.secretAccessKey, 2, self.availabilityZone, self.amiImage, self.instanceType, self.keyPairName)        
        self.assertIsNotNone(ipList)
        
if __name__ == '__main__':
    unittest.main()
                        
