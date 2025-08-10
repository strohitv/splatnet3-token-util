from data.app_config import AppConfig
from steps.block_while import BlockWhile
from steps.echo import Echo
from steps.execute_while import ExecuteWhile
from steps.press_power_button_long import PressPowerButtonLong
from steps.swipe import Swipe
from steps.search_and_tap_center import SearchAndTapCenter
from steps.tap import Tap
from steps.wait_ms import WaitMS
from steps.wait_s import WaitS


def get_steps(app_config: AppConfig):
	steps = {}

	steps['block_while'] = BlockWhile('block_while', app_config)
	steps['echo'] = Echo('echo', app_config)
	steps['execute_while'] = ExecuteWhile('execute_while', app_config, steps)
	steps['press_power_button_long'] = PressPowerButtonLong('press_power_button_long', app_config)
	steps['search_and_tap_center'] = SearchAndTapCenter('search_and_tap_center', app_config, steps)
	steps['swipe'] = Swipe('swipe', app_config)
	steps['tap'] = Tap('tap', app_config)
	steps['wait_s'] = WaitS('wait_s', app_config)
	steps['wait_ms'] = WaitMS('wait_ms', app_config)

	return steps
