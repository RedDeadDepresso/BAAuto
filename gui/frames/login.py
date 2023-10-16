import customtkinter 
from gui.custom_widgets.ctk_tooltip import CTkToolTip
from gui.custom_widgets.ctk_integerspinbox import CTkIntegerSpinbox

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

        self.restart_attempts_spinbox = CTkIntegerSpinbox(self, step_size=1, min_value=0, command=lambda x=["login", "restart_attempts"]:self.config.save_to_json(x))
        self.restart_attempts_spinbox.entry.bind("<KeyRelease>", lambda event, x=["login", "restart_attempts"]: self.config.save_to_json(x))
        self.restart_attempts_spinbox.grid(row=8, column=0, padx=20, pady=(20, 10))

        self.linker.widgets["login"]["restart_attempts"] = self.restart_attempts_spinbox