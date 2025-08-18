import json
from dataclasses import dataclass

from data.emulator_config import EmulatorConfig
from data.run_config import RunConfig
from data.token_config import TokenConfig
from data.update_config import UpdateConfig


@dataclass
class AppConfig:
	"""Config class for json serialization of application configuration values"""

	def __init__(self,
				 emulator_config=EmulatorConfig(),
				 run_config=RunConfig(),
				 token_config=TokenConfig(),
				 update_config=UpdateConfig(),
				 debug=False):
		if isinstance(emulator_config, EmulatorConfig):
			self.emulator_config = emulator_config
		else:
			self.emulator_config = EmulatorConfig()
			AppConfig.__fill_fields(self.emulator_config, emulator_config)

		if isinstance(run_config, RunConfig):
			self.run_config = run_config
		else:
			self.run_config = RunConfig()
			AppConfig.__fill_fields(self.run_config, run_config)

		if isinstance(token_config, TokenConfig):
			self.token_config = token_config
		else:
			self.token_config = TokenConfig()
			AppConfig.__fill_fields(self.token_config, token_config)

		if isinstance(update_config, UpdateConfig):
			self.update_config = update_config
		else:
			self.update_config = UpdateConfig()
			AppConfig.__fill_fields(self.update_config, update_config)

		self.debug = debug

	@staticmethod
	def __fill_fields(target, source):
		fields = [i for i in target.__dict__.keys() if i[:1] != '_']

		for field in fields:
			if field in source:
				setattr(target, field, source[field])

	def to_json(self):
		return json.dumps(
			self,
			default=lambda o: o.__dict__,
			sort_keys=True,
			indent=4)
