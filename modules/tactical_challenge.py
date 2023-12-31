from util.logger import Logger
from util.utils import Utils, Region, GoTo
from tqdm import tqdm
import re

class TacticalChallengeModule(object):
    def __init__(self, config):
        """Initializes the Tactical Challenge module.

        Args:
            config (Config): BAAuto Config instance
        """
        self.enabled = True
        self.config = config
        self.rank = self.config.tactical_challenge['rank']
        self.wins = 0
        self.loses = 0

        # Define regions for various elements on the screen
        self.region = {
            'tickets' : None,
            'rival_1': Region(615, 190, 150, 60), 
            'rival_2': Region(615, 345, 150, 60),
            'rival_3': Region(615, 505, 150, 60),
            'outcome': Region(405, 240, 465, 210)
        }

    def determine_tickets_region(self):
        if Utils.assets == 'EN':
            self.region['tickets'] = Region(208, 472, 44, 33)
        elif Utils.assets == 'CN':
            self.region['tickets'] = Region(156,470, 54, 45)

    def tactical_challenge_logic_wrapper(self):
        # Go to the tactical challenge sub-campaign
        GoTo.sub_campaign('tactical_challenge')
        self.claim()
        self.determine_tickets_region()
        ticket_owned = self.read_tickets()
        
        while ticket_owned:
            match = self.find_match()
            
            while match:
                Utils.wait_update_screen()
                
                # Check if the formation screen is displayed
                if Utils.find_and_touch('tactical_challenge/formation'):
                    continue
                
                # Check if there are no tickets available
                if Utils.find_and_touch('tactical_challenge/no_tick'):
                    continue
                
                # Check if the mobilize button is available
                if Utils.find('tactical_challenge/mobilise'):
                    self.read_outcome()
                    ticket_owned = self.read_tickets()
                    
                    if not ticket_owned:
                        return
                    
                    self.progress_bar(45)
                    break
                
                # Check if there are no tickets left
                if Utils.find('tactical_challenge/no_tickets'):
                    Logger.log_warning(f'Run out of tickets')
                    return

    def claim(self):
        # Attempt to claim rewards
        for i in range(2):
            while True:
                Utils.update_screen()
                if not Utils.find_and_touch(f'tactical_challenge/claim/{i}', color=True):
                    GoTo.sub_campaign('tactical_challenge')
                    break

    def read_tickets(self):
        # Read the number of tickets owned
        Utils.update_screen()
        tickets_owned = Utils.scan(self.region['tickets'])[0]['text']
        tickets_owned = tickets_owned.strip(' ')
        Logger.log_msg(f'Tickets owned: {tickets_owned}')

        if tickets_owned == '0/5':
            Logger.log_warning(f'Run out of tickets')
            Logger.log_info(f'Total Wins: {self.wins}')
            Logger.log_info(f'Total Loses: {self.loses}')
            return False

        return tickets_owned

    def find_match(self):
        # Find and select a match based on rank preference
        Utils.touch(1160, 145)
        Utils.wait_update_screen(2)
        extract_integer = lambda input_string: int(re.search(r'\d+', input_string).group()) if re.search(r'\d+', input_string) else None
        options = [
            [self.region['rival_1'], extract_integer(Utils.scan(self.region['rival_1'])[0]['text'])],
            [self.region['rival_2'], extract_integer(Utils.scan(self.region['rival_2'])[0]['text'])],
            [self.region['rival_3'], extract_integer(Utils.scan(self.region['rival_3'])[0]['text'])]
        ]
        Logger.log_info(f'Ranks detected: {options[0][1]}, {options[1][1]}, {options[2][1]}')
        options.sort(key=lambda x: x[1], reverse=True)

        if self.rank.lower() == "highest":
            match = options[2]
            Logger.log_info(f'Ranks set to highest -> {match[1]}')
        elif self.rank.lower() == "middle":
            match = options[1]
            Logger.log_info(f'Ranks set to middle -> {match[1]}')
        else:
            match = options[0]
            Logger.log_info(f'Ranks set to lowest -> {match[1]}')

        Utils.touch_randomly(match[0])
        Utils.wait_update_screen(2)
        return match

    def progress_bar(self, total):
        # Display a progress bar while waiting
        with tqdm(total=total, ncols=100, bar_format='{l_bar}{bar}{n_fmt}/{total_fmt}s', desc='Waiting Standby Time', colour='cyan') as pbar:
            for i in range(total):
                pbar.update(1)
                Utils.script_sleep(1)

    def read_outcome(self):
        while True:
            Utils.update_screen()
            
            # Check if the mobilize button is still available
            if Utils.find_and_touch('tactical_challenge/mobilise'):
                continue                
            # Check if the battle result screen is displayed
            if Utils.find('tactical_challenge/battle_result'):
                outcome = Utils.find_word('lose', self.region['outcome'])
                
                if outcome[0]:
                    Logger.log_msg('Result Battle: Lose')
                    self.loses += 1
                else:
                    Logger.log_msg('Result Battle: Win')
                    self.wins += 1

                GoTo.sub_campaign('tactical_challenge')
                break

        while True:
            # Check if the "New Best Season" message is displayed
            if Utils.find('tactical_challenge/best'):
                Logger.log_success('New Best Season Scored!')

            GoTo.sub_campaign('tactical_challenge')
            break
