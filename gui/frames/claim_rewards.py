import customtkinter

class ClaimRewardsFrame(customtkinter.CTkFrame):
    def __init__(self, master, linker, config, **kwargs):
        super().__init__(master, **kwargs)
        self.linker = linker
        self.config = config
        self.claim_reward_settings_label = customtkinter.CTkLabel(self, text="Claim Rewards Settings", font=customtkinter.CTkFont(family="Inter", size=30, weight="bold"))
        self.claim_reward_settings_label.grid(row=0, column=0, sticky="nw", padx=20, pady=20)
        self.claim_club_checkbox = customtkinter.CTkCheckBox(self, text="Club", font=customtkinter.CTkFont(family="Inter", size=20, weight="bold"), command= lambda x=["claim_rewards", "club"]: self.config.save_to_json(x))
        self.claim_club_checkbox.grid(row=1, column=0, pady=(20, 0), padx=20, sticky="nw")
        self.claim_tasks_checkbox = customtkinter.CTkCheckBox(self, text="Tasks", font=customtkinter.CTkFont(family="Inter", size=20, weight="bold"), command= lambda x=["claim_rewards", "tasks"]: self.config.save_to_json(x))
        self.claim_tasks_checkbox.grid(row=2, column=0, pady=(20, 0), padx=20, sticky="nw")
        self.claim_mail_checkbox = customtkinter.CTkCheckBox(self, text="Mailbox", font=customtkinter.CTkFont(family="Inter", size=20, weight="bold"), command= lambda x=["claim_rewards", "mailbox"]: self.config.save_to_json(x))
        self.claim_mail_checkbox.grid(row=3, column=0, pady=(20, 0), padx=20, sticky="nw")
        self.linker.widgets["claim_rewards"]["club"] = self.claim_tasks_checkbox
        self.linker.widgets["claim_rewards"]["tasks"] = self.claim_tasks_checkbox
        self.linker.widgets["claim_rewards"]["mailbox"] = self.claim_mail_checkbox 