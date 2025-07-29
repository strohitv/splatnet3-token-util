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
				 max_run_duration_minutes=50,
				 max_attempt_duration_seconds=150,
				 extract_g_token = True,
				 extract_bullet_token = True,
				 bullet_token_curl_request="curl 'https://api.lp1.av5ja.srv.nintendo.net/api/bullet_tokens' --compressed -X POST -H 'User-Agent: Mozilla/5.0 (Linux; Android 11; Pixel 4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.230 Mobile Safari/537.36' -H 'Accept: */*' -H 'Accept-Language: en-US' -H 'Accept-Encoding: gzip, deflate, br, zstd' -H 'Referer: https://api.lp1.av5ja.srv.nintendo.net/' -H 'content-type: application/json' -H 'x-nacountry: US' -H 'x-web-view-ver: 6.0.0-bbd7c576' -H 'Origin: https://api.lp1.av5ja.srv.nintendo.net' -H 'DNT: 1' -H 'Connection: keep-alive' -H 'Cookie: _gtoken={GTOKEN}' -H 'Sec-Fetch-Dest: empty' -H 'Sec-Fetch-Mode: cors' -H 'Sec-Fetch-Site: same-origin' -H 'Priority: u=4' -H 'Content-Length: 0' -H 'TE: trailers'",
				 extract_session_token = False,
				 validate_g_token = True,
				 validate_bullet_token = True,
				 validate_session_token = False,
				 validate_target_file_as_json = True,
				 validate_splat3_homepage = True,
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
		self.max_run_duration_minutes = max_run_duration_minutes
		self.max_attempt_duration_seconds = max_attempt_duration_seconds
		self.extract_g_token = extract_g_token
		self.extract_bullet_token = extract_bullet_token
		self.bullet_token_curl_request = bullet_token_curl_request
		self.extract_session_token = extract_session_token
		self.validate_g_token = validate_g_token
		self.validate_bullet_token = validate_bullet_token
		self.validate_session_token = validate_session_token
		self.validate_target_file_as_json = validate_target_file_as_json
		self.validate_splat3_homepage = validate_splat3_homepage
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
