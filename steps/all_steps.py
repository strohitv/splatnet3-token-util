from data.app_config import AppConfig
from steps.block_as_long_as_region_matches import BlockAsLongAsRegionMatches
from steps.block_until_region_matches import BlockUntilRegionMatches
from steps.echo import Echo
from steps.execute_command_as_long_as_region_matches import ExecuteCommandAsLongAsRegionMatches
from steps.execute_command_until_region_matches import ExecuteCommandUntilRegionMatches
from steps.long_press_power_button import LongPressPowerButton
from steps.swipe import Swipe
from steps.search_region_and_tap_center import SearchRegionAndTapCenter
from steps.tap import Tap
from steps.wait_ms import WaitMS
from steps.wait_s import WaitS

def get_steps(app_config: AppConfig):
	steps = {}

	steps['block_until_region_matches'] = BlockUntilRegionMatches('block_until_region_matches', app_config)
	steps['block_as_long_as_region_matches'] = BlockAsLongAsRegionMatches('block_as_long_as_region_matches', app_config)
	steps['echo'] = Echo('echo', app_config)
	steps['execute_command_as_long_as_region_matches'] = ExecuteCommandAsLongAsRegionMatches('execute_command_as_long_as_region_matches', app_config, steps)
	steps['execute_command_until_region_matches'] = ExecuteCommandUntilRegionMatches('execute_command_until_region_matches', app_config, steps)
	steps['long_press_power_button'] = LongPressPowerButton('long_press_power_button', app_config)
	steps['search_region_and_tap_center'] = SearchRegionAndTapCenter('search_region_and_tap_center', app_config, steps)
	steps['swipe'] = Swipe('swipe', app_config)
	steps['tap'] = Tap('tap', app_config)
	steps['wait_s'] = WaitS('wait_s', app_config)
	steps['wait_ms'] = WaitMS('wait_ms', app_config)


	return steps
