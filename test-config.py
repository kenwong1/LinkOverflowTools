import unittest, config

class ConfigSetup(unittest.TestCase):
    ''' This will sets up the command line parser from config.py '''
    @classmethod
    def setUpClass(cls):
        parser = config.create_parser()
        cls.parser = parser

class ValidateConfig(ConfigSetup):

    def test_with_empty_args(self):
        ''' Tests passing in no argument '''
        with self.assertRaises(SystemExit):
            self.parser.parse_args([])
            
    def test_all_arguments(self):        
        ''' Tests passing in all arguments to create_parser and verifying each one is set correctly'''
        aws_settings = 'test_aws_settings'
        confile_file = 'test_config_file'
        django_project_file = 'test_django_file'
        num_servers = '1'
        argList = ['--aws-settings', aws_settings, '--instance-config', confile_file, django_project_file, num_servers]
        
        parsedArgs = self.parser.parse_args(args=argList)
        self.assertEqual(parsedArgs.aws_settings, aws_settings)
        self.assertEqual(parsedArgs.instance_config, confile_file)
        self.assertEqual(parsedArgs.django_proj, django_project_file)
        self.assertEqual(parsedArgs.num_servers, int(num_servers))
    
    def test_checkFileIsPrivate_no_file(self):
        ''' Test passing in an invalid file name for test_checkFileIsPrivate_no_file '''
        self.assertRegexpMatches(config.checkFileIsPrivate('filename'), '.*is missing.')
        
if __name__ == '__main__':
    unittest.main()
            