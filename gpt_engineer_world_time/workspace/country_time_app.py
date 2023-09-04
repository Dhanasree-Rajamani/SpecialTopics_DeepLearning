import tkinter as tk
from tkinter import ttk, messagebox
from time_utils import get_country_timezones, get_current_time
import pytz

class CountryTimeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Country Time App")
        self.create_widgets()

    def create_widgets(self):
        self.country_var = tk.StringVar()
        self.time_label = tk.Label(self.root, text="")
        self.country_combobox = ttk.Combobox(self.root, textvariable=self.country_var)
        self.country_combobox['values'] = list(pytz.country_names.keys())
        self.country_combobox.bind("<<ComboboxSelected>>", self.update_time)
        self.country_combobox.pack()
        self.time_label.pack()

    def update_time(self, event):
        country = self.country_var.get()
        timezones = get_country_timezones(country)
        if timezones:
            time = get_current_time(timezones[0])
            self.time_label.config(text=time)
        else:
            messagebox.showerror("Error", "Invalid country")

def main():
    root = tk.Tk()
    app = CountryTimeApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
