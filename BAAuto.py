import tkinter as tk
from PIL import Image
import json
from subprocess import Popen, PIPE, STDOUT
import threading
import customtkinter
import sys
from gui import *
import random
import ctypes
import re

class Config:
    def __init__(self, linker, config_file):
        self.linker = linker
        self.config_file = config_file
        self.config_data = self.read()
        self.linker.widgets = self.set_values_to_none(self.config_data)
        linker.config = self

    def read(self):
        # Read the JSON file
        try:
            with open(self.config_file, 'r') as json_file:
                config_data = json.load(json_file)
            return config_data
        except FileNotFoundError:
            print(f"Config file '{self.config_file}' not found.")
            sys.exit(1)
        except json.JSONDecodeError:
            print(f"Invalid JSON format in '{self.config_file}'.")
            sys.exit(1)

    def set_values_to_none(self, input_dict):
        result = {}
        for key, value in input_dict.items():
            if isinstance(value, dict):
                result[key] = self.set_values_to_none(value)
            else:
                result[key] = None
        return result
    
    def load_config(self, widgets=None, config_data=None):
        if widgets == None:
            widgets = self.linker.widgets
            config_data = self.config_data
        for key in widgets:
            if isinstance(widgets[key], dict) and isinstance(config_data[key], dict):
                self.load_config(widgets[key], config_data[key])
            else:
                if widgets[key] is not None:
                    if isinstance(widgets[key], customtkinter.CTkCheckBox):
                        if config_data[key] == True:
                            widgets[key].select()
                        else:
                            widgets[key].deselect()
                    elif isinstance(widgets[key], customtkinter.CTkEntry):
                        widgets[key].insert(0, config_data[key])
                    else:                    
                        widgets[key].set(config_data[key])

    def save_to_json(self, list_keys):
        widget = self.linker.widgets
        data = self.config_data
        for i in list_keys[:-1]:
            widget = widget[i]
            data = data[i]
        widget = widget[list_keys[-1]] 
        value = widget.get()
        if isinstance(widget, customtkinter.CTkCheckBox):
            value = True if value==1 else False
        data[list_keys[-1]] = value
        self.save_file()

    def save_file(self):
        with open("config.json", "w") as config_file:
            json.dump(self.config_data, config_file, indent=2)
    
class Linker:
    def __init__(self):
        self.capitalise = lambda word: " ".join(x.title() for x in word.split("_"))        
        self.config = None
        self.widgets = {}
        self.modules_dictionary = {}
        self.start_button = None
        self.log_textbox = None
        self.p = None

    def switch_student_list(self):
        server = self.config.config_data["login"]["server"]
        with open(f"gui/student_list/{server}.json", "r") as f:
            student_list = json.load(f)
        cafe_frame = self.modules_dictionary["cafe"]["frame"]
        cafe_frame.student_dropdown.configure(values=student_list)
        
    def start_stop(self):
        if hasattr(self, 'p') and self.p is not None:
            # If process is running, terminate it
            self.p.terminate()
            self.p = None
            self.start_button.configure(text="Start", fg_color = ['#3B8ED0', '#1F6AA5'])
            self.switch_queue_state("normal")

        else:
            # If process is not running, start it
            color = self.start_button.cget("fg_color")
            print(color)
            self.p = Popen(['python', 'script.py'], stdout=PIPE, stderr=STDOUT)
            threading.Thread(target=self.read_output).start()
            self.start_button.configure(text="Stop", fg_color = "crimson")
            self.switch_queue_state("disabled")

    def read_output(self):
        for line in iter(self.p.stdout.readline, b''):
            line = line.decode("utf-8")  # Decode the bytes to a string
            # Check if line contains any log level
            for level, color in self.log_textbox.log_level_colors.items():
                if level in line:
                    # Display output in text box with color
                    self.log_textbox.log_textbox.configure(state="normal")           
                    self.log_textbox.log_textbox.insert("end", line, level)
                    self.log_textbox.log_textbox.configure(state="disabled")
                    break
            if self.log_textbox.autoscroll_enabled:
                self.log_textbox.log_textbox.yview_moveto(1.0)
        # If process ends, change button text to 'Start'
        self.start_button.configure(text="Start", fg_color = ['#3B8ED0', '#1F6AA5'])
        self.switch_queue_state("normal")
        self.p = None

    def switch_queue_state(self, state):
        farming_frame = self.modules_dictionary["farming"]["frame"]
        for button in farming_frame.queue_buttons:
            button.configure(state=state)
        self.update_queue()
        for frame in farming_frame.queue_frames:
            for widget in frame.winfo_children():
                widget.configure(state=state)

    def update_queue(self):
        farming_frame = self.modules_dictionary["farming"]["frame"]
        farming_frame.clear_frames(queue=True)
        new_config_data = self.config.read()
        self.config.config_data["farming"]['mission']['queue'] = new_config_data["farming"]['mission']['queue']
        for entry in self.config.config_data["farming"]['mission']['queue']:
            farming_frame.add_frame(entry, queue=True)

class Sidebar(customtkinter.CTkFrame):
    def __init__(self, master, linker, config, **kwargs):
        self.master = master
        self.linker = linker
        self.config = config
        super().__init__(master=self.master, **kwargs)
        karin_logo = customtkinter.CTkImage(light_image=Image.open("gui/icons/karin.png"), size=(132,132))
        karin_logo_label = customtkinter.CTkLabel(self, image=karin_logo, text="")
        karin_logo_label.grid(row=0, column=0, padx=(50,0), pady=20, sticky="nsew")
        self.gear_on = customtkinter.CTkImage(Image.open("gui/icons/gear_on.png"), size=(50,38))
        self.gear_off = customtkinter.CTkImage(Image.open("gui/icons/gear_off.png"), size=(50,38))
        self.create_module_frames()
        self.create_all_button_frame()
        self.create_start_button()
        
    def create_module_frames(self):

        self.checkbox_frame = customtkinter.CTkFrame(self, fg_color="transparent", border_color="white", border_width=2)
        self.checkbox_frame.grid(row=1, column=0, columnspan=4, padx=10, pady=10, sticky="w")

        self.module_list = [["login", LoginFrame], ["cafe", CafeFrame], ["farming", FarmingFrame], ["claim_rewards", ClaimRewardsFrame]]               
        for index, sublist in enumerate(self.module_list):
            module = sublist[0]
            self.linker.modules_dictionary[module] = {}
            self.create_module_checkbox(module, index)
            self.create_module_button(module, index)
            frame = sublist[1](self.master, self.linker, self.config, fg_color="#262250") 
            self.linker.modules_dictionary[module]['frame'] = frame
        self.linker.modules_dictionary["login"]["button"].configure(image=self.gear_on)
        self.linker.modules_dictionary["login"]["checkbox"].configure(text_color="#53B9E9")   
        self.current_frame = self.linker.modules_dictionary["login"]["frame"]  # Update the current frame
        self.current_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

    def create_module_checkbox(self, module, i):
        self.linker.modules_dictionary[module]['checkbox'] = customtkinter.CTkCheckBox(
            self.checkbox_frame, text=self.linker.capitalise(module), text_color="#FFFFFF", font=("Inter", 16), command=lambda x=[module, "enabled"]: self.config.save_to_json(x))
        self.linker.modules_dictionary[module]['checkbox'].grid(row=i, column=0, columnspan=2,padx=20, pady=(10, 5), sticky="nw")
        self.linker.widgets[module]['enabled'] = self.linker.modules_dictionary[module]['checkbox']

    def create_module_button(self, module, i):
        self.linker.modules_dictionary[module]['button'] = customtkinter.CTkButton(
            self.checkbox_frame, width=50, image=self.gear_off, text="", fg_color="transparent", command=lambda x=module: self.display_settings(module))
        self.linker.modules_dictionary[module]['button'].grid(row=i, column=1, padx=(40,0), pady=(2,0), sticky="nw")        

    def create_all_button_frame(self):
        self.select_all_button = customtkinter.CTkButton(self.checkbox_frame, width=100, text="Select All", fg_color="#DC621D", font=("Inter",20), command=self.select_all)
        self.select_all_button.grid(row=4, column=0, padx=10, pady=(15,20), sticky="w")
        self.clear_all_button = customtkinter.CTkButton(self.checkbox_frame, width=100, text="Clear All", fg_color="#DC621D", font=("Inter",20), command=self.clear_all)
        self.clear_all_button.grid(row=4, column=1, padx=10, pady=(15,20), sticky="w")

    def create_start_button(self):
        self.start_button = customtkinter.CTkButton(self, text="Start", width=18-0, height=40, command=self.linker.start_stop, font=customtkinter.CTkFont(family="Inter", size=16))
        self.start_button.grid(row=2, column=0, padx=(35,0), pady=(25,0),  sticky="nsew")
        self.linker.start_button = self.start_button

    def select_all(self):
        for module in self.linker.modules_dictionary:
            if module != "momotalk":
                self.linker.modules_dictionary[module]["checkbox"].select()
                self.config.config_data[module]["enabled"] = True
        self.config.save_file()

    def clear_all(self):
        for module in self.linker.modules_dictionary:
            self.linker.modules_dictionary[module]["checkbox"].deselect()
            self.config.config_data[module]["enabled"] = False
        self.config.save_file()

    def display_settings(self, module):
        for key in self.linker.modules_dictionary:
            if key == module:
                self.linker.modules_dictionary[key]["button"].configure(image=self.gear_on)
                self.linker.modules_dictionary[key]["checkbox"].configure(text_color="#53B9E9")                
                self.current_frame.grid_remove()  # Hide the current frame
                self.current_frame = self.linker.modules_dictionary[key]["frame"]  # Update the current frame
                self.current_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
            else:
                self.linker.modules_dictionary[key]["button"].configure(image=self.gear_off)
                self.linker.modules_dictionary[key]["checkbox"].configure(text_color="#FFFFFF")  

class LoginFrame(customtkinter.CTkFrame):
    def __init__(self, master, linker, config, **kwargs):
        super().__init__(master, **kwargs)
        self.linker = linker
        self.config = config
        self.create_widgets()

    def create_widgets(self):
        self.login_settings_label = customtkinter.CTkLabel(self, text="Login Settings", font=customtkinter.CTkFont(family="Inter", size=30, weight="bold"))
        self.login_settings_label.grid(row=0, column=0, sticky="nw", padx=20, pady=20)

        self.create_network_widgets()
        self.create_screenshot_widgets()
        self.create_server_widgets()
        self.create_restart_attempts_widgets()

    def create_network_widgets(self):
        self.network_label = customtkinter.CTkLabel(self, text="Connection address:", font=customtkinter.CTkFont(family="Inter", size=20, weight="bold"))
        self.network_label.grid(row=1, column=0, padx=20, pady=(20, 10))

        self.network_entry = customtkinter.CTkEntry(self)
        self.network_entry.bind("<KeyRelease>", lambda event, x=["login", "network"]: self.config.save_to_json(x))
        self.network_entry.grid(row=2, column=0, padx=20, pady=(20, 10))

        self.linker.widgets["login"]["network"] = self.network_entry

    def create_screenshot_widgets(self):
        self.screenshot_label = customtkinter.CTkLabel(self, text="Screenshot mode:", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.screenshot_label.grid(row=3, column=0, padx=20, pady=(20, 10))

        self.screenshot_dropdown = customtkinter.CTkOptionMenu(self, values=["SCREENCAP_PNG", "SCREENCAP_RAW", "ASCREENCAP", "UIAUTOMATOR2"], command=lambda x, y=["login", "screenshot_mode"]: self.config.save_to_json(y))
        self.screenshot_dropdown.grid(row=4, column=0, padx=20, pady=(20, 10))

        self.linker.widgets["login"]["screenshot_mode"] = self.screenshot_dropdown

    def create_server_widgets(self):
        self.server_label = customtkinter.CTkLabel(self, text="Server:", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.server_label.grid(row=5, column=0, padx=20, pady=(20, 10))

        self.server_dropdown = customtkinter.CTkOptionMenu(self, values=["EN", "CN"], command=lambda x,y=["login","server"]: (self.config.save_to_json(y), self.linker.switch_student_list()))
        self.server_dropdown.grid(row=6, column=0, padx=20, pady=(20, 10))

        self.linker.widgets["login"]["server"] = self.server_dropdown

    def create_restart_attempts_widgets(self):
        self.restart_attempts_label = customtkinter.CTkLabel(self, text="Restart attempts", font=customtkinter.CTkFont(size=20, weight="bold", underline=True))
        self.restart_attempts_label.grid(row=7, column=0, padx=20, pady=(20, 10))
        self.restart_attempts_tootltip = CTkToolTip(self.restart_attempts_label, message="Sets the number of restart attempts allowed to the script. Restart attempts are triggered when the game crashes or freezes.", wraplength=400)

        self.restart_attempts_spinbox = IntegerSpinbox(self, step_size=1, min_value=0, command=lambda x=["login", "restart_attempts"]:self.config.save_to_json(x))
        self.restart_attempts_spinbox.entry.bind("<KeyRelease>", lambda event, x=["login", "restart_attempts"]: self.config.save_to_json(x))
        self.restart_attempts_spinbox.grid(row=8, column=0, padx=20, pady=(20, 10))

        self.linker.widgets["login"]["restart_attempts"] = self.restart_attempts_spinbox

class CafeFrame(customtkinter.CTkFrame):
    def __init__(self, master, linker, config, **kwargs):
        super().__init__(master, **kwargs)
        self.linker = linker
        self.config = config
        self.create_widgets()

    def create_widgets(self):
        self.create_cafe_settings_label()
        self.create_invite_student_widgets()
        self.create_tap_students_widgets()
        self.create_claim_earnings_widgets()

    def create_cafe_settings_label(self):
        self.cafe_settings_label = customtkinter.CTkLabel(self, text="Cafe Settings", font=customtkinter.CTkFont(family="Inter", size=30, weight="bold"))
        self.cafe_settings_label.grid(row=0, column=0, sticky="nw", padx=20, pady=20)

    def create_invite_student_widgets(self):
        self.invite_checkbox = customtkinter.CTkCheckBox(self, text="Invite student", font=customtkinter.CTkFont(family="Inter", size=20), command=lambda x=["cafe", "invite_student"]: self.config.save_to_json(x))
        self.invite_checkbox.grid(row=1, column=0, pady=(20, 0), padx=20, sticky="nw")

        self.student_entry = customtkinter.CTkComboBox(self, width=180)
        self.student_entry.bind("<KeyRelease>", lambda event, x=["cafe", "student_name"]: (self.config.save_to_json(x)))
        self.student_entry.grid(row=1, column=1, padx=20, pady=(20, 0))

        save_student = lambda name: self.student_entry.set(name)
        server = self.config.config_data["login"]["server"]
        with open(f"gui/student_list/{server}.json", "r") as f:
            student_list = json.load(f)
        self.student_dropdown = CTkScrollableDropdown(self.student_entry, values=student_list, width=180, height=550, autocomplete=True, command=lambda choice, x=["cafe", "student_name"]: (save_student(choice), self.config.save_to_json(x)))
        self.linker.widgets["cafe"]["invite_student"] = self.invite_checkbox
        self.linker.widgets["cafe"]["student_name"] = self.student_entry

    def create_tap_students_widgets(self):
        self.tap_checkbox = customtkinter.CTkCheckBox(self, text="Tap Students", font=customtkinter.CTkFont(family="Inter", size=20), command=lambda x=["cafe", "tap_students"]: self.config.save_to_json(x))
        self.tap_checkbox.grid(row=2, column=0, pady=(20,0), padx=20, sticky="nw")
        self.linker.widgets["cafe"]["tap_students"] = self.tap_checkbox


    def create_claim_earnings_widgets(self):
        self.claim_checkbox = customtkinter.CTkCheckBox(self, text="Claim Earnings", font=customtkinter.CTkFont(family="Inter", size=20), command=lambda x=["cafe", "claim_earnings"]: self.config.save_to_json(x))
        self.claim_checkbox.grid(row=3, column=0, pady=(20, 0), padx=20, sticky="nw")
        self.linker.widgets["cafe"]["claim_earnings"] = self.claim_checkbox

class FarmingFrame(customtkinter.CTkScrollableFrame):
    def __init__(self, master, linker, config, **kwargs):
        super().__init__(master=master, **kwargs)
        self.linker = linker
        self.config = config
        self.create_widgets()
        # Load Template Data
        self.load_template_data()
        # Load queue Data
        self.load_queue_data()


    def create_widgets(self):
        self.farming_settings_label = customtkinter.CTkLabel(self, text="Farming Settings", font=customtkinter.CTkFont(family="Inter", size=30, weight="bold"))
        self.farming_settings_label.grid(row=0, column=0, sticky="nw", padx=20, pady=20)

        self.create_bounty_widgets()
        self.create_scrimmage_widgets()
        self.create_tactical_challenge_widgets()
        self.create_mission_commissions_widgets()

    def create_bounty_widgets(self):
        self.bounty_checkbox = customtkinter.CTkCheckBox(self, text="Bounty", command=lambda x=["farming", "bounty", "enabled"]: self.config.save_to_json(x), font=customtkinter.CTkFont(family="Inter", size=20, weight="bold"))
        self.bounty_checkbox.grid(row=1, column=0, sticky="nw", padx=20, pady=20)   
        self.linker.widgets["farming"]["bounty"]["enabled"] = self.bounty_checkbox
        values = ["0" + str(x) for x in range(1, 10)]

        for index, element in enumerate(["overpass", "desert_railroad", "classroom"]):
            label = customtkinter.CTkLabel(self, text=self.linker.capitalise(element), font=customtkinter.CTkFont(family="Inter", size=16))
            label.grid(row=index + 2, column=0, sticky="nw", padx=80)

            option_menu = customtkinter.CTkOptionMenu(self, width=80, values=values, command=lambda x, y=["farming", "bounty", element, "stage"]: self.config.save_to_json(y), font=customtkinter.CTkFont(family="Inter", size=16))
            option_menu.grid(row=index + 2, column=1)
            self.linker.widgets["farming"]["bounty"][element]["stage"] = option_menu

            spinbox = IntegerSpinbox(self, step_size=1, min_value=0, command=lambda x=["farming", "bounty", element, "run_times"]:self.config.save_to_json(x))
            spinbox.entry.bind("<KeyRelease>", lambda event, x=["farming", "bounty", element, "run_times"]: self.config.save_to_json(x))
            spinbox.grid(row=index + 2, column=2)
            self.linker.widgets["farming"]["bounty"][element]["run_times"] = spinbox

    def create_scrimmage_widgets(self):
        self.scrimmage_checkbox = customtkinter.CTkCheckBox(self, text="Scrimmage", command=lambda x=["farming", "scrimmage", "enabled"]: self.config.save_to_json(x), font=customtkinter.CTkFont(family="Inter", size=20, weight="bold"))
        self.scrimmage_checkbox.grid(row=5, column=0, sticky="nw", padx=20, pady=20)
        self.linker.widgets["farming"]["scrimmage"]["enabled"] = self.scrimmage_checkbox

        values = ["0" + str(x) for x in range(1, 10)]

        for index, element in enumerate(["trinity", "gehenna", "millennium"]):
            label = customtkinter.CTkLabel(self, text=self.linker.capitalise(element), font=customtkinter.CTkFont(family="Inter", size=16))
            label.grid(row=index + 6, column=0, sticky="nw", padx=80)

            option_menu = customtkinter.CTkOptionMenu(self, width=80, values=values[:5], command=lambda x, y=["farming", "scrimmage", element, "stage"]: self.config.save_to_json(y))
            option_menu.grid(row=index + 6, column=1)
            self.linker.widgets["farming"]["scrimmage"][element]["stage"] = option_menu

            spinbox = IntegerSpinbox(self, step_size=1, min_value=0, command=lambda x=["farming", "scrimmage", element, "run_times"]: self.config.save_to_json(x))
            spinbox.entry.bind("<KeyRelease>", lambda event, x=["farming", "scrimmage", element, "run_times"]: self.config.save_to_json(x))
            spinbox.grid(row=index + 6, column=2)
            self.linker.widgets["farming"]["scrimmage"][element]["run_times"] = spinbox

    def create_tactical_challenge_widgets(self):
        self.tactical_checkbox = customtkinter.CTkCheckBox(self, text="Tactical Challenge", command=lambda x=["farming", "tactical_challenge", "enabled"]: self.config.save_to_json(x), font=customtkinter.CTkFont(family="Inter", size=20, weight="bold"))
        self.tactical_checkbox.grid(row=9, column=0, sticky="nw", padx=20, pady=20)
        self.linker.widgets["farming"]["tactical_challenge"]["enabled"] = self.tactical_checkbox

        self.rank_label = customtkinter.CTkLabel(self, text="Rank", font=customtkinter.CTkFont(family="Inter", size=16))
        self.rank_label.grid(row=10, column=0, sticky="nw", padx=80)

        self.rank_optionmenu = customtkinter.CTkOptionMenu(self, values=["highest", "middle", "lowest"], command=lambda x, y=["farming", "tactical_challenge", "rank"]: self.config.save_to_json(y))
        self.rank_optionmenu.grid(row=10, column=1)
        self.linker.widgets["farming"]["tactical_challenge"]["rank"] = self.rank_optionmenu


    def create_mission_commissions_widgets(self):
        # Create Mission/Commissions/Event Checkbox
        self.create_mission_commissions_checkbox()

        # Create Reset Daily Widgets
        self.create_reset_daily_widgets()

        # Create Recharge AP and Event Checkboxes
        self.create_recharge_and_event_checkboxes()

        # Create Preferred Template Selection
        self.create_preferred_template_selection()

        # Create Mission Tabview with Template and Queue Tabs
        self.create_mission_tabview()

        # Create Top-Level Window for Template Editing
        self.create_template_queue_editor()

        # Create Template Frame and Queue Frame
        self.create_template_and_queue_frames()

        # Create Lists to Store Frame Widgets
        self.create_frame_lists()

        # Initialize Preferred Template and Templates List
        self.initialize_preferred_template()

        # Create OptionMenu for Selecting a Template
        self.create_template_option_menu()

        # Create Delete Template Button
        self.create_delete_template_button()

    # Helper method to create Mission/Commissions/Event Checkbox
    def create_mission_commissions_checkbox(self):
        self.mission_commissions_checkbox = customtkinter.CTkCheckBox(self, text="Mission/\nCommissions/Event", width=60, font=customtkinter.CTkFont(family="Inter", size=20, weight="bold"), command=lambda x=["farming", "mission", "enabled"]: self.config.save_to_json(x))
        self.mission_commissions_checkbox.grid(row=11, column=0, sticky="nw", padx=20, pady=20)
        self.linker.widgets["farming"]["mission"]["enabled"] = self.mission_commissions_checkbox

    # Helper method to create Reset Daily Widgets
    def create_reset_daily_widgets(self):
        self.reset_daily = customtkinter.CTkCheckBox(self, text="Reset Daily", font=customtkinter.CTkFont(family="Inter", size=16, underline=True))
        self.reset_daily.grid(row=12, column=0, sticky="nw", padx=80)
        self.reset_daily_tooltip = CTkToolTip(self.reset_daily, wraplength=400,
                                              message="If enabled and if current time >= reset time,\
                                                the queue will automatically be cleared and repopulated with preferred template stages. Only activated once a day.")

        self.reset_daily_sub_label = customtkinter.CTkLabel(self, text="hh/mm/ss", font=customtkinter.CTkFont(family="Inter", size=12))
        self.reset_daily_sub_label.grid(row=13, column=0, padx=80)

        self.reset_time = TimeEntry(self)
        self.reset_time.grid(row=12, column=1)
        self.reset_time.hour_entry.bind("<KeyRelease>", lambda event, x=["farming", "mission", "reset_time"]: self.config.save_to_json(x))
        self.reset_time.minute_entry.bind("<KeyRelease>", lambda event, x=["farming", "reset_time"]: self.config.save_to_json(x))
        self.reset_time.second_entry.bind("<KeyRelease>", lambda event, x=["farming", "reset_time"]: self.config.save_to_json(x))

        self.linker.widgets["farming"]["mission"]["reset_daily"] = self.reset_daily
        self.linker.widgets["farming"]["mission"]["reset_time"] = self.reset_time

    # Helper method to create Recharge AP and Event Checkboxes
    def create_recharge_and_event_checkboxes(self):
        self.recharge_checkbox = customtkinter.CTkCheckBox(self, text="Recharge AP", command=lambda x=["farming", "mission", "recharge_ap"]: self.config.save_to_json(x), font=customtkinter.CTkFont(family="Inter", size=16, underline=True))
        self.recharge_checkbox.grid(row=14, column=0, sticky="nw", padx=80, pady=20)
        self.linker.widgets["farming"]["mission"]["recharge_ap"] = self.recharge_checkbox
        self.recharge_tooltip = CTkToolTip(self.recharge_checkbox, wraplength=400,
                                              message="When enabled, recharge AP when low via cafe earnings and mailbox, regardless of whether they are enabled in their respective sections.")
        self.event_checkbox = customtkinter.CTkCheckBox(self, text="Sweep Event Stages", command=lambda x=["farming", "mission", "event"]: self.config.save_to_json(x), font=customtkinter.CTkFont(family="Inter", size=16, underline=True))
        self.event_tooltip = CTkToolTip(self.event_checkbox, wraplength=400, message="When enabled, the script will sweep event stages. Otherwise, it will ignore them.")
        self.event_checkbox.grid(row=15, column=0, sticky="nw", padx=80)
        self.linker.widgets["farming"]["mission"]["event"] = self.event_checkbox

    # Helper method to create Preferred Template Selection
    def create_preferred_template_selection(self):
        self.templates = self.config.config_data["farming"]["mission"]["templates"]
        self.templates_list = list(self.templates.keys())

        self.preferred_template_label = customtkinter.CTkLabel(self, text="Preferred Template:", font=customtkinter.CTkFont(family="Inter", size=16, underline=True))
        self.preferred_template_label.grid(row=16, column=0, pady=20)
        self.preferred_template_tooltip = CTkToolTip(self.preferred_template_label, wraplength=400,
                                              message="The template from which to repopulate the queue when it is empty or reset daily is activated")
        self.preferred_template_optionmenu = customtkinter.CTkOptionMenu(self, values=self.templates_list, command=lambda x, y=["farming", "mission", "preferred_template"]: self.config.save_to_json(y))
        self.preferred_template_optionmenu.grid(row=16, column=1, pady=20)
        self.linker.widgets["farming"]["mission"]["preferred_template"] = self.preferred_template_optionmenu

    # Helper method to create Mission Tabview with Template and Queue Tabs
    def create_mission_tabview(self):
        self.mission_tabview = customtkinter.CTkTabview(self, height=500)
        self.mission_tabview.grid(row=17, column=0, columnspan=3, padx=20)

        self.tab_template = self.mission_tabview.add('Template')
        self.tab_queue = self.mission_tabview.add('Queue')

    # Helper method to create Template Queue Editor 
    def create_template_queue_editor(self):
        self.queue_buttons = []

        for i in [self.tab_queue, self.tab_template]:
            queue = True if i == self.tab_queue else False

            self.template_labels = customtkinter.CTkFrame(i)
            self.template_labels.grid(row=0, column=0, sticky="ew")

            self.mode_label = customtkinter.CTkLabel(self.template_labels, text="Mode:", font=customtkinter.CTkFont(underline=True))
            self.mode_tooltip = CTkToolTip(self.mode_label, message="N:Mission Normal\nH:Mission Hard\nE:Event Quest\nBD:Base Defense\nIR:Item Retrieval\n")
            self.mode_label.grid(row=1, column=0, padx=(130, 0), pady=5)

            self.stage_label = customtkinter.CTkLabel(self.template_labels, text="Stage:", font=customtkinter.CTkFont(underline=True))
            self.stage_tooltip = CTkToolTip(self.stage_label, message="Valid format for Mission: 1-1\nValid format for Commissions/Event: 01")
            self.stage_label.grid(row=1, column=1, padx=(40, 20), pady=5)

            self.run_times_label = customtkinter.CTkLabel(self.template_labels, text="Number of Sweeps:", font=customtkinter.CTkFont(underline=True))
            self.run_times_tooltip = CTkToolTip(self.run_times_label, message="How many times do you want to sweep the stage?")
            self.run_times_label.grid(row=1, column=2, pady=5)

            self.template_buttons_frame = customtkinter.CTkFrame(i)
            self.template_buttons_frame.grid(row=3, column=0)

            self.add_button = customtkinter.CTkButton(self.template_buttons_frame , text="Add", command=lambda queue=queue: self.add_frame(queue=queue))
            self.add_button.grid(row=0, column=0, padx=5, pady=5)

            # Clear button to clear all frames
            self.clear_button = customtkinter.CTkButton(self.template_buttons_frame, text="Clear All", command=lambda queue=queue: self.clear_frames(queue=queue), fg_color="crimson")
            self.clear_button.grid(row=0, column=1, padx=5, pady=5)

            # Save button to save data
            self.save_button = customtkinter.CTkButton(self.template_buttons_frame, text="Save", command=lambda queue=queue: self.save_data(queue=queue), fg_color="#DC621D")
            self.save_button.grid(row=0, column=2, padx=5, pady=5)
            if queue:
                self.queue_buttons = [self.add_button, self.clear_button, self.save_button]

    # Helper method to create Template Frame and Queue Frame
    def create_template_and_queue_frames(self):
        self.template_frame = customtkinter.CTkScrollableFrame(self.tab_template, width=400, height=350)
        self.template_frame.grid(row=1, column=0, sticky="nsew")
        
        self.queue_frame = customtkinter.CTkScrollableFrame(self.tab_queue, width=400, height=350)
        self.queue_frame.grid(row=1, column=0, sticky="nsew")

    # Helper method to create Lists to Store Frame Widgets
    def create_frame_lists(self):
        self.template_frames = []
        self.queue_frames = []

    # Helper method to initialize Preferred Template and Templates List
    def initialize_preferred_template(self):
        self.preferred_template = self.config.config_data["farming"]["mission"]["preferred_template"]
        self.templates_list.append("Add New Template")

    # Helper method to create OptionMenu for Selecting a Template
    def create_template_option_menu(self):
        self.selected_template = tk.StringVar(self.template_frame)
        self.selected_template.set(self.preferred_template)  # Set the initial value to the preferred template

        self.template_optionmenu = customtkinter.CTkOptionMenu(self.template_labels, values=self.templates_list, variable=self.selected_template, command=lambda *args: self.load_template_data())
        self.template_optionmenu.grid(row=0, column=0, padx=5, pady=5)

    # Helper method to create Delete Template Button
    def create_delete_template_button(self):
        self.delete_template_button = customtkinter.CTkButton(self.template_labels, width=40, text="Delete", command=self.delete_template)
        self.delete_template_button.grid(row=0, column=1)

    # Helper method to add frames from Configuration Data
    def load_queue_data(self):
        for entry in self.config.config_data["farming"]['mission']['queue']:
            self.add_frame(entry, queue=True)

    # Function to load template data into frames
    def load_template_data(self):
        selected = self.selected_template.get()
        if selected == "Add New Template":
            dialog = customtkinter.CTkInputDialog(text="Type in new template name:", title="Template Name")
            template_name = dialog.get_input()
            if template_name in ["",None]:
                self.template_optionmenu.set(self.previous_selected)
                return
            elif template_name == "Add New Template":
                self.open_toplevel()
                return
            else:
                self.templates[template_name] = []
                self.templates_list.insert(-1, template_name)
                selected = template_name
                self.template_optionmenu.set(selected)
                self.template_optionmenu.configure(values=self.templates_list)
                self.preferred_template_optionmenu.configure(values=self.templates_list)
        self.clear_frames()
        for entry in self.templates[selected]:
            self.add_frame(entry)
        self.previous_selected  = selected

    def delete_template(self):
        msg = CTkMessagebox(title="Template Deletetion", message=f"Are you sure you want to delete Template {self.previous_selected}?",
                        icon="question", option_1="No", option_2="Yes")
        response = msg.get()
        if response=="Yes":
            if self.templates != 1:
                del self.templates[self.previous_selected]
                self.templates_list = list(self.templates.keys())
                self.preferred_template_optionmenu.configure(values=self.templates_list)
                if self.preferred_template == self.previous_selected:
                    self.preferred_template = random.choice(self.templates_list)
                self.config.config_data["farming"]["mission"]["preferred_template"] = self.preferred_template
                self.selected_template.set(self.preferred_template)  # Set the initial value to the preferred template
                self.preferred_template_optionmenu.set(self.preferred_template)
                self.load_template_data()
                self.config.save_file()
                self.templates_list.append("Add New Template")
                self.template_optionmenu.configure(values=self.templates_list)
                self.template_optionmenu.set(self.preferred_template)
            else:
                CTkMessagebox(title="Error", message="At least one template must exist!!!", icon="cancel")
        return

# Function to add a frame with widgets
    def add_frame(self, inner_list=None, queue=False):
        frames = self.queue_frames if queue else self.template_frames
        parent_frame = self.queue_frame if queue else self.template_frame
        row_index = len(frames) + 1  # Calculate the row for the new frame
        # Create a frame
        frame = customtkinter.CTkFrame(parent_frame)
        frame.grid(row=row_index, column=0, columnspan=4, padx=10, pady=10, sticky="w")
        frames.append(frame)
        # "Up" button to move the frame up
        up_button = customtkinter.CTkButton(frame, text="Up", width=5, command=lambda f=frame, queue=queue: self.move_frame_up(f, queue))
        up_button.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        # "Down" button to move the frame down
        down_button = customtkinter.CTkButton(frame, text="Down", width=5, command=lambda f=frame, queue=queue: self.move_frame_down(f, queue))
        down_button.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        # Dropdown menu for mode
        mode_optionmenu = customtkinter.CTkOptionMenu(frame, width=60, values=["N", "H", "E", "BD", "IR"])
        mode_optionmenu.set(inner_list[0] if inner_list else "N")
        mode_optionmenu.grid(row=0, column=2, padx=5, pady=5, sticky="w")
        # Entry widget for stage
        stage_var = tk.StringVar(value=inner_list[1] if inner_list else "")
        stage_entry = customtkinter.CTkEntry(frame, width=60, textvariable=stage_var)
        stage_entry.grid(row=0, column=3, padx=5, pady=5, sticky="w")
        mode_optionmenu.configure(command=lambda x=mode_optionmenu, y=stage_entry : self.check_entry(x,y))
        stage_entry.bind('<KeyRelease>', command=lambda event, x=mode_optionmenu, y=stage_entry : self.check_entry(x,y))
        self.check_entry(mode_optionmenu, stage_entry)
        # Entry widget for run times (only accepts numbers)
        run_times_spinbox = IntegerSpinbox(frame, step_size=1, min_value=1)
        run_times_spinbox.set(value=inner_list[2] if inner_list else 1)
        run_times_spinbox.grid(row=0, column=4, padx=5, pady=5, sticky="w")

        # Delete button to delete the frame
        delete_button = customtkinter.CTkButton(frame, text="Delete", width=5, command=lambda f=frame, queue=queue: self.delete_frame(f, queue))
        delete_button.grid(row=0, column=5, padx=5, pady=5, sticky="w")

    # Function to clear all frames
    def clear_frames(self, queue=False):
        frames = self.queue_frames if queue else self.template_frames
        for frame in frames:
            frame.destroy()
        frames.clear()

    # Function to save frames as data
    def save_data(self, queue=False):
        entries = []
        frames = self.queue_frames if queue else self.template_frames
        for frame in frames:
            mode_optionmenu = frame.winfo_children()[2]
            stage_entry = frame.winfo_children()[3]
            if not self.check_entry(mode_optionmenu, stage_entry):
                CTkMessagebox(title="Error", message="Configuration not saved. Some entries are incomplete or have incorect input.", icon="cancel")
                return
            mode = frame.winfo_children()[2].get()
            stage = frame.winfo_children()[3].get()
            run_times = frame.winfo_children()[4].get()
            entries.append([mode, stage, int(run_times)])
        if queue:
            self.config.config_data["farming"]['mission']['queue'] = entries
        else:
            selected = self.selected_template.get()
            self.templates[selected] = entries
        self.config.save_file()

    def check_entry(self, mode_dropdown, stage_entry):
        mode = mode_dropdown.get()
        stage = stage_entry.get()
        if mode in ["N", "H"]:
            pattern = r'\d+-\d+'
        else:
            pattern = r"^\d{2}$"
        if re.match(pattern, stage):
            stage_entry.configure(border_color=['#979DA2', '#565B5E'])
            return True
        else:
            stage_entry.configure(border_color='crimson')  
            return False

    # Function to move a frame up
    def move_frame_up(self, frame, queue=False):
        frames = self.queue_frames if queue else self.template_frames
        index = frames.index(frame)
        if index > 0:
            frames[index], frames[index - 1] = frames[index - 1], frames[index]
            self.update_frame_positions(queue=queue)

    # Function to move a frame down
    def move_frame_down(self, frame, queue=False):
        frames = self.queue_frames if queue else self.template_frames
        index = frames.index(frame)
        if index < len(frames) - 1:
            frames[index], self.template_frames[index + 1] = frames[index + 1], frames[index]
            self.update_frame_positions(queue=queue)

    # Function to update frame positions in the grid
    def update_frame_positions(self, queue=False):
        frames = self.queue_frames if queue else self.template_frames
        for index, frame in enumerate(frames, start=1):
            frame.grid(row=index + 1, column=0, columnspan=4, padx=10, pady=10, sticky="w")

    # Function to delete a frame
    def delete_frame(self, frame, queue=False):
        if queue:
            self.queue_frames.remove(frame)
        else:
            self.template_frames.remove(frame)
        frame.destroy()
        # Update the positions of remaining frames
        self.update_frame_positions(queue=queue)

class ClaimRewardsFrame(customtkinter.CTkFrame):
    def __init__(self, master, linker, config, **kwargs):
        super().__init__(master, **kwargs)
        self.linker = linker
        self.config = config
        self.claim_reward_settings_label = customtkinter.CTkLabel(self, text="Claim Rewards Settings", font=customtkinter.CTkFont(family="Inter", size=30, weight="bold"))
        self.claim_reward_settings_label.grid(row=0, column=0, sticky="nw", padx=20, pady=20)
        self.claim_tasks_checkbox = customtkinter.CTkCheckBox(self, text="Taks", font=customtkinter.CTkFont(family="Inter", size=20, weight="bold"), command= lambda x=["claim_rewards", "tasks"]: self.config.save_to_json(x))
        self.claim_tasks_checkbox.grid(row=1, column=0, pady=(20, 0), padx=20, sticky="nw")
        self.claim_mail_checkbox = customtkinter.CTkCheckBox(self, text="Mailbox", font=customtkinter.CTkFont(family="Inter", size=20, weight="bold"), command= lambda x=["claim_rewards", "mailbox"]: self.config.save_to_json(x))
        self.claim_mail_checkbox.grid(row=2, column=0, pady=(20, 0), padx=20, sticky="nw")
        self.linker.widgets["claim_rewards"]["tasks"] = self.claim_tasks_checkbox
        self.linker.widgets["claim_rewards"]["mailbox"] = self.claim_mail_checkbox 

class LoggerTextBox(customtkinter.CTkFrame):
    def __init__(self, master, linker, config, **kwargs):
        super().__init__(master=master, **kwargs)
        self.linker = linker
        self.config = config
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.log_label = customtkinter.CTkLabel(self, text="Log",font=customtkinter.CTkFont(family="Inter", size=30, weight="bold"))
        self.log_label.grid(row=0, column=0, sticky="nw", padx=20, pady=(20,0))
         # Button to toggle autoscroll
        self.toggle_autoscroll_button = customtkinter.CTkButton(self, height=35, text="Autoscroll On", command=self.toggle_autoscroll, font=("Inter", 16))
        self.toggle_autoscroll_button.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.autoscroll_enabled = True  # Initially, autoscroll is enabled
        self.log_textbox = customtkinter.CTkTextbox(self, state="disabled", font=("Inter", 16), wrap="word")
        self.log_textbox.grid(row=1, column=0,columnspan=4, padx=20, pady=20, sticky="nsew")  
        self.log_level_colors = {
            "[INFO]": "light blue",
            "[SUCCESS]": "light green",
            "[WARNING]": "orange",
            "[ERROR]": "red",
            "[DEBUG]": "purple"  
        }
        for level, color in self.log_level_colors.items():
            self.log_textbox.tag_config(level, foreground=color)
        self.linker.log_textbox = self

    def toggle_autoscroll(self):
        self.autoscroll_enabled = not self.autoscroll_enabled
        if self.autoscroll_enabled:
            self.toggle_autoscroll_button.configure(text="Autoscroll On")
        else:
            self.toggle_autoscroll_button.configure(text="Autoscroll Off")

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__("#18173C")
        self.configure_window()
        linker = Linker()
        config = Config(linker, "config.json")
        sidebar = Sidebar(self, linker, config, fg_color="#25224F")
        sidebar.grid(row=0, column=0, sticky="nsw")
        logger = LoggerTextBox(self, linker, config, fg_color="#262250")
        logger.grid(row=0, column=2, pady=20, sticky="nsew")
        config.load_config()

    def configure_window(self):
        self.title("BAAuto")
        self.geometry(f"{1500}x{850}")
        self.iconbitmap('gui/icons/karin.ico')
        self.scaleFactor = ctypes.windll.shcore.GetScaleFactorForDevice(0) / 100
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=0, minsize=650*self.scaleFactor)
        self.grid_columnconfigure(2, weight=1, minsize=506*self.scaleFactor)
        self.grid_rowconfigure(0, weight=1)

if __name__ == "__main__":
    app = App()
    app.mainloop()
