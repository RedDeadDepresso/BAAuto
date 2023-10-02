import sys
import re
import traceback
import argparse
try:
    from modules.login import LoginModule
    from modules.cafe import CafeModule
    from modules.bounty import BountyModule
    from modules.scrimmage import ScrimmageModule
    from modules.mission import MissionModule
    from modules.tactical_challenge import TacticalChallengeModule
    from modules.claim_rewards import ClaimRewardsModule
    from util.adb import Adb
    from util.config import Config
    from util.logger import Logger
    from util.utils import Utils
    from util.exceptions import GameStuckError, GameNotRunningError, ReadOCRError
    class BAAuto(object):
        modules = {
            'login': None,
            'cafe': None,
            'club': None,
            'mission': None,
            'bounty': None,
            'scrimmage': None,
            'tactical_challenge': None,
            'claim_rewards': None,
        }

        def __init__(self, config):
            """Initializes the primary azurlane-auto instance with the passed in
            Config instance; 

            Args:
                config (Config): BAAuto Config instance
            """
            self.config = config
            if self.config.login['enabled']:
                self.modules['login'] = LoginModule(self.config)
            if self.config.cafe['enabled']:
                self.modules['cafe'] = CafeModule(self.config)
            if self.config.farming['enabled'] and self.config.bounty['enabled']:
                self.modules['bounty'] = BountyModule(self.config)
            if self.config.farming['enabled'] and self.config.scrimmage['enabled']:
                self.modules['scrimmage'] = ScrimmageModule(self.config)
            if self.config.farming['enabled'] and self.config.mission['enabled']:
                self.modules['mission'] = MissionModule(self.config)
            if self.config.farming['enabled'] and self.config.tactical_challenge['enabled']:
                self.modules['tactical_challenge'] = TacticalChallengeModule(self.config)
            if self.config.claim_rewards['enabled']:
                self.modules['claim_rewards'] = ClaimRewardsModule(self.config)
                
        def run_login_cycle(self):
            """Method to run the login cycle.
            """
            if self.modules['login']:
                return self.modules['login'].login_logic_wrapper
            return None

        def run_cafe_cycle(self):
            """Method to run the cafe cycle.
            """
            if self.modules['cafe']:
                return self.modules['cafe'].cafe_logic_wrapper
            return None

        def run_bounty_cycle(self):
            """Method to run the bounty cycle.
            """
            if self.modules['bounty']:
                return self.modules['bounty'].bounty_logic_wrapper
            return None
        
        def run_scrimmage_cycle(self):
            """Method to run the scrimmage cycle.
            """
            if self.modules['scrimmage']:
                return self.modules['scrimmage'].scrimmage_logic_wrapper
            return None

        def run_mission_cycle(self):
            """Method to run the mission cycle.
            """
            if self.modules['mission']:
                return self.modules['mission'].mission_logic_wrapper
            return None
        
        def run_tactical_challenge_cycle(self):
            """Method to run the tactica challenge cycle.
            """
            if self.modules['tactical_challenge']:
                return self.modules['tactical_challenge'].tactical_challenge_logic_wrapper
            return None

        def run_claim_rewards_cycle(self):
            """Method to run the claim rewards cycle.
            """
            if self.modules['claim_rewards']:
                return self.modules['claim_rewards'].claim_rewards_logic_wrapper
            return None
        
    # check run-time args
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config',
                        metavar=('CONFIG_FILE'),
                        help='Use the specified configuration file instead ' +
                            'of the default config.ini')
    parser.add_argument('-d', '--debug',
                        help='Enables debugging logs.', action='store_true')
    parser.add_argument('-l', '--legacy',
                        help='Enables sed usage.', action='store_true')
    args = parser.parse_args()
    # check args, and if none provided, load default config
    if args:
        if args.config:
            config = Config(args.config)
        else:
            config = Config('config.json')
        if args.debug:
            Logger.log_info("Enabled debugging.")
            Logger.enable_debugging(Logger)
        if args.legacy:
            Logger.log_info("Enabled sed usage.")
            Adb.enable_legacy(Adb)

    with open('traceback.log', 'w') as f:
        pass

    script = BAAuto(config)

    Adb.service = config.network
    Adb.tcp = False if (Adb.service.find(':') == -1) else True
    adb = Adb()

    if adb.init():
        Logger.log_msg('Successfully connected to the service with transport_id({}).'.format(Adb.transID))
        output = Adb.exec_out('wm size').decode('utf-8').strip()

        if not re.search('1280x720|1280x720', output):
            Logger.log_error("Resolution is not 1280x720, please change it.")
            sys.exit()

        if 'com.nexon.bluearchive' not in Adb.u2device.app_list():
            Logger.log_error("Blue Archive is not installed. Unable to run script.")
            sys.exit()     

        Utils.assets = config.assets
        # screencap init
        Utils.init_screencap_mode(config.screenshot_mode)
        Utils.init_ocr_mode()
        Utils.record['restart_attempts'] = config.restart_attempts
    else:
        Logger.log_error('Unable to connect to the service.')
        sys.exit()

except:
    print(f'[ERROR] Script Initialisation Error. For more info, check the traceback.log file.')
    with open('traceback.log', 'w') as f:
        f.write(f'Script Initialisation Error')
        f.write('\n')
        traceback.print_exc(None, f, True)
        f.write('\n')
        sys.exit()

run_cycles = [
    ('Login', script.run_login_cycle),
    ('Cafe', script.run_cafe_cycle),
    ('Bounty', script.run_bounty_cycle),
    ('Scrimmage', script.run_scrimmage_cycle),
    ('Mission/Commissions', script.run_mission_cycle),
    ('Tactical Challenge', script.run_tactical_challenge_cycle),
    ('Claim Rewards', script.run_claim_rewards_cycle)
]
counter = 0
task_started = False
task_restarted = False
while counter != len(run_cycles):
    try:
        enabled = run_cycles[counter][1]()
        if enabled:
            if not task_started:
                Logger.log_info(f'Start Task: {run_cycles[counter][0]}')
                task_started = True
            enabled()
    except GameNotRunningError:
        if not Utils.record['game_started']:
            Logger.log_warning("Blue Archive is not running. Attempting to start it...")
            Adb.u2device.app_start("com.nexon.bluearchive", use_monkey=True)
        elif Utils.record['restart_attempts'] > 0:
            Logger.log_warning("Blue Archive crashed. Attempting to restart it...")
            Adb.u2device.app_start("com.nexon.bluearchive", use_monkey=True)
            Utils.record['restart_attempts'] -= 1
            Logger.log_warning(f"Restart attempts left: {Utils.record['restart_attempts']}")
        else:
            Logger.log_warning(f"Blue Archive is not running but ran out of restart attempts. Unable to restart game and run script.")
            sys.exit(1)     
        Utils.reset_record()
    except GameStuckError:
        if Utils.record['restart_attempts'] > 0:
            Logger.log_warning("Blue Archive is stuck. Attempting to restart it...")
            Adb.u2device.app_stop("com.nexon.bluearchive")
            Adb.u2device.app_start("com.nexon.bluearchive", use_monkey=True)
            Utils.record['restart_attempts'] -= 1
            Logger.log_warning(f"Restart attempts left: {Utils.record['restart_attempts']}")
            Utils.reset_record()
        else:
            Logger.log_warning(f"Blue Archive is stuck but ran out of restart attempts. Unable restart game and run script.")
            sys.exit(1)     
    except ReadOCRError:
        if not task_restarted:
            Logger.log_warning("Failed to read OCR. Did you change page? Restarting task...")
            task_restarted = True
        else:
            Logger.log_error("Failed to read OCR again. Skipping task...")
            counter += 1
            task_started = False
            task_restarted = False
    except KeyboardInterrupt:
        # handling ^C from user
        Logger.log_msg("Received keyboard interrupt from user. Closing...")
        sys.exit(0)
    except SystemExit:
        pass
    except:
        Logger.log_error(f'Task error: {run_cycles[counter][0]}. For more info, check the traceback.log file.')
        with open('traceback.log', 'a') as f:
            f.write(f'[{run_cycles[counter][0]}]')
            f.write('\n')
            traceback.print_exc(None, f, True)
            f.write('\n')
        counter += 1
        task_started = False
    else:
        if enabled:
            Logger.log_success(f'Task completed: {run_cycles[counter][0]}')
        counter += 1
        task_started = False

        


        
