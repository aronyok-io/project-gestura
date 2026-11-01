import tkinter as tk
from tkinter import ttk


class ActivityLog(tk.Text):
    def __init__(self, parent):
        super().__init__(parent, height=5, state="disabled", wrap="word")

    def append(self, message):
        self.configure(state="normal")
        self.insert("end", str(message) + "\n")
        if int(self.index("end-1c").split(".")[0]) > 100:
            self.delete("1.0", "50.0")
        self.see("end")
        self.configure(state="disabled")


class CameraPreview(ttk.Label):
    def __init__(self, parent, text):
        super().__init__(parent, text=text, anchor="center")
        self.photo = None

    def show_frame(self, frame):
        from PIL import Image, ImageTk
        image = Image.fromarray(frame)
        image.thumbnail((760, 380))
        self.photo = ImageTk.PhotoImage(image)
        self.configure(image=self.photo, text="")
