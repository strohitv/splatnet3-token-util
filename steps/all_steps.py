from steps.block_until_screenshot_region_matches import BlockUntilScreenshotRegionMatches
from steps.echo import Echo
from steps.execute_command_as_long_as_screenshot_region_matches import ExecuteCommandAsLongAsScreenshotRegionMatches
from steps.execute_command_until_screenshot_region_matches import ExecuteCommandUntilScreenshotRegionMatches
from steps.long_press_power_button import LongPressPowerButton
from steps.swipe import Swipe
from steps.search_region_and_tap_center import SearchRegionAndTapCenter
from steps.tap import Tap
from steps.wait_ms import WaitMS
from steps.wait_s import WaitS

def get_steps(app_config):
	steps = {}

	steps['block_until_screenshot_region_matches'] = BlockUntilScreenshotRegionMatches('block_until_screenshot_region_matches', app_config)
	steps['echo'] = Echo('echo', app_config)
	steps['execute_command_as_long_as_screenshot_region_matches'] = ExecuteCommandAsLongAsScreenshotRegionMatches('execute_command_as_long_as_screenshot_region_matches', app_config, steps)
	steps['execute_command_until_screenshot_region_matches'] = ExecuteCommandUntilScreenshotRegionMatches('execute_command_until_screenshot_region_matches', app_config, steps)
	steps['long_press_power_button'] = LongPressPowerButton('long_press_power_button', app_config)
	steps['search_region_and_tap_center'] = SearchRegionAndTapCenter('search_region_and_tap_center', app_config, steps)
	steps['swipe'] = Swipe('swipe', app_config)
	steps['tap'] = Tap('tap', app_config)
	steps['wait_s'] = WaitS('wait_s', app_config)
	steps['wait_ms'] = WaitMS('wait_ms', app_config)


	return steps
