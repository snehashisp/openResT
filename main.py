from api_base import api_logger

default_config = "./moe-config.json"
api_log = api_logger.ApiLogs(default_config, debug = True)
api_log.run_domains("moe-domain_log.csv")


