import json


class AppConfig:
	"""Config class for json serialization of configuration values"""

	def __init__(self,
				 emulator_path='~/Android/Sdk/emulator/emulator',
				 adb_path='~/Android/Sdk/platform-tools/adb',
				 avd_name='SplatNet3',
				 snapshot_dir='~/.android/avd/SplatNet3.avd/snapshots/',
				 snapshot_name='splatnet3-emu-token-util',
				 show_window=True,
				 template_path='./config/template.txt',
				 target_path='./config.txt',
				 boot_script_path='./config/boot.txt',
				 cleanup_script_path='./config/cleanup.txt',
				 max_attempts=10,
				 extract_g_token = True,
				 extract_bullet_token = True,
				 extract_session_token = True,
				 validate_g_token = True,
				 validate_bullet_token = True,
				 validate_session_token = True,
				 log_stats_csv=False,
				 stats_csv_path='./stats.csv',
				 debug=False):
		self.emulator_path = emulator_path
		self.adb_path = adb_path
		self.avd_name = avd_name
		self.snapshot_dir = snapshot_dir
		self.snapshot_name = snapshot_name
		self.show_window = show_window
		self.template_path = template_path
		self.target_path = target_path
		self.boot_script_path = boot_script_path
		self.cleanup_script_path = cleanup_script_path
		self.max_attempts = max_attempts
		self.extract_g_token = extract_g_token
		self.extract_bullet_token = extract_bullet_token
		self.extract_session_token = extract_session_token
		self.validate_g_token = validate_g_token
		self.validate_bullet_token = validate_bullet_token
		self.validate_session_token = validate_session_token
		self.log_stats_csv = log_stats_csv
		self.stats_csv_path = stats_csv_path
		self.debug = debug

	def to_json(self):
		return json.dumps(
			self,
			default=lambda o: o.__dict__,
			sort_keys=True,
			indent=4)

	@classmethod
	def from_json(cls, d):
		return cls(**d)
