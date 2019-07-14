import api_test
from datetime import datetime
import copy
import json

class ApiStats:

	def __init__(self, test_stats_file):
		self.test_stats_file = test_stats_file
		try:
			with open(test_stats_file,'r') as fp:
				self.test_stats = json.load(fp)
		except:
			self.test_stats = {}

		self.default_stats_map = {
			"last_executed_time" : None,
			"successfull_runs" : 0,
			"failure_runs" : 0
		}

	def get_test_time(self, domain_name, test_name):
		return test_stats.get(domain_name, {}).get(test_name, {}).get('last_executed_time', None)

	def get_test_success_count(self, domain_name, test_name):
		return test_stats.get(domain_name, {}).get(test_name, {}).get('successfull_runs', 0)

	def get_test_failure_count(self, domain_name, test_name):
		return test_stats.get(domain_name, {}).get(test_name, {}).get('failure_runs', 0)

	def increment_success(self, domain_name, test_name, increment_amount = 1):
		test_stats = self.test_stats.setdefault(domain_name, {})
		test_stats.setdefault(test_name, copy.deepcopy(self.default_stats_map))['successfull_runs'] += increment_amount
		test_stats[test_name]['last_executed_time'] = str(datetime.utcnow())

	def increment_failure(self, domain_name, test_name, increment_amount = 1):
		test_stats = self.test_stats.setdefault(domain_name, {})
		test_stats.setdefault(test_name, copy.deepcopy(self.default_stats_map))['failure_runs'] += increment_amount
		test_stats[test_name]['last_executed_time'] = str(datetime.utcnow())

	def update_stats_file(self):
		with open(self.test_stats_file,'w') as fp:
			json.dump(self.test_stats, fp)

	#def __del__(self):
	#	self.update_stats_file()

