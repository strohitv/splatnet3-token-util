import json
from dataclasses import dataclass


@dataclass
class RunConfig:
	"""Config class for json serialization of configuration values"""

	def __init__(self,
				 template_path='./config/template.txt',
				 target_path='./config.txt',
				 boot_script_path='./config/boot.txt',
				 cleanup_script_path='./config/cleanup.txt',
				 max_run_duration_minutes=50,
				 max_attempt_duration_seconds=180,
				 log_stats_csv=False,
				 stats_csv_path='./stats.csv'):
		self.template_path = template_path
		self.target_path = target_path
		self.boot_script_path = boot_script_path
		self.cleanup_script_path = cleanup_script_path
		self.max_run_duration_minutes = max_run_duration_minutes
		self.max_attempt_duration_seconds = max_attempt_duration_seconds
		self.log_stats_csv = log_stats_csv
		self.stats_csv_path = stats_csv_path

	def to_json(self):
		return json.dumps(
			self,
			default=lambda o: o.__dict__,
			sort_keys=True,
			indent=4)
