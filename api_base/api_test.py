import requests
import boto3
import json
import jsonschema
import numpy as np
import math
import copy
from api_base.api_utils import Response

"""
Tests are present as JSON files called domains. 
The api domain of each test is by default the name of the file in which it is present. 

Each tests in json files have the format as ...
{
    "testname": { // the name of the test
        "url": ""  // string representing url of the request5
        
        "method": "" // GET or POST

        (optional) "headers": {} // headers as json dict, dont include if not present
        
        "activated": true or false // this test activated to be run periodically (if the tests are scheduled to executed periodically)
        
        (optional)"data": {} //data of the API request in json format (test map)

        (optional) "correct_response": { $schema } // a json schema on which the response will be validated

        (optional)"sns": {
            "region_code": "",
            "arn": "" 
            // the AWS SNS arn of the notification group to which an error notification (if generated) will be sent
        }
        
        (optional) "options": {
            //optional parameters that define the test execution. 
            "repeat":"True", //whether the test can be executed more than once
            "true_dependency":[] //list of true dependencies, see executor module for more info
            "false_dependency": [] //list of false dependencies, see executor module for more info
            "number_of_runs": x //the number of times this test will be executed, the tests are asynchronous

        }

    }
    ...
}

"""

class TestType:

    SINGLE_TEST = "SINGLE_TEST"
    MULTI_TEST = "MULTI_TEST"

    log_entry_template = {
        "domain_name" : "",
        "test_name" : "",
        "test_type" : SINGLE_TEST,
        "response_status" : "",
        "response_body" : "",
        "response_times" : None
    }



class ApiTest:

    def __init__(self, domain_name, test_name, test_map):
        self.domain_name = domain_name
        self.test_name = test_name
        self.test_map = test_map
        self.test_type = TestType.SINGLE_TEST
        if test_map.get("options",{}).get("number_of_runs",1) > 1:
            self.test_type = TestType.MULTI_TEST

    def execute_request(self):
        headers = self.test_map.get('headers', None)
        return requests.request(self.test_map['method'], self.test_map['url'], headers = headers, json = self.test_map['data'])

    async def execute_request_async(self, session, test_number = 0):
        context = {
            "domain":  self.domain_name, 
            "name": self.test_name, 
            "number": test_number
        }
        headers = self.test_map.get('headers', None)
        data = self.test_map.get('data', None)
        return await session.request(self.test_map['method'], self.test_map['url'], headers = headers, json = data,
                                     trace_request_ctx = context)

    def validate_respone(self, response):
        try:
            jsonschema.validate(response, self.test_map['correct_response'])
            return True, None
        except jsonschema.ValidationError as e:
            return False, "Validation Error : Schema Path: " + " -> ".join(e.absolute_schema_path) + " Error: " + e.message 
        except jsonschema.SchemaError as e:
            return False, "Schema Error : Schema Path: " + " -> ".join(e.absolute_schema_path) + " Error: " + e.message 

    def report_error_sns(self, error_msg):
        if self.test_map.get('sns', {}).get('region_code', None) and self.test_map.get('sns', {}).get('arn', None):
            client = boto3.client('sns', region_name = self.test_map['sns']['region_code'])
            client.publish(TopicArn = self.test_map['sns']['arn'], Message = error_msg)







