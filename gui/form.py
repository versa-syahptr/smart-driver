import sys
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import subprocess

def show_keyboard():
    # Temporarily set AlwaysOnTop to False
    # root.attributes('-topmost', False)
    
    # Use dbus calls to show the on-screen keyboard
    try:
        subprocess.run(["dbus-send", "--type=method_call", "--dest=org.onboard.Onboard",
                        "/org/onboard/Onboard/Keyboard", "org.onboard.Onboard.Keyboard.Show"])
        print("Keyboard shown")
    except Exception:
        print("Error", "Onboard not installed: show_keyboard")

    # Set AlwaysOnTop back to True
    # root.attributes('-topmost', True)

def hide_keyboard():
    # Temporarily set AlwaysOnTop to False
    # root.attributes('-topmost', False)
    
    # Use dbus calls to hide the on-screen keyboard
    try:
        subprocess.run(["dbus-send", "--type=method_call", "--dest=org.onboard.Onboard",
                        "/org/onboard/Onboard/Keyboard", "org.onboard.Onboard.Keyboard.Hide"])
        print("Keyboard hidden")
    except Exception:
        print("Error", "Onboard not installed: hide_keyboard")

    # Set AlwaysOnTop back to True
    # root.attributes('-topmost', True)


class Form(tk.Frame):
    def __init__(self, parent, fields, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.fields = fields
        self.entries = {}
        self.create_widgets()

    def create_widgets(self):
        for i, field in enumerate(self.fields):
            label = ttk.Label(self, text=field)
            entry = ttk.Entry(self)
            if field == 'Password':
                entry.config(show='*')
            label.grid(row=i, column=0, sticky=tk.W, padx=5, pady=5)  # Add padx and pady for margin
            entry.grid(row=i, column=1, sticky=tk.E, padx=5, pady=5)  # Add padx and pady for margin
            self.entries[field] = entry
            entry.bind("<FocusIn>", lambda event: show_keyboard())
            entry.bind("<FocusOut>", lambda event: hide_keyboard())


    def get(self):
        values = []
        for field in self.fields:
            value = self.entries[field].get()
            values.append(value)
        return values
    
    def focus(self, field):
        self.entries[field].focus_set()


if __name__ == '__main__':
    fields = ('SSID', 'Password')
    root = tk.Tk()
    root.title('Form')
    root.iconify()
    top = tk.Toplevel(root)
    # top.geometry('480x320')
    # set minimum size
    # top.minsize(480, 120)
    # set maximum size
    # top.maxsize(480, 320)
    # set fullscreen
    # root.attributes('-fullscreen', True)
    top.overrideredirect(True)
    top.resizable(False, True)
    root.attributes('-topmost', False)
    # if 'win' not in sys.platform:
    #     print("Linux")
    #     root.wm_attributes('-type', '-splash')
    form = Form(top, fields)
    form.pack()
    btn = ttk.Button(top, text='Submit', command=root.destroy)
    btn.pack()
    top.after(1000, lambda: form.focus('SSID'))
    root.mainloop()