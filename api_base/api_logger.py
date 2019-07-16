from api_base import api_test
from api_base import api_domain
from api_base import api_executor
from api_base import api_stats
from api_base import api_utils
from datetime import datetime
import json
import os

"""
Takes a config file containing information on a test domain and executes and logs the tests in it.
"""

class ApiLogs:

    """
    pass a configuration file which is a json doc 
    with the name of the folder wchich has the test domains
    and a list of test domains from these which has the required 
    tests to be computed.

    {
        "test_domain_dir" : "",
        "test_domains" : [ "", "", ...],
        "test_stats" : "" //stores information on individual tests (how many times tested, how many times failed). This is a persistant file accross multiple
                            tests. Is usfull for maintaining dependencies between tests. 
    }
    """

    def __init__(self, config_loc, debug = False):
        with open(config_loc, 'r') as fp:
            config = json.load(fp)
        self.domain_dir = config['test_domain_dir']
        self.test_domains = config['test_domains']
        self.stats = api_stats.ApiStats(config.get("test_stats", "default_test_stats.json"))
        self.executor = api_executor.ApiTestExecutor()
        self.debug = debug

    def send_error_info(self, response):

        response_type_map = response.aggregate_type()
        if api_utils.Response.INCORRECT_RESPONSE_ERROR in response_type_map or api_utils.Response.STATUS_ERROR in response_type_map:
            response.test.report_error_sns(str(response.response_dict()))

    def update_stats_and_log(self, responses, log_file_pointer):

        for response in responses:
            if response:
                try:
                    log_entry = response.log_entry()
                    if self.debug:
                        print(log_entry)
                    response_type_map = response.aggregate_type()
                    self.stats.increment_success(response.test.domain_name, response.test.test_name, response_type_map.get(api_utils.Response.SUCCESS, 0))
                    failures = response_type_map.get(api_utils.Response.INCORRECT_RESPONSE_ERROR, 0) + response_type_map.get(api_utils.Response.STATUS_ERROR, 0)
                    self.stats.increment_failure(response.test.domain_name, response.test.test_name, failures)
                    log_file_pointer.write(str(datetime.utcnow()) + "," + log_entry + "\n")
                    self.send_error_info(response)
                except Exception as e:
                    print(e)

    def run_domains(self, log_file = "default_log_file.csv"):

        with open(log_file, 'a+') as log_file_pointer:
            for domain_name in self.test_domains:
                if os.path.exists(self.domain_dir + "/" + domain_name + ".json"):
                    with open(self.domain_dir + "/" + domain_name + ".json",'r') as domain_file:
                        domain = api_domain.ApiDomain(domain_name, json.load(domain_file))
                        self.update_stats_and_log(self.executor.execute_domain(domain, self.stats), log_file_pointer)
                    self.stats.update_stats_file()







