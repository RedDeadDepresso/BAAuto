from util.logger import Logger
from util.utils import Utils, Region, GoTo
from tqdm import tqdm

class CafeModule(object):
    def __init__(self, config):
        """Initializes the Cafe module.

        Args:
            config (Config): BAAuto Config instance
        """
        self.enabled = True
        self.config = config
        
        # Define regions for various elements on the screen
        self.region = {
            'invite': Region(800, 620, 55, 70),
            'momotalk': Region(410, 187, 290, 413),
        }    

    def cafe_logic_wrapper(self):
        # Navigate to the Cafe screen
        GoTo.sub_home('cafe')
        Utils.update_screen()
        
        # Invite a student if the configuration allows and a student is available
        if self.config.cafe['invite_student'] and Utils.find("cafe/available"):
            self.find_student()

        # Tap on students if the configuration allows
        if self.config.cafe['tap_students']:
            # Define ranges for tapping students in a grid
            y_range = range(140, 543, 50)
            x_range = range(0, 1365, 50)
            total_iterations = len(y_range) * len(x_range)
            
            # Create a progress bar for tapping students
            progress_bar = tqdm(total=total_iterations, unit="taps", colour='cyan', desc='Tapping Students')
            
            # Loop through the grid and tap on students
            for y in y_range:
                for x in x_range:
                    Utils.touch(x, y)
                    progress_bar.update(1)  # Increment the progress bar

        # Claim earnings if the configuration allows
        if self.config.cafe['claim_earnings']:
            while True:
                Utils.wait_update_screen(1)
                if not Utils.find("cafe/earnings"):
                    Utils.touch(1158, 647)  # Touch the earnings button
                else:
                    Utils.touch(640, 520)  # Touch the claim button
                    break
        
        # Return to the home screen
        GoTo.home()

    def find_student(self):
        found = False
        last_student = ""
        if self.config.cafe["student_name"].replace(" ", "") == "":
            Logger.log_warning("Inviting student is turned on but student name is empty. Unable to proceed.")
            return
        Logger.log_info(f'Inviting student: {self.config.cafe["student_name"]}')
        
        # Wait for the momotalk screen to appear
        while not Utils.find("cafe/momotalk"):
            Utils.touch_randomly(self.region['invite'])
            Utils.wait_update_screen(1)
        
        # Continue searching for the student until found or no more students are available
        Utils.init_ocr_mode()
        while not found:
            Utils.wait_update_screen(1)
            
            # Search for the student's name in the momotalk region
            result = Utils.find_word(self.config.cafe['student_name'], self.region['momotalk'])
            
            if result[0]:
                Logger.log_success("Student found!")
                found = True
                
                # Find and touch the invite button for the student
                button = Utils.find_button('cafe/invite', result[1], self.region['momotalk'])
                
                if button:
                    while True:
                        Utils.wait_update_screen(1)
                        
                        # Confirm the invitation
                        if Utils.find_and_touch('cafe/confirm'):
                            break
                        Utils.touch_randomly(button)
                else:
                    Logger.log_error('Error: Could not find button')
            elif last_student == result[1]:
                Logger.log_error('Student not found. Please check spelling.')
                break
            else:
                last_student = result[1] if not result[1].isdigit() else last_student
                Utils.swipe(600, 500, 600, 200)  # Swipe to scroll the momotalk region
        Utils.init_ocr_mode(EN=True)
