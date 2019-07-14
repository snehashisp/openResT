import api_test
import json
import copy

"""
API domain are a set of logically similar API tests. They may not all be call to the 
same web domain. API domains house the tests (structure in api_test file) that will be executed.
{
	"defaults": {
		...
	},
	"test1": { ... },
	"test2": { ... },
	...
}
It has a "defaults" metadata which contains default paramateres that will be applied to all the 
tests in the domain if they do not have the corresponding attribute. These default parameters can be overrident by
the same test specific parameter if they are present. For example, to set the the url of every test in the domain to
the same location set the url parameter as 
	"defaults": {
		"url":"..."
	}
and this parameter will be added to every test in the domain which do not have a url parameter. If any test has a 
url paramter that parameter will overrride the default url parameter. 

The addition and overriding of default parameters work recursively to add defaults to any nested json objects. example
To set the payload of WEB notifications uder the data (REST api message body) set the defalts as 
	"defaults": {
		"data": {
			"payload": {
				"WEB" : "xyz"
			}
		}
	}
If there exists a test with data as
	"data": {
		"payload": {
			"redirect":"abc.com"
		},
		"retry": true
	}
then the merged test will have the data attribute as 
	"data" : {
		"payload": {
			"WEB": "xyz",
			"redirect":, "abc.xom"
		}
		"retry": true
	}
"""

class ApiDomain:

	def __init__(self, domain_name, domain):

		self.domain_name = domain_name
		self.domain = domain
		self.test_defaults = domain.pop("defaults", {})

	def _update_defaults(self, default_map, test_map):

		for k, v in test_map.items():
			if type(default_map.get(k,None)) == dict and type(v) == dict:
				default_map_value = default_map.pop(k, {})
				default_map[k] = self._update_defaults(default_map_value, v)
			else:
				default_map[k] = v
		return default_map


	def generate_tests(self):

		for k, v in self.domain.items():
			default_map = copy.deepcopy(self.test_defaults)
			yield api_test.ApiTest(self.domain_name, k, self._update_defaults(default_map, v))

