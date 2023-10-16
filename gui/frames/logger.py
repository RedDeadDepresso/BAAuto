import customtkinter

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
        self.linker.logger = self

    def toggle_autoscroll(self):
        self.autoscroll_enabled = not self.autoscroll_enabled
        if self.autoscroll_enabled:
            self.toggle_autoscroll_button.configure(text="Autoscroll On")
        else:
            self.toggle_autoscroll_button.configure(text="Autoscroll Off")