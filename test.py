
import unittest
import RichContextAPI


class TestVerifypublications (unittest.TestCase):


    def allow_arg(self):
        return None
    
    def setUp(self):
        """load titles to test APIs"""
        self.dimensions_title = 'Relationships between Diet, Alcohol Preference, and Heart Disease and Type 2 Diabetes among Americans'
        self.ssrn_title = 'Modeling the Term Structure from the On-the-Run Treasury Yield Curve'
        self.oa_title = "Categorizing US State Drinking Practices and Consumption Trends"
        self.epmc_title = "Categorizing US State Drinking Practices and Consumption Trends"
        

    def test_dimensions (self):
        dim_results = RichContextAPI.get_dimensions_md(self.dimensions_title)
        print('dimensions ran')
        
    def test_ssrn (self):
        ssrn_results = RichContextAPI.get_ssrn_md(self.ssrn_title)
        print('For title "{}", ssrn returned results: {}'.format(self.ssrn_title,ssrn_results))
    
    def test_oa (self):
        oa_results = RichContextAPI.oa_lookup_pub_uris(self.oa_title)
        print('openAIRE ran')    

    def test_epmc (self):
        epmc_results = RichContextAPI.get_epmc_md(self.epmc_title)
        print('EuropePMC ran')
    

if __name__ == "__main__":
    unittest.main()
