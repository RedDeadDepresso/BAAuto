import customtkinter
import tkinter as tk
import random
import re
from gui.custom_widgets.ctkmessagebox import CTkMessagebox
from gui.custom_widgets.ctk_tooltip import CTkToolTip
from gui.custom_widgets.ctk_timeentry import CTkTimeEntry
from gui.custom_widgets.ctk_integerspinbox import CTkIntegerSpinbox
from gui.custom_widgets.ctk_templatedialog import CTkTemplateDialog

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

            spinbox = CTkIntegerSpinbox(self, step_size=1, min_value=0, command=lambda x=["farming", "bounty", element, "run_times"]:self.config.save_to_json(x))
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

            option_menu = customtkinter.CTkOptionMenu(self, width=80, values=values[:5], command=lambda x, y=["farming", "scrimmage", element, "stage"]: self.config.save_to_json(y), font=customtkinter.CTkFont(family="Inter", size=16))
            option_menu.grid(row=index + 6, column=1)
            self.linker.widgets["farming"]["scrimmage"][element]["stage"] = option_menu

            spinbox = CTkIntegerSpinbox(self, step_size=1, min_value=0, command=lambda x=["farming", "scrimmage", element, "run_times"]: self.config.save_to_json(x))
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
        self.reset_daily = customtkinter.CTkCheckBox(self, text="Reset Daily", font=customtkinter.CTkFont(family="Inter", size=16, underline=True), command=lambda x=["farming", "mission", "reset_daily"]: self.config.save_to_json(x))
        self.reset_daily.grid(row=12, column=0, sticky="nw", padx=80)
        self.reset_daily_tooltip = CTkToolTip(self.reset_daily, wraplength=400,
                                              message="If enabled and if current time >= reset time,\
                                                the queue will automatically be cleared and repopulated with preferred template stages. Only activated once a day.")

        self.reset_daily_sub_label = customtkinter.CTkLabel(self, text="hh/mm/ss", font=customtkinter.CTkFont(family="Inter", size=12))
        self.reset_daily_sub_label.grid(row=13, column=0, padx=80)

        self.reset_time = CTkTimeEntry(self)
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
                                              message="When enabled, recharge AP when low via cafe earnings and claim rewards, if they are enabled in their respective sections.")
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
    def load_queue_data(self, state="normal"):
        for entry in self.config.config_data["farming"]['mission']['queue']:
            self.add_frame(entry, queue=True, state=state)

    # Function to load template data into frames
    def load_template_data(self):
        selected = self.selected_template.get()
        if selected == "Add New Template":
            dialog = CTkTemplateDialog(text="Type in new template name. Template name MUST be different from other templates!", title="Template Name", values=self.templates_list[:-1])
            template_name, template_import = dialog.get_input()
            if template_name.replace(" ", "") == "":
                self.template_optionmenu.set(self.previous_selected)
                return
            elif template_name in self.templates_list:
                CTkMessagebox(title="Error", message="Name is invalid.", icon="cancel")
                self.template_optionmenu.set(self.previous_selected)
                return
            else:
                if template_import != "":
                    self.templates[template_name] = self.templates[template_import]
                else:
                    self.templates[template_name] = []
                self.templates_list[-1] = template_name
                self.preferred_template_optionmenu.configure(values=self.templates_list)
                selected = template_name
                self.template_optionmenu.set(selected)
                self.templates_list.append("Add New Template")
                self.template_optionmenu.configure(values=self.templates_list)
        self.clear_frames()
        for entry in self.templates[selected]:
            self.add_frame(entry)
        self.previous_selected  = selected

    def delete_template(self):
        msg = CTkMessagebox(title="Template Deletetion", message=f"Are you sure you want to delete Template {self.previous_selected}?",
                        icon="question", option_1="No", option_2="Yes")
        response = msg.get()
        if response=="Yes":
            if len(self.templates) != 1:
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
    def add_frame(self, inner_list=None, queue=False, state="normal"):
        frames = self.queue_frames if queue else self.template_frames
        parent_frame = self.queue_frame if queue else self.template_frame
        row_index = len(frames) + 1  # Calculate the row for the new frame
        # Create a frame
        frame = customtkinter.CTkFrame(parent_frame)
        frame.grid(row=row_index, column=0, columnspan=4, padx=10, pady=10, sticky="w")
        frames.append(frame)
        # "Up" button to move the frame up
        up_button = customtkinter.CTkButton(frame, text="Up", width=5, command=lambda f=frame, queue=queue: self.move_frame_up(f, queue), state=state)
        up_button.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        # "Down" button to move the frame down
        down_button = customtkinter.CTkButton(frame, text="Down", width=5, command=lambda f=frame, queue=queue: self.move_frame_down(f, queue), state=state)
        down_button.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        # Dropdown menu for mode
        mode_optionmenu = customtkinter.CTkOptionMenu(frame, width=60, values=["N", "H", "E", "BD", "IR"], state=state)
        mode_optionmenu.set(inner_list[0] if inner_list else "N")
        mode_optionmenu.grid(row=0, column=2, padx=5, pady=5, sticky="w")
        # Entry widget for stage
        stage_var = tk.StringVar(value=inner_list[1] if inner_list else "")
        stage_entry = customtkinter.CTkEntry(frame, width=60, textvariable=stage_var, state=state)
        stage_entry.grid(row=0, column=3, padx=5, pady=5, sticky="w")
        mode_optionmenu.configure(command=lambda choice, x=mode_optionmenu, y=stage_entry : self.check_entry(x,y))
        stage_entry.bind('<KeyRelease>', command=lambda event, x=mode_optionmenu, y=stage_entry : self.check_entry(x,y))
        self.check_entry(mode_optionmenu, stage_entry)
        # Entry widget for run times (only accepts numbers)
        run_times_spinbox = CTkIntegerSpinbox(frame, step_size=1, min_value=1)
        run_times_spinbox.set(value=inner_list[2] if inner_list else 1)
        run_times_spinbox.grid(row=0, column=4, padx=5, pady=5, sticky="w")

        # Delete button to delete the frame
        delete_button = customtkinter.CTkButton(frame, text="Delete", width=5, command=lambda f=frame, queue=queue: self.delete_frame(f, queue), state=state)
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
        name = "Queue" if queue else "Template"
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
        self.config.save_file(name)

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
            frames[index], frames[index + 1] = frames[index + 1], frames[index]
            self.update_frame_positions(queue=queue)

    # Function to update frame positions in the grid
    def update_frame_positions(self, queue=False):
        frames = self.queue_frames if queue else self.template_frames
        for index, frame in enumerate(frames):
            frame.grid(row=index, column=0, columnspan=4, padx=10, pady=10, sticky="w")

    # Function to delete a frame
    def delete_frame(self, frame, queue=False):
        if queue:
            self.queue_frames.remove(frame)
        else:
            self.template_frames.remove(frame)
        frame.destroy()
        # Update the positions of remaining frames
        self.update_frame_positions(queue=queue)
