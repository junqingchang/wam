from wam import WarcraftAddonManager


config_file = 'wamconfig.json'

if __name__ == '__main__':
    manager = WarcraftAddonManager(config_file=config_file)
    manager.wam_cmd()