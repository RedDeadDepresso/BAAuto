import json
import subprocess
import threading
import customtkinter
import sys
import platform
import customtkinter
import subprocess
import os

from util.emulator import Emulator
from gui.frames.sidebar import Sidebar
from gui.frames.logger import LoggerTextBox
from gui.custom_widgets.ctk_notification import CTkNotification
from gui.custom_widgets.ctkmessagebox import CTkMessagebox
from gui.custom_widgets.ctk_integerspinbox import CTkIntegerSpinbox

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

    def bind(self, widget, list_keys):

        if isinstance(widget, customtkinter.CTkEntry):
            widget.bind("<KeyRelease>", lambda event, x=list_keys: self.save_to_json(x))
        elif isinstance(widget, CTkIntegerSpinbox):
            widget.configure(command=lambda x=list_keys: self.save_to_json(x))
            widget.entry.bind("<KeyRelease>", lambda event, x=list_keys: self.save_to_json(x))
        elif isinstance(widget, (customtkinter.CTkCheckBox)):
            widget.configure(command=lambda x=list_keys: self.save_to_json(x))
        else:
            widget.configure(command=lambda x, y=list_keys: self.save_to_json(y))

        widgets_dictionary = self.linker.widgets
        for key in list_keys[:-1]:
            widgets_dictionary = widgets_dictionary[key]
        widgets_dictionary[list_keys[-1]] = widget

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
        self.save_file("Configuration")

    def save_file(self, name=None):
        with open("config.json", "w") as config_file:
            json.dump(self.config_data, config_file, indent=2)
        if name:    
            self.linker.show_notification(name)
    
class Linker:
    def __init__(self):
        self.capitalise = lambda word: " ".join(x.title() for x in word.split("_"))        
        self.config = None
        self.widgets = {}
        # frames
        self.sidebar = None
        self.modules_dictionary = {}
        self.logger = None
        # script.py process
        self.script = None
        self.name_to_sidebar_frame = {
            "Template": None,
            "Queue": None,
            "Configuration":None
        }
        self.should_then = False

    def terminate_script(self):
        # If process is running, terminate it
        self.script.terminate()
        self.script = None
        self.sidebar.start_button.configure(text="Start", fg_color = ['#3B8ED0', '#1F6AA5'])
        self.switch_queue_state("normal")

    def switch_student_list(self):
        server = self.config.config_data["login"]["server"]
        with open(f"gui/student_list/{server}.json", "r") as f:
            student_list = json.load(f)
        cafe_frame = self.modules_dictionary["cafe"]["frame"]
        cafe_frame.student_dropdown.configure(values=student_list)
        
    def start_stop(self):
        if hasattr(self, 'script') and self.script is not None:
            self.terminate_script()
        else:
            # If process is not running, start it
            self.script = subprocess.Popen(['python', 'script.py'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            threading.Thread(target=self.read_output).start()
            self.sidebar.start_button.configure(text="Stop", fg_color = "crimson")
            self.switch_queue_state("disabled")

    def read_output(self):
        while self.script is not None:
            line = self.script.stdout.readline().decode('utf-8')
            for string in ['Terminating...', "All assigned tasks were executed."]:
                if string in line or line == '':
                    if hasattr(self, 'script') and self.script is not None:
                        self.sidebar.master.after(10, self.terminate_script)

                    if "All assigned tasks were executed." in line:
                        self.sidebar.master.after(10, self.execute_then)
                    return  # Break the loop if there's no more output and the subprocess has finished

            # Check if line contains any log level
            for level, color in self.logger.log_level_colors.items():
                if level in line:
                    # Display output in text box with color
                    self.logger.log_textbox.configure(state="normal")           
                    self.logger.log_textbox.insert("end", line, level)
                    self.logger.log_textbox.configure(state="disabled")
                    break

            if self.logger.autoscroll_enabled:
                self.logger.log_textbox.yview_moveto(1.0)

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
        self.config.config_data["farming"]['mission']['last_run'] = new_config_data["farming"]['mission']['last_run']
        self.config.config_data["farming"]['mission']['queue'] = new_config_data["farming"]['mission']['queue']
        for entry in self.config.config_data["farming"]['mission']['queue']:
            farming_frame.add_frame(entry, queue=True)

    def show_notification(self, name):
        sidebar_frame = self.name_to_sidebar_frame[name]
        if self.script:
            new_notification = CTkNotification(text= f"{name} was saved but will be read by the script in the next run.", master=sidebar_frame, fg_color="orange")
        else:
            new_notification = CTkNotification(text= f"{name} was saved successfully.", master=sidebar_frame, fg_color="green")
        new_notification.grid(row=0, column=0, sticky="nsew")
        self.sidebar.master.after(2500, new_notification.destroy)
    
    def execute_then(self):
        if hasattr(self, 'script') and self.script is not None:
            self.terminate_script()

        then = self.config.config_data["then"]
        emulator_path = self.config.config_data["login"]["emulator_path"]

        if then == "Do Nothing":
            return

        elif then == "Exit BAAuto":
            self.sidebar.master.destroy()

        elif then == "Exit Emulator":
            if os.path.isfile(emulator_path):
                Emulator.terminate(emulator_path)  

        elif then == "Exit BAAuto and Emulator":
            if os.path.isfile(emulator_path):
                Emulator.terminate(emulator_path)  
            self.sidebar.master.destroy()
                
        elif then == "Shutdown":
            subprocess.run("shutdown -s -t 60", shell=True)
            msg = CTkMessagebox(title="Cancel Shutdown?", message="All tasks have been completed: shutting down. Do you want to cancel?",
                                icon="question", option_1="Cancel")
            response = msg.get()
            if response=="Cancel":
                subprocess.run("shutdown -a", shell=True)

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
        if config.config_data["login"]["auto_start"]:
            self.after(10, linker.start_stop)

    def configure_window(self):
        self.title("BAAuto")
        self.geometry(f"{1500}x{850}")
        self.iconbitmap('gui/icons/karin.ico')
        """ 
        solution to Settings Frame and Logger Frame widths not being 
        consistent between different windows scaling factoro#s
        """
        self.scaling_factor = self.get_scaling_factor()
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=0, minsize=650*self.scaling_factor)
        self.grid_columnconfigure(2, weight=1, minsize=506*self.scaling_factor)
        self.grid_rowconfigure(0, weight=1)

    def get_scaling_factor(self):
        system = platform.system()
        
        if system == 'Windows':
            import ctypes
            user32 = ctypes.windll.user32
            return user32.GetDpiForSystem() / 96.0
        
        if system == 'Darwin':  # macOS
            from Quartz import CGDisplayScreenSize, CGDisplayPixelsWide
            screen_size = CGDisplayScreenSize(0)
            screen_width = CGDisplayPixelsWide(0)
            return screen_width / screen_size[0]
        
        if system == 'Linux':
            command = ["gsettings", "get", "org.gnome.desktop.interface", "scaling-factor"]
            try:
                output = subprocess.check_output(command).decode("utf-8")
                return float(output.strip())
            except subprocess.CalledProcessError:
                return 1.0  # Default to 100% if unable to retrieve scaling factor
        
        return 1.0  # Default scaling factor for unknown or unsupported systems

if __name__ == "__main__":
    app = App()
    app.mainloop()
