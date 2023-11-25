import customtkinter

class ClaimRewardsFrame(customtkinter.CTkFrame):
    def __init__(self, master, linker, config, **kwargs):
        super().__init__(master, **kwargs)
        self.linker = linker
        self.config = config
        self.create_widgets()

        # Call bind_to_config to set up bindings
        self.bind_to_config()

    def create_widgets(self):
        self.claim_reward_settings_label = customtkinter.CTkLabel(self, text="Claim Rewards Settings", font=customtkinter.CTkFont(family="Inter", size=30, weight="bold"))
        self.claim_reward_settings_label.grid(row=0, column=0, sticky="nw", padx=20, pady=20)

        self.claim_club_checkbox = customtkinter.CTkCheckBox(self, text="Club", font=customtkinter.CTkFont(family="Inter", size=20, weight="bold"))
        self.claim_club_checkbox.grid(row=1, column=0, pady=(20, 0), padx=20, sticky="nw")

        self.claim_tasks_checkbox = customtkinter.CTkCheckBox(self, text="Tasks", font=customtkinter.CTkFont(family="Inter", size=20, weight="bold"))
        self.claim_tasks_checkbox.grid(row=2, column=0, pady=(20, 0), padx=20, sticky="nw")

        self.claim_mail_checkbox = customtkinter.CTkCheckBox(self, text="Mailbox", font=customtkinter.CTkFont(family="Inter", size=20, weight="bold"))
        self.claim_mail_checkbox.grid(row=3, column=0, pady=(20, 0), padx=20, sticky="nw")

    def bind_to_config(self):
        # Bind club checkbox
        self.config.bind(self.claim_club_checkbox, ["claim_rewards", "club"])

        # Bind tasks checkbox
        self.config.bind(self.claim_tasks_checkbox, ["claim_rewards", "tasks"])

        # Bind mailbox checkbox
        self.config.bind(self.claim_mail_checkbox, ["claim_rewards", "mailbox"])

# Example usage:
# claim_rewards_frame = ClaimRewardsFrame(master, linker, config)
# (No need to call claim_rewards_frame.bind_to_config() explicitly)
