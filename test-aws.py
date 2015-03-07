import unittest, aws

class ConfigSetup(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        ''' This will setup valid AWS connection variables that we will use for all the tests '''

        accessKeyId = 'AKIAJVKMGB365LWDH36A'
        secretAccessKey = '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'
        availabilityZone = 'us-west-2'
        amiImage = 'ami-c7d092f7'
        instanceType = 't2.micro'
        keyPairName = 'testkey'
        cls.accessKeyId = accessKeyId
        cls.secretAccessKey = secretAccessKey
        cls.availabilityZone = availabilityZone
        cls.amiImage = amiImage
        cls.instanceType = instanceType
        cls.keyPairName = keyPairName


class ValidateAWS(ConfigSetup):
    
    def test_invalid_launchEC2Instances(self):
        ''' Test launching EC2 instances with invalid access key '''
        with self.assertRaises(Exception):
            ipList = aws.launchEC2Instances('accessKeyId', 'secretAccessKey', 1, 'availabilityZone', 'amiImage', 'instanceType', 'keyPairName')
        
    def test_keyPair_none(self):
        ''' Test passing an invalid keyPairName '''
        with self.assertRaises(Exception):
            ipList = aws.launchEC2Instances(self.accessKeyId, self.secretAccessKey, 1, self.availabilityZone, self.amiImage, self.instanceType, 'keyPairName')        

    def test_invalid_reservation(self):
        ''' Test passing an invalid instanceType '''
        with self.assertRaises(Exception):
            ipList = aws.launchEC2Instances(self.accessKeyId, self.secretAccessKey, 1, self.availabilityZone, self.amiImage, 'instanceType', self.keyPairName)        

    def test_valid_scenario(self):        
        ''' Test launching EC2 instance with valid arguments '''
        ipList = aws.launchEC2Instances(self.accessKeyId, self.secretAccessKey, 1, self.availabilityZone, self.amiImage, self.instanceType, self.keyPairName)        
        self.assertIsNotNone(ipList)
        
if __name__ == '__main__':
    unittest.main()
                        