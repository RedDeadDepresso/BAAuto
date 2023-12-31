from util.logger import Logger
from util.utils import GoTo, Region, Utils


class BountyModule(object):
    def __init__(self, config):
        """Initializes the Bounty module.

        Args:
            config (Config): BAAuto Config instance
        """
        self.enabled = True
        self.config = config
        
        # Define the stages and their corresponding configuration settings
        self.stage = {
            'overpass': self.config.bounty['overpass'],
            'desert_railroad': self.config.bounty['desert_railroad'],
            'classroom': self.config.bounty['classroom']
        }

        # Define regions for various elements on the screen
        self.region = {
            'tickets': None,
            'overpass': (800,200),
            'desert_railroad': (800,310),
            'classroom': (800, 410),
            'stage_list': Region(677, 132, 747, 678)
        }
        
    def determine_tickets_region(self):
        if Utils.assets == 'EN':
            self.region['tickets'] = Region(225, 75, 45, 45)
        elif Utils.assets == 'CN':
            self.region['tickets'] = Region(155,80, 50, 40)

    def bounty_logic_wrapper(self):
        # Navigate to the Bounty campaign
        GoTo.sub_campaign('bounty')

        # Read available locations from tickets and create a queue
        locations_queue = {k:v for k,v in self.stage.items() if v["run_times"] != 0}
        if locations_queue == {}:
            Logger.log_warning = "Bounty was enabled but all locations run times were set to 0. Unable to proceed."
            return
        self.determine_tickets_region()
        if Utils.scan(self.region["tickets"],resize=True)[0]["text"].strip() == "0/6":
            Logger.log_warning("Not enough tickets to run bounty.")
            return
        # Loop through the locations queue
        for entry in locations_queue:
            while Utils.find('goto/bounty'):
                Utils.touch(*self.region[entry])
                Utils.update_screen()

            # Find the region for the current stage
            stage_region = Utils.find_stage(self.stage[entry]["stage"])

            if stage_region:
                # Find and touch the "Enter" button for the stage
                button = Utils.find_button('farming/small_enter', stage_region, self.region['stage_list'])
                if button:
                    while True:
                        Utils.wait_update_screen(1)
                        if not Utils.find('farming/sweep'):
                            Utils.touch_randomly(button)
                            continue
                        outcome = Utils.sweep(locations_queue[entry]["run_times"])  # Perform the sweep action
                        if outcome[0] == "incomplete":
                            if outcome[1] == 0:
                                Logger.log_warning("Not enough tickets to complete sweep")
                            else:
                                Logger.log_warning(f'Ran out of tickets but enough to complete stage {outcome[1]} times instead of {locations_queue[entry]["run_times"]}')
                            return
                        break
                else:
                    Logger.log_error(f'{entry.capitalize()}-{self.stage[entry]["stage"]} not unlocked')
            while not Utils.find("goto/bounty", color=True):
                Utils.touch(55,40)
                Utils.wait_update_screen(1)
