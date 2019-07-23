from api_base import api_logger
import os
import sys
import json

if len(sys.argv) < 2:
	print("Format is python main.py {NAME OF CONFIG FILE} {NAME OF LOGGING FILE}")
else:
	if os.path.exists(sys.argv[1]):
		config = sys.argv[1]
		api_log = api_logger.ApiLogs(config, debug = False)
		log_file = "default_log_file.csv"
		if len(sys.argv) == 3:
			log_file = sys.argv[2]
		api_log.run_domains(log_file)
	else:
		print("File not present")


