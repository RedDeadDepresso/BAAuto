import customtkinter
from PIL import Image
from gui.frames.login import LoginFrame
from gui.frames.cafe import CafeFrame
from gui.frames.farming import FarmingFrame
from gui.frames.claim_rewards import ClaimRewardsFrame
from gui.custom_widgets.ctk_tooltip import CTkToolTip

class Sidebar(customtkinter.CTkFrame):
    def __init__(self, master, linker, config, **kwargs):
        self.master = master
        self.linker = linker
        self.config = config
        super().__init__(master=self.master, **kwargs)
        self.grid_rowconfigure((0, 1, 2), weight=1)
        self.grid_columnconfigure(0, weight=1)
        karin_logo = customtkinter.CTkImage(light_image=Image.open("gui/icons/karin.png"), size=(152,152))
        karin_logo_label = customtkinter.CTkLabel(self, image=karin_logo, text="")
        karin_logo_label.grid(row=0, column=0, sticky="nsew")
        self.gear_on = customtkinter.CTkImage(Image.open("gui/icons/gear_on.png"), size=(50,38))
        self.gear_off = customtkinter.CTkImage(Image.open("gui/icons/gear_off.png"), size=(50,38))
        self.create_module_frames()
        self.create_all_button_frame()
        self.create_then_frame()
        self.create_start_button()
        self.create_notification_frames()
        self.linker.sidebar = self
        
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

    def create_then_frame(self):
        self.then_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.then_frame.grid(row=2, column=0)

        self.then_label = customtkinter.CTkLabel(self.then_frame, text="Then", font=customtkinter.CTkFont(size=16, family="Inter", underline=True))
        self.then_label.grid(row=0, column=0, padx=(0, 10), sticky="nw")
        self.then_tooltip = CTkToolTip(self.then_label, 
                                       message="Administrator privileges most likely required for exiting emulator and shutting down. For exiting emulator, path MUST be provided in Login Settings and be valid.", 
                                       wraplength=400)
        
        then_values = ["Do Nothing", "Exit BAAuto", "Exit Emulator", "Exit BAAuto and Emulator", "Shutdown"]
        self.then_optionmenu = customtkinter.CTkOptionMenu(self.then_frame, values=then_values, command=lambda choice: self.save_then(choice))
        self.then_optionmenu.grid(row=0, column=1, sticky="nw")

        
        self.linker.widgets["then"] = self.then_optionmenu

    def create_start_button(self):
        self.start_button = customtkinter.CTkButton(self, text="Start", width=200, height=40, command=self.linker.start_stop, font=customtkinter.CTkFont(family="Inter", size=16))
        self.start_button.grid(row=3, column=0, pady=20, sticky="n")

    def create_notification_frames(self):
        for index, element in enumerate(["Template", "Queue", "Configuration"]):
            frame = customtkinter.CTkFrame(self, fg_color="transparent", height=50)
            if index == 0:
                top_pady=170
            else:
                top_pady=0
            frame.grid(row=3+index, column=0, sticky="s", pady=(top_pady,0))
            self.linker.name_to_sidebar_frame[element] = frame

    def select_all(self):
        for module in self.linker.modules_dictionary:
            if module != "momotalk":
                self.linker.modules_dictionary[module]["checkbox"].select()
                self.config.config_data[module]["enabled"] = True
        self.config.save_file("Configuration")

    def clear_all(self):
        for module in self.linker.modules_dictionary:
            self.linker.modules_dictionary[module]["checkbox"].deselect()
            self.config.config_data[module]["enabled"] = False
        self.config.save_file("Configuration")

    def save_then(self, choice):
        self.config.config_data["then"] = choice
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
