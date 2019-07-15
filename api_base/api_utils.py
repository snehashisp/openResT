import aiohttp
import asyncio
from datetime import datetime, timedelta

class Response:

    # Success Response
    SUCCESS = 0
    # Status Error (http errors like 400)
    STATUS_ERROR = 1
    # Response does not match the given correct json schema provided
    INCORRECT_RESPONSE_ERROR = 2
    # Test is set not to repeat i.e. is executed only once (only successful executions)
    NO_REPEAT = 3
    # Dependencies to other tests 
    TRUE_DEPENDENCY_UNSATISFIED = 4
    FALSE_DEPENDENCY_UNSATISFIED = 5

    # messages corresponding to different responses
    _messages = {
        SUCCESS : "Succesful execution",
        STATUS_ERROR : "Status Error ",
        INCORRECT_RESPONSE_ERROR : "Incorrect Response ",
        NO_REPEAT : "Already Successfully Executed (Repeat is off) ",
        TRUE_DEPENDENCY_UNSATISFIED : "True dependencies unsatisfied ",
        FALSE_DEPENDENCY_UNSATISFIED : "False dependencies unsatisfied "
    }

    @staticmethod
    def get_response_msg(response_type, additional_info = ""):
        return Response._messages[response_type] + additional_info


"""
aiohttp session have a tracing ability where certain events can have an associated 
functions which gets executed when those events occur. These events can be used to calculate 
the time taken for a request using the on_request_start and on_response_chunk_received events.
This module stores the time taken for any test to return results in a dictionary structure
{
    "domain": {
        "name": {
            nummber:time_taken
        }
    }
}

Only those sessions that use the trace_config of the corresponding ElapsedTimeTracer are logged in the
map of that tracer. The context provided at the time of 
"""
class ElapsedTimeTracer:

    async def _on_request_start(self, session, context, param):
        context = context.trace_request_ctx
        self.elapsed_time_map.setdefault(context['domain'], {}).setdefault(context['name'], {})[context['number']] = datetime.now()

    async def _on_response_chunk_received(self, session, context, param):
        context = context.trace_request_ctx
        start_time = self.elapsed_time_map[context['domain']][context['name']][context['number']] 
        self.elapsed_time_map[context['domain']][context['name']][context['number']] = (datetime.now() - start_time).total_seconds()

    def __init__(self):
        self.elapsed_time_map = {}
        self.trace_config = aiohttp.TraceConfig()
        self.trace_config.on_request_start.append(self._on_request_start)
        self.trace_config.on_response_chunk_received.append(self._on_response_chunk_received)

    def get_elapsed_info(self, domain_name, test_name):
        return self.elapsed_time_map.get(domain_name, {}).get(test_name, {})


