
import customtkinter
import tkinter as tk
import re
from typing import Callable

class TimeEntry(customtkinter.CTkFrame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.hour = tk.StringVar()
        self.minute = tk.StringVar()
        self.second = tk.StringVar()

        self.hour_entry = customtkinter.CTkEntry(self, width=50, textvariable=self.hour, validate="key", validatecommand=(self.register(self.validate_hour), '%P'))
        self.hour_entry.pack(side=tk.LEFT)

        self.minute_entry = customtkinter.CTkEntry(self,width=50, textvariable=self.minute, validate="key", validatecommand=(self.register(self.validate_min_sec), '%P'))
        self.minute_entry.pack(side=tk.LEFT)

        self.second_entry = customtkinter.CTkEntry(self, width=50, textvariable=self.second, validate="key", validatecommand=(self.register(self.validate_min_sec), '%P'))
        self.second_entry.pack(side=tk.LEFT)

    def validate_hour(self, P):
        return len(P) <= 2 and (P.isdigit() and int(P) <= 23 or P == "")

    def validate_min_sec(self, P):
        return len(P) <= 2 and (P.isdigit() and int(P) <= 59 or P == "")

    def set(self, time_str):
        h, m, s = map(str, time_str.split(':'))
        self.hour.set(h)
        self.minute.set(m)
        self.second.set(s)

    def get(self):
        h = self.hour.get() if self.hour.get() else "00"
        m = self.minute.get() if self.minute.get() else "00"
        s = self.second.get() if self.second.get() else "00"
        return f"{h.zfill(2)}:{m.zfill(2)}:{s.zfill(2)}"
    
class Notification(customtkinter.CTkFrame):
    def __init__(self, text, master, **kwargs):
        super().__init__(master=master, **kwargs)
        self.label = customtkinter.CTkLabel(self, text=text, width=200, wraplength=200, font=("Inter", 16))
        self.label.grid(row=0, column=0, sticky="nsew")
        self.close_button = customtkinter.CTkButton(self, width=40, text="X", command=self.destroy, fg_color="transparent")
        self.close_button.grid(row=0, column=1)
        self.progress_bar = customtkinter.CTkProgressBar(self, progress_color="white", determinate_speed=0.4)
        self.progress_bar.grid(row=1, column=0, columnspan=2, sticky="nsew")
        self.progress_bar.set(0)
        self.progress_bar.start()

class IntegerSpinbox(customtkinter.CTkFrame):
    def __init__(self, *args,
                 width: int = 100,
                 height: int = 32,
                 step_size: int = 1,
                 min_value: int = 0,
                 command: Callable = None,
                 **kwargs):
        super().__init__(*args, width=width, height=height, **kwargs)

        self.step_size = step_size
        self.min_value = min_value
        self.command = command

        self.grid_columnconfigure((0, 2), weight=0)
        self.grid_columnconfigure(1, weight=1)

        self.subtract_button = customtkinter.CTkButton(self, text="-", width=height-6, height=height-6,
                                                       command=self.subtract_button_callback)
        self.subtract_button.grid(row=0, column=0, padx=(3, 0), pady=3)

        self.entry = customtkinter.CTkEntry(self, width=width-(2*height), height=height-6, border_width=0)
        self.entry.grid(row=0, column=1, columnspan=1, padx=3, pady=3, sticky="ew")

        self.add_button = customtkinter.CTkButton(self, text="+", width=height-6, height=height-6,
                                                  command=self.add_button_callback)
        self.add_button.grid(row=0, column=2, padx=(0, 3), pady=3)

        self.entry.insert(0, "0")
        
        # Configure validatecommand to allow only integers
        vcmd = (self.entry.register(self.validate_input), '%P')
        self.entry.configure(validate='key', validatecommand=vcmd)

    def add_button_callback(self):
        try:
            value = int(self.entry.get()) + self.step_size
            self.entry.delete(0, "end")
            self.entry.insert(0, max(self.min_value, value))  # Ensure the value is not less than 1
            if self.command is not None:
                self.command()
        except ValueError:
            return

    def subtract_button_callback(self):
        try:
            value = int(self.entry.get()) - self.step_size
            self.entry.delete(0, "end")
            self.entry.insert(0, max(self.min_value, value))  # Ensure the value is not less than 0
            if self.command is not None:
                self.command()
        except ValueError:
            return

    def validate_input(self, new_value):
        # Validate that the input is a non-negative integer
        return re.match(r'^\d*$', new_value) is not None

    def get(self) -> int:
        try:
            return int(self.entry.get())
        except ValueError:
            return 0

    def set(self, value: int):
        self.entry.delete(0, "end")
        self.entry.insert(0, max(self.min_value, value))  # Ensure the value is not less than 0

    def configure(self, state):
        self.subtract_button.configure(state=state)
        self.add_button.configure(state=state)
        self.entry.configure(state=state)