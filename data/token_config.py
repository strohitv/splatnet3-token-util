import json
from dataclasses import dataclass


@dataclass
class TokenConfig:
	"""Config class for json serialization of token configuration values"""

	def __init__(self,
				 extract_g_token=True,
				 extract_bullet_token=True,
				 bullet_token_curl_request="curl 'https://api.lp1.av5ja.srv.nintendo.net/api/bullet_tokens' --compressed -X POST -H 'User-Agent: Mozilla/5.0 (Linux; Android 11; Pixel 4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.230 Mobile Safari/537.36' -H 'Accept: */*' -H 'Accept-Language: en-US' -H 'Accept-Encoding: gzip, deflate, br, zstd' -H 'Referer: https://api.lp1.av5ja.srv.nintendo.net/' -H 'content-type: application/json' -H 'x-nacountry: US' -H 'x-web-view-ver: 6.0.0-bbd7c576' -H 'Origin: https://api.lp1.av5ja.srv.nintendo.net' -H 'DNT: 1' -H 'Connection: keep-alive' -H 'Cookie: _gtoken={GTOKEN}' -H 'Sec-Fetch-Dest: empty' -H 'Sec-Fetch-Mode: cors' -H 'Sec-Fetch-Site: same-origin' -H 'Priority: u=4' -H 'Content-Length: 0' -H 'TE: trailers'",
				 extract_session_token=False,
				 validate_g_token=True,
				 validate_bullet_token=True,
				 validate_session_token=False,
				 validate_target_file_as_json=True,
				 validate_splat3_homepage=True):
		self.extract_g_token = extract_g_token
		self.extract_bullet_token = extract_bullet_token
		self.bullet_token_curl_request = bullet_token_curl_request
		self.extract_session_token = extract_session_token
		self.validate_g_token = validate_g_token
		self.validate_bullet_token = validate_bullet_token
		self.validate_session_token = validate_session_token
		self.validate_target_file_as_json = validate_target_file_as_json
		self.validate_splat3_homepage = validate_splat3_homepage

	def to_json(self):
		return json.dumps(
			self,
			default=lambda o: o.__dict__,
			sort_keys=True,
			indent=4)

	@classmethod
	def from_json(cls, d):
		return cls(**d)
