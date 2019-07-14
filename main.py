import api_logger

default_config = "./config.json"
api_log = api_logger.ApiLogs(default_config, debug = True)
api_log.run_domains("domain_log.csv")


