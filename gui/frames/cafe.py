import customtkinter
import json
from gui.custom_widgets.ctk_scrollable_dropdown import CTkScrollableDropdown

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
