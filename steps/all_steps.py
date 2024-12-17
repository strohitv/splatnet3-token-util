from steps.block_until_screenshot_region_matches import BlockUntilScreenshotRegionMatches
from steps.echo import Echo
from steps.long_press_power_button import LongPressPowerButton
from steps.swipe import Swipe
from steps.tap import Tap
from steps.wait_ms import WaitMS
from steps.wait_s import WaitS


def get_steps(app_config):
	steps = {
		'block_until_screenshot_region_matches': BlockUntilScreenshotRegionMatches('block_until_screenshot_region_matches', app_config),
		'echo': Echo('echo', app_config),
		'long_press_power_button': LongPressPowerButton('long_press_power_button', app_config),
		'swipe': Swipe('swipe', app_config),
		'tap': Tap('tap', app_config),
		'wait_s': WaitS('wait_s', app_config),
		'wait_ms': WaitMS('wait_ms', app_config)
	}

	return steps
