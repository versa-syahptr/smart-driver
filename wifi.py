import tkinter as tk
from subprocess import check_output

def get_wifi_list():
    try:
        wifi_list = check_output(["nmcli", "-t", "-f", "SSID,BARS", "device", "wifi"]).decode("utf-8").split()
        return [wifi.split(":") for wifi in wifi_list]
    except Exception as e:
        return ["Error fetching WiFi list:10"]

def connect_to_wifi(ssid, password):
    try:
        check_output(["nmcli", "device", "wifi", "connect", ssid, "password", password])
        return "Connected to {}".format(ssid)
    except Exception as e:
        return "Error connecting to {}".format(ssid)

class WiFiChooserApp:
    def __init__(self, master):
        self.master = master
        self.master.title("WiFi Chooser")

        self.label = tk.Label(master, text="Select a WiFi network:")
        self.label.pack(pady=10)

        self.wifi_listbox = tk.Listbox(master)
        self.wifi_listbox.pack()

        self.password_label = tk.Label(master, text="Enter WiFi Password:")
        self.password_label.pack()

        import tkinter.ttk as ttk

        self.password_entry = tk.Entry(master, show="*")
        self.password_entry.pack(pady=10)

        self.signal_label = tk.Label(master, text="Signal Strength:")
        self.signal_label.pack()

        self.signal_progress = ttk.Progressbar(master, orient="horizontal", length=200, mode="determinate")
        self.signal_progress.pack(pady=10)

        self.refresh_button = tk.Button(master, text="Refresh", command=self.refresh_wifi_list)
        self.refresh_button.pack(pady=10)

        self.connect_button = tk.Button(master, text="Connect", command=self.connect_to_selected_wifi)
        self.connect_button.pack(pady=10)

        self.refresh_wifi_list()

    def refresh_wifi_list(self):
        self.wifi_listbox.delete(0, tk.END)
        wifi_list = get_wifi_list()
        for wifi in wifi_list:
            ssid, signal_strength = wifi.split(":")
            self.wifi_listbox.insert(tk.END, ssid)
            self.signal_progress["value"] = int(signal_strength)

    def connect_to_selected_wifi(self):
        selected_index = self.wifi_listbox.curselection()
        if selected_index:
            selected_ssid = self.wifi_listbox.get(selected_index)
            password = self.password_entry.get()
            result = connect_to_wifi(selected_ssid, password)
            self.label.config(text=result)

if __name__ == "__main__":
    root = tk.Tk()
    app = WiFiChooserApp(root)
    root.mainloop()
