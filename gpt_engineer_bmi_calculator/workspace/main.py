import tkinter as tk
from bmi_calculator import calculate_bmi

def calculate():
    weight = float(weight_entry.get())
    height = float(height_entry.get())
    bmi = calculate_bmi(weight, height)
    result_label.config(text=f"Your BMI is {bmi}")

root = tk.Tk()
root.title("BMI Calculator")

weight_label = tk.Label(root, text="Enter your weight (in kg):")
weight_label.pack()
weight_entry = tk.Entry(root)
weight_entry.pack()

height_label = tk.Label(root, text="Enter your height (in cm):")
height_label.pack()
height_entry = tk.Entry(root)
height_entry.pack()

calculate_button = tk.Button(root, text="Calculate", command=calculate)
calculate_button.pack()

result_label = tk.Label(root, text="")
result_label.pack()

root.mainloop()
