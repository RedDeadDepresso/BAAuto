from util.logger import Logger
from util.utils import Utils, GoTo

class ClaimRewardsModule(object):
    def __init__(self, config):
        """Initializes the Claim Rewards module.

        Args:
            config (Config): BAAuto Config instance
        """
        self.enabled = True
        self.config = config

    def claim_rewards_logic_wrapper(self):
        if self.config.claim_rewards['club']:
            GoTo.sub_home('club')
        # Check if there are tasks to claim rewards from
        if self.config.claim_rewards['tasks']:
            # Navigate to the tasks section
            GoTo.sub_home('tasks')
            
            while True:
                Utils.update_screen()
                
                # Check if the "Claim All" button is available in tasks
                if Utils.find('claim_rewards/tasks_claim_all', color=True):
                    Utils.touch(1150, 670)  # Touch the "Claim All" button
                    GoTo.sub_home('tasks')  # Return to the tasks section
                    continue
                
                # Check if individual task rewards can be claimed
                if Utils.find('claim_rewards/claim', color=True):
                    Utils.touch(970, 675)  # Touch the individual task reward
                    GoTo.sub_home('tasks')  # Return to the tasks section
                    continue
                
                break  # Exit the loop if no more rewards can be claimed in tasks

        # Check if there are rewards to claim from the mailbox
        if self.config.claim_rewards['mailbox']:
            # Navigate to the club and then the mailbox
            GoTo.sub_home('mailbox')
            
            while True:
                Utils.update_screen()
                
                # Check if the "Claim All" button is available in the mailbox
                if Utils.find('claim_rewards/mailbox_claim_all', color=True):
                    Utils.touch(1150, 670)  # Touch the "Claim All" button
                    GoTo.sub_home('mailbox')  # Return to the mailbox
                    continue
                
                break  # Exit the loop if no more rewards can be claimed in the mailbox
        
        # Return to the home screen and reset reward claim flags
        GoTo.home()