import sys
from copy import deepcopy
from util.logger import Logger
import util.config_consts
import json

class Config(object):
    """Config module that reads and validates the config to be passed to
    azurlane-auto
    """

    def __init__(self, config_file):
        """Initializes the config file by changing the working directory to the
        root azurlane-auto folder and reading the passed-in config file.

        Args:
            config_file (string): Name of config file.
        """
        Logger.log_msg("Initializing config module")
        self.config_file = config_file
        self.ok = False
        self.initialized = False
        self.login = {'enabled': False}
        self.cafe = {'enabled': False}
        self.farming = {'enabled': False}
        self.tactical_challenge = {'enabled': False}
        self.bounty = {'enabled': False}
        self.scrimmage = {'enabled': False}
        self.mission = {'enabled': False}
        self.claim_rewards = {'enabled': False}
        self.network = None
        self.assets = None
        self.screenshot_mode = None
        self.restart_attempts = 0
        self.read()

    def read(self):
        backup_config = deepcopy(self.__dict__)

        # Read the JSON file
        try:
            with open(self.config_file, 'r') as json_file:
                config_data = json.load(json_file)
        except FileNotFoundError:
            Logger.log_error(f"Config file '{self.config_file}' not found.")
            sys.exit(1)
        except json.JSONDecodeError:
            Logger.log_error(f"Invalid JSON format in '{self.config_file}'.")
            sys.exit(1)

        self.login = config_data.get('login', {'enabled': False})
        self.network = config_data["login"]["network"]
        self.assets = config_data["login"]["server"]
        self.restart_attempts = config_data["login"]["restart_attempts"]
        self.cafe = config_data.get('cafe', {'enabled': False})
        self.farming = config_data.get('farming', {'enabled':False})
        self.tactical_challenge = config_data["farming"]["tactical_challenge"]
        self.bounty = config_data["farming"]["bounty"]
        self.scrimmage = config_data["farming"]["scrimmage"]
        self.mission = config_data["farming"]["mission"]
        self.claim_rewards = config_data.get('claim_rewards', {'enabled': False})

        consts = util.config_consts.UtilConsts.ScreenCapMode
        screenshot_mode = config_data.get('login', {}).get('screenshot_mode', '').upper()
        vals = {'SCREENCAP_PNG':consts.SCREENCAP_PNG, 'SCREENCAP_RAW':consts.SCREENCAP_RAW, 
                'UIAUTOMATOR2': consts.UIAUTOMATOR2, 'ASCREENCAP':consts.ASCREENCAP}
        
        if screenshot_mode not in ['SCREENCAP_PNG', 'SCREENCAP_RAW', 'UIAUTOMATOR2', 'ASCREENCAP']:
            raise ValueError("Invalid screenshot mode")
        
        self.screenshot_mode = vals[screenshot_mode]

        self.validate()

        if (self.ok and not self.initialized):
            Logger.log_msg("Starting BAAuto!")
            self.initialized = True
            self.changed = True
        elif (not self.ok and not self.initialized):
            Logger.log_error("Invalid config. Please check your config file.")
            sys.exit(1)
        elif (not self.ok and self.initialized):
            Logger.log_warning("Config change detected, but with problems. Rolling back config.")
            self._rollback_config(backup_config)
        elif (self.ok and self.initialized):
            if backup_config != self.__dict__:
                Logger.log_warning("Config change detected. Hot-reloading.")
                self.changed = True
        
    def validate(self):
        """Method to validate the passed-in config file
        """
        if not self.initialized:
            Logger.log_msg("Validating config")
        self.ok = True

        valid_servers = ['EN']
        if self.assets not in valid_servers:
            if len(valid_servers) < 2:
                Logger.log_error("Invalid server assets configured. Only {} is supported.".format(''.join(valid_servers)))
            else:
                Logger.log_error("Invalid server assets configured. Only {} and {} are supported.".format(', '.join(valid_servers[:-1]), valid_servers[-1]))
            self.ok = False

        if not any(module['enabled'] for module in [self.login, self.cafe, self.farming, self.claim_rewards]):
            Logger.log_error("All modules are disabled, consider checking your config.")
            self.ok = False

    def _rollback_config(self, config):
        """Method to roll back the config to the passed-in config's.
        Args:
            config (dict): previously backed up config
        """
        for key in config:
            setattr(self, key, config['key'])
