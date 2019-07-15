from api_base import api_test
import copy
import numpy as np
import math

from api_base.api_utils import Response

class ApiTestResponse:

    """
    All are test may be run more than once using options
    response_type : type of reponse, see api_utils Response Class 
    response_type_message : user generated message corresponding to the response_type, 
    response_body : body of each individual response
    elapsed_time : time it took for each individual request
    """
    def __init__(self, test, response_type = [], response_type_msg = [], response_body = [], elapsed_times = []):
        self.test = test
        self.response_type = copy.deepcopy(response_type)
        self.response_type_msg = copy.deepcopy(response_type_msg)
        self.response_body = copy.deepcopy(response_body)
        self.elapsed_times = copy.deepcopy(elapsed_times)
        self.type_map = None

    def aggregate_type(self):
        if not self.type_map:
            self.type_map = {}
            for resp in self.response_type:
                self.type_map.setdefault(resp, 0)
                self.type_map[resp] += 1
        return self.type_map

    def get_errors(self):
        errors = set()
        for resp_index, resp in enumerate(self.response_type):
            if resp == Response.STATUS_ERROR:
                errors.add("(" + self.response_type_msg[resp_index] + ")")
            elif resp == Response.INCORRECT_RESPONSE_ERROR:
                errors.add("(" + self.response_type_msg[resp_index] + ". Response Body:" + str(self.response_body[resp_index]) + ")")
        return errors

    def get_elapsed_time_stats(self):
        
        times = np.array(self.elapsed_times)
        times.sort()
        return {
            "avg" : times.mean(), 
            "std" : times.std(), 
            "avg_high" : times[-1 * int(math.ceil(0.1 * len(times))):].mean()
        }

    def _get_single_response_log(self):

        log_dict = copy.deepcopy(api_test.TestType.log_entry_template)
        log_dict["domain_name"] = self.test.domain_name
        log_dict["test_name"] = self.test.test_name
        log_dict["response_status"] = self.response_type_msg[0]
        if self.response_type[0] == Response.INCORRECT_RESPONSE_ERROR:
            log_dict["response_body"] = self.response_body[0]
        log_dict["response_times"] = self.elapsed_times[0]
        return log_dict

    def _get_multi_response_log(self):

        log_dict = copy.deepcopy(api_test.TestType.log_entry_template)
        log_dict["domain_name"] = self.test.domain_name
        log_dict["test_name"] = self.test.test_name
        log_dict["test_type"] = api_test.TestType.MULTI_TEST
        response_type_aggr = self.aggregate_type()
        type_list = list(map(lambda x: str(Response.get_response_msg(x[0])) + ":" + str(x[1]), response_type_aggr.items()))
        log_dict["response_status"] = " ".join(type_list).translate({44:":",39:""})
        errors = self.get_errors()
        if errors != []:
            log_dict["response_body"] = str(errors).translate({44:""})
        times = self.get_elapsed_time_stats()
        log_dict["response_times"] = "average_time: {avg}. standard_deviation: {std}. average_high: {avg_high}.".format(**times)
        return log_dict

    def log_entry(self):

        if self.test.test_type == api_test.TestType.SINGLE_TEST:
            return ",".join(list(map(lambda x: str(x), self._get_single_response_log().values())))
        else:
            return ",".join(list(map(lambda x: str(x), self._get_multi_response_log().values())))

