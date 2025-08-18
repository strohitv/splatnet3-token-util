import json
from dataclasses import dataclass


@dataclass
class TokenConfig:
	"""Config class for json serialization of token configuration values"""

	def __init__(self,
				 extract_g_token=True,
				 extract_bullet_token=True,
				 extract_session_token=False,
				 validate_g_token=True,
				 validate_bullet_token=True,
				 validate_session_token=False,
				 validate_target_file_as_json=True,
				 validate_splat3_homepage=True):
		self.extract_g_token = extract_g_token
		self.extract_bullet_token = extract_bullet_token
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
