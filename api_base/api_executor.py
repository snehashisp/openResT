from api_base import api_test
from api_base import api_stats
from api_base import api_response
import aiohttp
import asyncio
from api_base.api_utils import Response, ElapsedTimeTracer


"""
Executor module considers the optional parameters provided and executes the tests.
It also maintains a ClientSession object with a elapsed time trace (see utils) 
Execution may not necessarily have a http REST API call. 
The result of an execution is a instance of ApiTestResponse
"""
class ApiTestExecutor:

    def __init__(self):

        self.elapsed_time_tracer = ElapsedTimeTracer()
        #self.session = aiohttp.ClientSession(trace_configs = [self.elapsed_time_tracer.trace_config])

    async def _execute(self, test, test_number, session):

        response = await test.execute_request_async(session, test_number)
        correct_response = test.test_map.get('correct_response', None)
        json_resp = await response.json()
        response_type_msg = Response.get_response_msg(Response.SUCCESS)
        response_type = Response.SUCCESS
        if response.status != 200:
            response_type_msg = Response.get_response_msg(Response.STATUS_ERROR, str(response.status))
            response_type = Response.STATUS_ERROR
        elif correct_response:
            valid, error = test.validate_respone(json_resp)
            if not valid:
                response_type_msg = Response.get_response_msg(Response.INCORRECT_RESPONSE_ERROR, error)
                response_type = Response.INCORRECT_RESPONSE_ERROR
        return (response_type, response_type_msg, json_resp)

    async def _request_executer(self, test):

        number_of_runs = test.test_map.get("options",{}).get("number_of_runs",1)
        async with aiohttp.ClientSession(trace_configs = [self.elapsed_time_tracer.trace_config]) as session:
            result = await asyncio.gather(*[self._execute(test, test_number, session) for test_number in range(number_of_runs)])
        return result

    async def _task_creator(self, test):

        responses = []
        number_of_runs = test.test_map.get("options",{}).get("number_of_runs",1)
        for test_number in range(number_of_runs):
            responses += [await asyncio.create_task(self._execute(test, test_number))]
        return responses

    def _response_creator(self, test, list_of_responses):

        test_response = api_response.ApiTestResponse(test)
        elapsed_times = list(self.elapsed_time_tracer.get_elapsed_info(test.domain_name, test.test_name).items())
        elapsed_times = sorted(elapsed_times, key = lambda x: x[0])
        for i, resp in enumerate(list_of_responses):
            test_response.response_type.append(resp[0])
            test_response.response_type_msg.append(resp[1])
            test_response.response_body.append(resp[2])
            if elapsed_times != []:
                test_response.elapsed_times.append(elapsed_times[i][1])
        return test_response
    

    def _check_true_dependencies(self, dependent_tests, stats):

        """
        True dependencies are those tests that must have succesfully run at least once for this test to run.
        True dependencies are specified under the options key in the following format in the test structure.
        Note that the dependent test must exist and have its domain amongst the given domains in the config file 
        otherwise this function will always return false. 
        "options" : {
            "true_dependency" : [
                {
                    "domain_name":"...",
                    "test_name":"..."
                },
                ...
            ]
        }
        """
        for test in dependent_tests:
            if int(stats.get_test_success_count(test['domain_name'], test['test_name'])) == 0:
                return False
        return True

    def _check_false_dependencies(self, dependent_tests, stats):

        """
        Similar to true dependencies false dependencies are satisfied if all of the tests listed have failed at least once. 
        Note that only failures are considered. Tests that have not yet run are not designated as failures.
        """
        for test in dependent_tests:
            if int(stats.get_test_failure_count(test['domain_name'], test['test_name'])) == 0:
                return False
        return True

    async def _execute_test(self, test, stats):

        options = test.test_map.get('options',{})
        if options.get('repeat', True) is False:
            if stats.get_test_success_count(test.domain_name, test.test_name) > 0:
                return self._response_creator(test, [(Response.NO_REPEAT, Response.get_response_msg(Response.NO_REPEAT), None)])

        true_dependencies = options.get('true_dependency', None)
        if true_dependencies and not self._check_true_dependencies(true_dependencies, stats):
            return self._response_creator(test, [(Response.TRUE_DEPENDENCY_UNSATISFIED, Response.get_response_msg(Response.TRUE_DEPENDENCY_UNSATISFIED), None)])

        false_dependencies = options.get('false_dependencies', None)
        if false_dependencies and not self._check_false_dependencies(false_dependencies, stats):
            return self._response_creator(test, [(Response.FALSE_DEPENDENCY_UNSATISFIED, Response.get_response_msg(Response.FALSE_DEPENDENCY_UNSATISFIED), None)])

        responses = await self._request_executer(test)
        return self._response_creator(test, responses)

    async def _domain_executor(self, domain, stats):
        tests = list(domain.generate_tests())
        return await asyncio.gather(*[self._execute_test(test, stats) for test in tests])

    def execute_domain(self, domain, stats):

        try:
            responses = list()
            if domain.options.get("async", False) == True:
                responses = asyncio.run(self._domain_executor(domain, stats))
            else:
                for test in domain.generate_tests():
                    responses.append(asyncio.run(self._execute_test(test, stats)))
            return responses
        except Exception as e:
            raise e

            




