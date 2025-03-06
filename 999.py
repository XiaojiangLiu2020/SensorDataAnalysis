import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import argrelextrema
import numpy as np
import os
import tkinter as tk
from tkinter import filedialog, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageTk  # Import Pillow for image handling
import json

def save_variables():
    variables = {
        "startSamplePoint": start_entry.get(),
        "endSamplePoint": end_entry.get(),
        "peaksCounts": peaks_entry.get(),
        "peakLength": peak_entry.get(),
        "gasOutTime": gasOut_entry.get(),
        "gasInTime": gasIn_entry.get(),
        "windowSize": window_entry.get(),
        "showPeakValue": show_peak_value.get(),
        "showGasIn": show_gas_in.get(),
        "showGasOut": show_gas_out.get(),
        "showResponse": show_response.get(),
        "showResponseTime": show_response_time.get(),
        "showRecoveryTime": show_recovery_time.get(),
        "sampleRate": sample_rate_entry.get(),
        "mode": mode_var.get()
    }
    with open("variables.json", "w") as f:
        json.dump(variables, f)
    messagebox.showinfo("Info", "Variables saved successfully.")

def load_variables():
    if os.path.exists("variables.json"):
        with open("variables.json", "r") as f:
            variables = json.load(f)
        start_entry.delete(0, tk.END)
        start_entry.insert(0, variables.get("startSamplePoint", "0"))
        end_entry.delete(0, tk.END)
        end_entry.insert(0, variables.get("endSamplePoint", "13000"))
        peaks_entry.delete(0, tk.END)
        peaks_entry.insert(0, variables.get("peaksCounts", "4"))
        peak_entry.delete(0, tk.END)
        peak_entry.insert(0, variables.get("peakLength", "500"))
        gasOut_entry.delete(0, tk.END)
        gasOut_entry.insert(0, variables.get("gasOutTime", "700"))
        gasIn_entry.delete(0, tk.END)
        gasIn_entry.insert(0, variables.get("gasInTime", "700"))
        window_entry.delete(0, tk.END)
        window_entry.insert(0, variables.get("windowSize", "200"))
        sample_rate_entry.delete(0, tk.END)
        sample_rate_entry.insert(0, variables.get("sampleRate", "1"))
        show_peak_value.set(variables.get("showPeakValue", 1))
        show_gas_in.set(variables.get("showGasIn", 1))
        show_gas_out.set(variables.get("showGasOut", 1))
        show_response.set(variables.get("showResponse", 1))
        show_response_time.set(variables.get("showResponseTime", 1))
        show_recovery_time.set(variables.get("showRecoveryTime", 1))
        mode_var.set(variables.get("mode", "SamplePoints"))

def preview_plot():
    try:
        filename = file_entry.get()
        startSamplePoint = int(start_entry.get())
        endSamplePoint = int(end_entry.get())

        file_extension = os.path.splitext(filename)[1]

        if file_extension == '.csv':
            with open(filename, 'r') as file:
                lines = file.readlines()

            header_line = 0
            for i, line in enumerate(lines):
                if 'Reading' in line:
                    header_line = i
                    break

            data = pd.read_csv(filename, skiprows=header_line)

        elif file_extension == '.xlsx':
            data = pd.read_excel(filename)

        values = data['Reading'].values[startSamplePoint:endSamplePoint]

        fig, ax = plt.subplots(figsize=(8, 6))
        ax.plot(values, label='Reading')
        ax.set_xlabel('Sample Index')
        ax.set_ylabel('Reading Value')
        ax.set_title('Gas Sensor Reading Preview')
        ax.grid(True)
        plt.tight_layout()

        for widget in plot_frame.winfo_children():
            widget.destroy()

        canvas = FigureCanvasTkAgg(fig, master=plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack()

    except Exception as e:
        messagebox.showerror("Error", str(e))

def display_guide_image():
    try:
        # Path to the image (change this to the path of your image file)
        image_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")])
        if not image_path:
            return

        # Open the image using PIL
        img = Image.open(image_path)
        img = img.resize((600, 400), Image.ANTIALIAS)  # Resize the image to fit the plot frame

        # Convert the image to a format Tkinter can use
        img_tk = ImageTk.PhotoImage(img)

        # Clear previous widgets in the plot_frame
        for widget in plot_frame.winfo_children():
            widget.destroy()

        # Create a label to display the image
        image_label = tk.Label(plot_frame, image=img_tk)
        image_label.image = img_tk  # Keep a reference to avoid garbage collection
        image_label.pack()

    except Exception as e:
        messagebox.showerror("Error", f"Failed to load image: {str(e)}")

def browse_file():
    filename = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx"), ("CSV files", "*.csv")])
    file_entry.delete(0, tk.END)
    file_entry.insert(0, filename)

app = tk.Tk()
app.title("Gas Sensor Data Plotter")

input_frame = tk.Frame(app)
input_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

tk.Label(input_frame, text="Filename:").grid(row=0, column=0, padx=5, pady=5)
file_entry = tk.Entry(input_frame, width=50)
file_entry.grid(row=0, column=1, padx=5, pady=5)
tk.Button(input_frame, text="Browse", command=browse_file).grid(row=0, column=2, padx=5, pady=5)

# Add the new "Guide for Users" button
tk.Button(input_frame, text="Guide for Users", command=display_guide_image).grid(row=1, column=0, columnspan=3, pady=5)

tk.Label(input_frame, text="Start Sample Point:").grid(row=2, column=0, padx=5, pady=5)
start_entry = tk.Entry(input_frame)
start_entry.insert(0, '0')
start_entry.grid(row=2, column=1, padx=5, pady=5)

tk.Label(input_frame, text="End Sample Point:").grid(row=3, column=0, padx=5, pady=5)
end_entry = tk.Entry(input_frame)
end_entry.insert(0, '13000')
end_entry.grid(row=3, column=1, padx=5, pady=5)

tk.Button(input_frame, text="Preview", command=preview_plot).grid(row=4, column=0, columnspan=3, pady=5)

# Additional input fields and buttons continue here...

plot_frame = tk.Frame(app)
plot_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

load_variables()

app.mainloop()