import json
from dataclasses import dataclass

from data.emulator_config import EmulatorConfig
from data.run_config import RunConfig
from data.token_config import TokenConfig


@dataclass
class AppConfig:
	"""Config class for json serialization of application configuration values"""

	def __init__(self,
				 emulator_config=EmulatorConfig(),
				 run_config=RunConfig(),
				 token_config=TokenConfig(),
				 debug=False):
		if isinstance(emulator_config, EmulatorConfig):
			self.emulator_config = emulator_config
		else:
			self.emulator_config = EmulatorConfig(**emulator_config)

		if isinstance(run_config, RunConfig):
			self.run_config = run_config
		else:
			self.run_config = RunConfig(**run_config)

		if isinstance(token_config, TokenConfig):
			self.token_config = token_config
		else:
			self.token_config = TokenConfig(**token_config)

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
