import json
from dataclasses import dataclass


@dataclass
class EmulatorConfig:
	"""Config class for json serialization of emulator configuration values"""

	def __init__(self,
				 emulator_path='~/Android/Sdk/emulator/emulator',
				 emulator_boot_args='-avd {AVD_NAME} -feature -Vulkan -no-snapshot-load',
				 adb_path='~/Android/Sdk/platform-tools/adb',
				 avd_name='NSA',
				 snapshot_dir='~/.android/avd/{AVD_NAME}.avd/snapshots/',
				 snapshot_name='splatnet3-opened'):
		self.emulator_path = emulator_path
		self.emulator_boot_args = emulator_boot_args
		self.adb_path = adb_path.replace(' ', '_')
		self.avd_name = avd_name
		self.snapshot_dir = snapshot_dir
		self.snapshot_name = snapshot_name

	def get_emulator_boot_args(self):
		return self.emulator_boot_args.replace('{AVD_NAME}', self.avd_name)

	def get_snapshot_dir(self):
		return self.snapshot_dir.replace('{AVD_NAME}', self.avd_name)

	def to_json(self):
		return json.dumps(
			self,
			default=lambda o: o.__dict__,
			sort_keys=True,
			indent=4)
