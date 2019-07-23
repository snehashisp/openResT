## openResT
version 0.1

<br/><br/>
A Framework for REST based api testing with JSON schema based validation. 
Core functionalities (Implemented in current version)
<ul>
    <li> Creating tests in JSON </li>
    <li> Organising tests into domains </li>
    <li> Running domains and the tests within the domains 
        <ul>
            <li> Running tests once synchronously. </li>
            <li> Running tests multiple times (for stress testing API) asynchronously. </li>
            <li> Running all tests in a domain asynchronously all at once. </li>
        </ul>
    </li>
    <li> Checking for status errors. </li>
    <li> Validating using JSON schema. </li>
    <li> Calculating response times. </li>
    <li> Error logging in csv. </li>
    <li> AWS SNS based error notifications. </li>
</ul>
<br/>
Considerations: At current implementation levels openResT is a framework providing the foundation for
the above functionalities and not a full fledged application or a library. The following sections will 
outline the structure and philosophy of the framework. Users can (should) extend the functionalities of 
the module to meet their demands. 

### Domains

Tests are organised into domain files, each with multiple tests. Domains are organised as json files.
The name of the domain is the same as the filename. The format for the domain and the tests within it are.

API domain are a set of logically similar API tests. They may not all be calls to the 
same web domain. API domains house the tests (structure in api_test file) that will be executed.

```json
{
    "defaults": {
        "..."
    },
    "options": {
        "async":false 
    },
    "test1": { "..." },
    "test2": { "..." },
    "..."
}
```
It has a "defaults" metadata which contains default parameters that will be applied to all the 
tests in the domain if they do not have the corresponding attribute. These default parameters can be overridden by
the same test specific parameter if they are present. For example, to set the the url of every test in the domain to
the same location set the url parameter as 

```json
"defaults": {
    "url":"..."
}
```
and this parameter will be added to every test in the domain which do not have a url parameter. If any test has a 
url parameter that parameter will override the default url parameter. 

The addition and overriding of default parameters work recursively to add defaults to any nested json objects. example
To set the payload of WEB notifications under the data (REST api message body) set the defaults as 

```json
"defaults": {
    "data": {
        "payload": {
            "WEB" : "xyz"
        }
    }
}
```
If there exists a test with data as
```json
"data": {
    "payload": {
        "redirect":"abc.com"
    },
    "retry": true
}
```
then the merged test will have the data attribute as 
```json
"data" : {
    "payload": {
        "WEB": "xyz",
        "redirect":, "abc.com"
    },
    "retry": true
}
```

Set the async parameter in option to true to run all tests in the domain asynchronously all at once.
```json
"options":{
    "async":true
}
```

### Tests

Each tests in json files have the format as ...
```json
{
    "testname": {
        "url":"",
        "headers": {},
        "data": {},
        "activated":true,
        "correct_response": {"$schema"},
        "sns": {
            "region_code":"",
            "arn":""
        },
        "options": {
            "repeat":true,
            "true_dependency":[],
            "false_dependency":[],
            "number_of_runs":[]
        }
    }
}
```
<ul>
<li> method: GET or POST </li>
<li> headers: headers as json dict, dont include if not present (optional) </li>
<li> activated: wheather this test will be executed this </li>
<li> data: data of the API request in json format (optional for GET requests) </li>
<li> correct_response: a json schema on which the response will be validated (optional) </li>
<li> sns: he AWS SNS arn of the notification group to which an error notification (if generated) will be sent (optional) </li>
<li> options: optional parameters that define the test execution. 
    <ul>
    <li> repeat:true/false, whether the test can be executed more than once </li>
    <li> true_dependency: list of true dependencies. True dependencies are those tests that must have successfully run at least once for this test to run. True dependencies are specified under the options key in the following format in the test structure. Note that the dependent test must exist and have its domain amongst the given domains in the config file otherwise this function will always return false. </li>
    <li> false_dependency: list of false dependencies. Similar to true dependencies false dependencies are satisfied if all of the tests listed have failed at least once. Note that only failures are considered. Tests that have not yet run are not designated as failures.</li>
    <li>number_of_runs: the number of times this test will be executed, the tests are asynchronous</li>
</li>
</ul>

True Dependency format, (similar for false dependencies)
```json
"options" : {
    "true_dependency" : [
        {
            "domain_name":"...",
            "test_name":"..."
        },
        ...
    ]
}
```
### Execution

Execution of tests is done per domain either one after another synchronously or all together asynchronously. 
The executor functions are in api_executor class. Execution uses a <i>stats</i> file for keeping track of what tests
have been executed and when. This file is used for maintaining dependencies and checking repeats i.e. if The stats should be created once 
and maintained across further executions. They are given as set of initial configuration parameters when the tests are initiated to 
run. If the stats file is removed or deleted then it is as if all tests were running for the first time.

### Responses

The responses possible for a test are

* SUCCESS : Success Response
* STATUS_ERROR : Status Error (http errors like 400)
* INCORRECT_RESPONSE_ERROR : Response does not match the given correct json schema provided
* NO_REPEAT : Test is set not to repeat i.e. is executed only once (only successful executions)
* TRUE_DEPENDENCY_UNSATISFIED : True dependencies to other tests 
* FALSE_DEPENDENCY_UNSATISFIED : False dependencies to other tests

The Response Structure created as a result of execution has a response types (see api_utils), response messages with response body, and the time it took for the
response to be received by the sender. The information received can be sumarized by using the log_entry function. This prints a comma-separated-line of response with the following structure. 

* domain_name : Name of the test domain (i.e. the file name in which it was)
* test_name : Name of the test
* test_type : Whether the test had a single run or multiple runs. 
* response_status : The response status of all the responses as they were run aggregated by type, example if in a multi-test if 3 tests were successfull and 2 failed it will show up as Successful Execution:3 Status Error:1 Incorrect Response:1
* response_body :  Response body is present only in-case of an error, for status errors it prints the error code and the response message and for incorrect response it gives the json schema validator path where a mismatch occurs and the corresponding response message generated. Since there can be multiple erros each unique error type is printed, generating a list of tuples [(), (), ...]
* response_times : Response times are the time period between the request sent and the response chunk being received. It the response time incase of a single execution. For multiple executions the reported metrics are 
    * average response time
    * standard deviation
    * the highest 10% of the response times.


### Configuration

The api_logger class has the functionality to run tests present in domain and log the output in a log file. The required list of domains, its location and the name of the stats file to be used is given as a config file with the following structure to the program (main.py) as cmd line arguments. The log file where the test execution results are stored is also given as a parameters. Note that the logs generated are appended to already present logs in the log_file (or a new file is created if the file is not present).

```json
{
    "test_domain_dir": "",
    "test_domains": ["", "", "..."],
    "test_stats":""

}
```

* test_domain_dir: directory where the domains are present
* test_domains: the list of domains which in which tests will be executed
* test_stats: the file where the some logging information on the tests like how many times it runs, for checking dependencies are stored.

