from util.logger import Logger
from util.config import Config
from util.utils import Utils, Region, GoTo
from datetime import datetime, time
import json
import copy
import os 

class MissionModule(object):
    def __init__(self, config):
        """Initializes the Mission Module.

        Args:
            config (Config): BAAuto Config instance
        """
        self.enabled = True
        self.config = config
        self.acronym = {
            'N': 'Mission Normal',
            'H': 'Mission Hard',
            'BR': 'Commissions Base Defense',
            'IR': 'Commissions Item Retrieval',
            'E': "Event"
        }
        self.region = {
            'ap': Region(555, 0, 105, 45),
            'stage_list': Region(677, 132, 747, 678)
        }

    def mission_logic_wrapper(self):
        clear_queue = False
        recharged = False
        location = None
        current_ap, max_ap = self.read_ap()
        Logger.log_info(f'AP detected: {current_ap}/{max_ap}')

        # Check if there's enough AP to proceed
        if current_ap < 10:
            Logger.log_warning('Not enough AP to complete stages.')
            if self.config.mission['recharge_ap']:
                Logger.log_info('Attempting to recharge AP...')
                self.recharge_ap()
                current_ap, max_ap = self.read_ap()
                if current_ap < 10:
                    Logger.log_warning('Still not enough AP to complete stages. Unable to proceed.')
            Logger.log_info('Recharge AP disabled. Unable to complete stages.')
            return

        # Check if it's time to clear the queue or reset daily
        if self.config.mission['reset_daily']:
            clear_queue = self.check_reset_time()

        # If the queue is empty or needs clearing, populate it
        if clear_queue or self.config.mission['queue'] == []:
            preferred_template = self.config.mission['preferred_template']
            self.config.mission['queue'] = copy.deepcopy(self.config.mission["templates"][preferred_template])

        # Process each entry in the queue
        while self.config.mission['queue'] != []:
            entry = self.config.mission['queue'][0]
            if entry[0].upper() in ['N', 'H']:
                location = 'mission'
                sweep_status = self.mission(entry)
            elif entry[0].upper() in ['BD', 'IR']:
                location = 'commissions'
                sweep_status = self.commissions(entry)
            else:
                location = 'event'
                sweep_status = self.event(entry)                

            # Handle incomplete sweeps
            if sweep_status[0] == 'incomplete':
                current_ap, max_ap = self.read_ap(location)
                if not recharged and self.config.mission['recharge_ap']:
                    if current_ap < 20:
                        Logger.log_info('Attempting to recharge AP...')
                        self.config.mission['queue'][0][2] -= sweep_status[1]
                        self.update_config()
                        self.recharge_ap()
                        recharged = True
                        continue
                else:
                    self.config.mission['queue'][0][2] -= sweep_status[1]
                    self.update_config()
                    Logger.log_info(f'AP left: {current_ap} / {max_ap}. Unable to complete stages.')
                    return

            self.config.mission['queue'].pop(0)
            self.update_config()

    def mission(self, entry):
        # Logic for mission stages
        GoTo.sub_campaign('mission')
        mode, stage, run_times = entry
        Logger.log_info(f'Current stage: {self.acronym[mode]} {stage}, run {run_times} times')
        area = int(stage.split('-')[0].strip())

        if not self.find_area(area):
            Logger.log_error('Area not found, please check spelling. Skipping stage...')
            return ('failed')

        if mode.upper() == 'H':
            if run_times > 3:
                Logger.log_warning(f'Hard {stage} was set to be swept {run_times}. Reset to 3 as it surpass limit.')
                run_times = 3

            while Utils.find('farming/normal'):
                Utils.touch(1065, 160)
                Utils.wait_update_screen(1)
        else:
            while not Utils.find('farming/normal'):
                Utils.touch(915, 160)
                Utils.wait_update_screen(1)

        return self.attempt_stage(mode, stage, run_times)

    def commissions(self, entry):
        # Logic for commission stages
        GoTo.sub_campaign('commissions')
        mode, stage, run_times = entry

        while Utils.find('goto/commissions'):
            if mode.upper() == 'BD':
                Utils.touch(800, 200)
            else:
                Utils.touch(800, 310)
            Utils.update_screen()

        return self.attempt_stage(mode, stage, run_times)
    
    def event(self, entry):
        if self.config.mission["event"] == True:
            event_banner_path = f"assets/{Utils.assets}/goto/event_banner.png"
            mode, stage, run_times = entry
            Logger.log_info(f'Current stage: {self.acronym[mode]} {stage}, run {run_times} times')
            if os.path.exists(event_banner_path):
                GoTo.event()
                while Utils.find_and_touch('farming/quest'):
                    Utils.wait_update_screen(1)
                return self.attempt_stage(mode, stage, run_times)
            else:
                Logger.log_warning("Event Banner not found. Unable to run event stages.")
        return ("failed")


    def find_area(self, desired_area):
        # Find and navigate to the desired area
        roi = Region(108, 178, 62, 37)
        left = (45, 360)
        right = (1240, 360)
        last_area = None

        while True:
            Utils.wait_update_screen(1)
            detected_area = int(Utils.scan(roi, resize=True)[0]['text'])

            if detected_area == last_area:
                return False
            elif detected_area < desired_area:
                Utils.touch(*right)
                last_area = detected_area
            elif detected_area > desired_area:
                Utils.touch(*left)
                last_area = detected_area
            else:
                return True

    def attempt_stage(self, mode, stage, run_times):
        # Logic for attempting a stage
        stage_region = Utils.find_stage(stage)

        if stage_region:
            if mode in ['H', 'E']:
                button = Utils.find_button('farming/big_enter', stage_region, self.region['stage_list'])
            else:
                button = Utils.find_button('farming/small_enter', stage_region, self.region['stage_list'])

            if button:
                while True:
                    Utils.wait_update_screen(1)
                    if not Utils.find('farming/sweep'):
                        Utils.touch_randomly(button)
                        continue
                    outcome = Utils.sweep(run_times)
                    if outcome[0] == "incomplete" and outcome[1] != 0:
                        Logger.log_warning(f'Ran out of AP but enough to complete stage {outcome[1]} times instead of {run_times}')
                    return outcome
            else:
                Logger.log_error(f'{self.acronym[mode]} {stage} is not unlocked')
        return ('failed')

    def read_ap(self, location=None):
        # Read and return current AP and max AP
        if location is None:
            GoTo.sub_home('campaign')
        elif location == "event":
            GoTo.event()    
        else:
            GoTo.sub_campaign(location)
        waiting_time = 0    
        ap = [""]
        # solution to AP being hidden by tasks notifications
        while waiting_time <= 5 and not ap[0].isdigit():
            Utils.wait_update_screen(1)
            ap = Utils.scan(self.region['ap'])[0]['text']
            waiting_time += 1
        if not ap[0].isdigit():
            Logger.log_error("Error reading AP")
        return [int(x) for x in [x.strip() for x in ap.split('/')]]

    def recharge_ap(self):
        # Recharge AP if configured to do so
        if self.config.mission['recharge_ap']:
            if self.config.cafe['enabled'] and self.config.cafe['claim_earnings']:
                GoTo.sub_home('cafe')
                while True:
                    Utils.wait_update_screen(1)
                    if not Utils.find("cafe/earnings"):
                        Utils.touch(1158, 647)
                    else:
                        Utils.touch(640, 520)
                        break
            if self.config.claim_rewards['enabled']:
                from modules.claim_rewards import ClaimRewardsModule
                ClaimRewardsModule(self.config).claim_rewards_logic_wrapper()

    def check_reset_time(self):
        # Check if it's time to reset the queue
        current_datetime = datetime.now().replace(microsecond=0)  # Round to the nearest second
        current_date = current_datetime.date()
        current_time = current_datetime.time()
        last_run_datetime = datetime.strptime(self.config.mission["last_run"], "%Y-%m-%d %H:%M:%S")
        reset_time = datetime.strptime(self.config.mission["reset_time"], "%H:%M:%S").time()

        if current_date != last_run_datetime.date() and current_time >= reset_time:
            self.update_config(last_run=True)
            Logger.log_info("Reset Daily activated. Resetting queue...")
            return True
        return False

    def update_config(self, last_run=False):
        # Update the configuration file with the current queue and last run time
        with open('config.json', 'r') as json_file:
            config_data = json.load(json_file)
        config_data["farming"]['mission']['queue'] = self.config.mission['queue']
        if last_run:
            config_data["farming"]['mission']["last_run"] = str(datetime.now().replace(microsecond=0))
        with open("config.json", "w") as json_file:
            json.dump(config_data, json_file, indent=2)
