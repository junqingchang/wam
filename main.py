from wam import WarcraftAddonManager


addon_path = ''
config_file = ''

if __name__ == '__main__':
    manager = WarcraftAddonManager(addon_path=addon_path, config_file=config_file)
    manager.add_new_addon('')