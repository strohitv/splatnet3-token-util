import json


class S3sConfig:
	"""Config class for json serialization of s3s configuration"""

	def __init__(self,
				 gtoken='{GTOKEN}',
				 bullettoken='{BULLETTOKEN}',
				 session_token='{SESSIONTOKEN}',
				 api_key='INSERT_STAT_INK_API_KEY_HERE',
				 acc_loc='en-US|DE',
				 f_gen='https://api.imink.app/f'):
		self.gtoken = gtoken
		self.bullettoken = bullettoken
		self.session_token = session_token
		self.api_key = api_key
		self.acc_loc = acc_loc
		self.f_gen = f_gen

	def to_json(self):
		return json.dumps(
			self,
			default=lambda o: o.__dict__,
			sort_keys=True,
			indent=4)

	@classmethod
	def from_json(cls, d):
		return cls(**d)
