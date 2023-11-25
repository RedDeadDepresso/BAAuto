import customtkinter 
from gui.custom_widgets.ctk_tooltip import CTkToolTip
from gui.custom_widgets.ctk_integerspinbox import CTkIntegerSpinbox
from tkinter import filedialog, END

class LoginFrame(customtkinter.CTkFrame):
    def __init__(self, master, linker, config, **kwargs):
        super().__init__(master, **kwargs)
        self.linker = linker
        self.config = config
        self.create_widgets()
        self.bind_to_config()

    def create_widgets(self):
        self.login_settings_label = customtkinter.CTkLabel(self, text="Login Settings", font=customtkinter.CTkFont(family="Inter", size=30, weight="bold"))
        self.login_settings_label.grid(row=0, column=0, sticky="nw", padx=20, pady=20)
        
        self.core_label = customtkinter.CTkLabel(self, text="Core", font=customtkinter.CTkFont(family="Inter", size=26, weight="bold"))
        self.core_label.grid(row=1, column=0, sticky="nw", padx=20, pady=20)

        self.create_network_widgets()
        self.create_screenshot_widgets()
        self.create_server_widgets()
        self.create_restart_attempts_widgets()
        self.create_autorun_widgets()
        self.create_emulator_widgets()

    def create_network_widgets(self):
        self.network_label = customtkinter.CTkLabel(self, text="Connection address:", font=customtkinter.CTkFont(family="Inter", size=20))
        self.network_label.grid(row=2, column=0, padx=20, pady=(20, 10))

        self.network_entry = customtkinter.CTkEntry(self)
        self.network_entry.grid(row=2, column=1, padx=20, pady=(20, 10))

    def create_screenshot_widgets(self):
        self.screenshot_label = customtkinter.CTkLabel(self, text="Screenshot mode:", font=customtkinter.CTkFont(size=20))
        self.screenshot_label.grid(row=3, column=0, padx=20, pady=(20, 10))

        self.screenshot_dropdown = customtkinter.CTkOptionMenu(self, values=["SCREENCAP_PNG", "SCREENCAP_RAW", "ASCREENCAP", "UIAUTOMATOR2"])
        self.screenshot_dropdown.grid(row=3, column=1, padx=20, pady=(20, 10))

    def create_server_widgets(self):
        self.server_label = customtkinter.CTkLabel(self, text="Server:", font=customtkinter.CTkFont(size=20))
        self.server_label.grid(row=4, column=0, padx=20, pady=(20, 10))

        self.server_dropdown = customtkinter.CTkOptionMenu(self, values=["EN", "CN"])
        self.server_dropdown.grid(row=4, column=1, padx=20, pady=(20, 10))

    def create_restart_attempts_widgets(self):
        self.restart_attempts_label = customtkinter.CTkLabel(self, text="Restart attempts", font=customtkinter.CTkFont(size=20, underline=True))
        self.restart_attempts_label.grid(row=5, column=0, padx=20, pady=(20, 10))
        self.restart_attempts_tootltip = CTkToolTip(self.restart_attempts_label, message="Sets the number of restart attempts allowed to the script. Restart attempts are triggered when the game crashes or freezes.", wraplength=400)

        self.restart_attempts_spinbox = CTkIntegerSpinbox(self, step_size=1, min_value=0)
        self.restart_attempts_spinbox.grid(row=5, column=1, padx=20, pady=(20, 10))

    def create_autorun_widgets(self):
        self.core_label = customtkinter.CTkLabel(self, text="Startup", font=customtkinter.CTkFont(family="Inter", size=26, weight="bold"))
        self.core_label.grid(row=6, column=0, sticky="nw", padx=20, pady=20)

        self.autostart_checkbox = customtkinter.CTkCheckBox(self, text="Auto Start Script", font=customtkinter.CTkFont(size=20, weight="bold", underline=True))
        self.autostart_tootltip = CTkToolTip(self.autostart_checkbox, message="Script will automatically start after launching BAAuto.", wraplength=400)
        self.autostart_checkbox.grid(row=7, column=0, padx=40, pady=(20, 10), sticky="nw")

    def create_emulator_widgets(self):
        self.emulator_checkbox = customtkinter.CTkCheckBox(self, text="Launch Emulator", font=customtkinter.CTkFont(size=20, underline=True))
        self.emulator_tooltip = CTkToolTip(self.emulator_checkbox, 
                                           message="When enabled, the script will launch the emulator if it doesn't find any device with the specified address. Emulator path MUST be provided and be valid.", 
                                           wraplength=400)
        
        self.emulator_checkbox.grid(row=8, column=0, padx=40, pady=(20, 10), sticky="nw")

        self.emulator_path_entry = customtkinter.CTkEntry(self, font=customtkinter.CTkFont(family="Inter", size=16))
        self.emulator_path_entry.grid(row=9, column=0, columnspan=2, padx=(60,0), pady=(20, 10), sticky="nsew")


        self.emulator_path_button = customtkinter.CTkButton(self, width=50, text="Select", command = self.open_file)
        self.emulator_path_button.grid(row=9, column=2, padx=20, pady=(20, 10), sticky="nsew")

        self.delay_label = customtkinter.CTkLabel(self, text="Delay time (s)", font=customtkinter.CTkFont(size=20, family="Inter", underline=True))
        self.delay_tooltip = CTkToolTip(self.delay_label, message="The time for the script to wait after launching the emulator", wraplength=400)
        self.delay_label.grid(row=10, column=0, padx=20, pady=(20, 10))

        self.delay_spinbox = CTkIntegerSpinbox(self, step_size=1, min_value=0)
        self.delay_spinbox.grid(row=10, column=1)

    def bind_to_config(self):
        # Bind network entry
        self.config.bind(self.network_entry, ["login", "network"])

        # Bind screenshot dropdown
        self.config.bind(self.screenshot_dropdown, ["login", "screenshot_mode"])

        # Bind server dropdown
        self.config.bind(self.server_dropdown, ["login", "server"])

        # Bind restart attempts spinbox
        self.config.bind(self.restart_attempts_spinbox, ["login", "restart_attempts"])

        # Bind autostart checkbox
        self.config.bind(self.autostart_checkbox, ["login", "auto_start"])

        # Bind emulator checkbox
        self.config.bind(self.emulator_checkbox, ["login", "launch_emulator"])

        # Bind emulator path entry
        self.config.bind(self.emulator_path_entry, ["login", "emulator_path"])

        # Bind delay spinbox
        self.config.bind(self.delay_spinbox, ["login", "delay"])

    def open_file(self):
        filepath = filedialog.askopenfilename(filetypes=[("Executable files", "*.exe;*.lnk")])
        if filepath != "":
            self.emulator_path_entry.delete(0, END)
            self.emulator_path_entry.insert(0, filepath)
            self.config.save_to_json(["login", "emulator_path"])


