from data.app_config import AppConfig
from steps.block_while import BlockWhile
from steps.close_nsa import CloseNSA
from steps.create_screenshot import CreateScreenshot
from steps.echo import Echo
from steps.execute_while import ExecuteWhile
from steps.open_splatnet3 import OpenSplatNet3
from steps.press_power_button_long import PressPowerButtonLong
from steps.shutdown_emu import ShutdownEmulator
from steps.swipe import Swipe
from steps.search_and_tap_center import SearchAndTapCenter
from steps.tap import Tap
from steps.type import Type
from steps.wait_ms import WaitMS
from steps.wait_s import WaitS


def get_steps(app_config: AppConfig):
	steps = {}

	steps['block_while'] = BlockWhile('block_while', app_config)
	steps['close_nsa'] = CloseNSA('close_nsa', app_config)
	steps['create_screenshot'] = CreateScreenshot('create_screenshot', app_config)
	steps['echo'] = Echo('echo', app_config)
	steps['execute_while'] = ExecuteWhile('execute_while', app_config, steps)
	steps['open_splatnet3'] = OpenSplatNet3('open_splatnet3', app_config)
	steps['press_power_button_long'] = PressPowerButtonLong('press_power_button_long', app_config)
	steps['search_and_tap_center'] = SearchAndTapCenter('search_and_tap_center', app_config, steps)
	steps['shutdown_emu'] = ShutdownEmulator('shutdown_emu', app_config)
	steps['swipe'] = Swipe('swipe', app_config)
	steps['tap'] = Tap('tap', app_config)
	steps['type'] = Type('type', app_config)
	steps['wait_s'] = WaitS('wait_s', app_config)
	steps['wait_ms'] = WaitMS('wait_ms', app_config)

	return steps
