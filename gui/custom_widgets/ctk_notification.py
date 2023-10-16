import customtkinter
class CTkNotification(customtkinter.CTkFrame):
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