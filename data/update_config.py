import json
from dataclasses import dataclass


@dataclass
class UpdateConfig:
	"""Config class for json serialization of configuration values"""

	def __init__(self,
				 git_command='git',
				 pip_command='pip',
				 check_for_update=True):
		self.git_command = git_command
		self.pip_command = pip_command
		self.check_for_update = check_for_update

	def to_json(self):
		return json.dumps(
			self,
			default=lambda o: o.__dict__,
			sort_keys=True,
			indent=4)

	@classmethod
	def from_json(cls, d):
		return cls(**d)
