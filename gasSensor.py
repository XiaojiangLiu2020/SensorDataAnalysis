import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import argrelextrema
import numpy as np
import os
import tkinter as tk
from tkinter import filedialog, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageTk
import json
import io
import base64

# 将图片转换为 base64 编码并粘贴在这里
image_data = b''  # 使用工具转换图片文件为 base64 编码，粘贴到这里

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

def display_guide_text():
    try:
        guide_text = "This is the Guide for the User: \n\n1.This App can read .csv and .xlsx file. Only plot one column a time and MAKE SURE START YOUR COLUMN WITH 'Reading'\n\n2. Once select the file you want, set start points and end points to choose the domain of data, and click 'Preview' to see the graph. \n\n3. Based on the preview graph, set the variables properly:\n\n   'Peak Counts' means how many gas pulse you have, make sure graph start with baseline and end with baseline.\n  'Peak Length' refers to the the Length between PeakPoints and GasOut points;'Gas Out Length' refers to the length between GasOut points and the points recovered to baseline;'Gas In Length' refers to the length between GasIn points and Peak points.\n *IMPORTANT* How to set these values? \n    For example, if the largest length between GasIn points and Peak points (The longest response time)on your preview graph is around 300, you should set the 'Gas In Length' larger that that, maybe 400 or 500, a little bit larger is totally fine. The setting rule are the same for other two values. \n  'WindowSize' set the values as 50 at beginning. \n\n4. You can choose x axis in SamplePoints form or in Time form. The response time and recovery time would be influenced by ModeSelection. \n\n5.Once you set all the variables, you can Save Setting and all the variables would be saved.\n\n 6.About the the Calculation: Response = (Rg-Ra)/Ra*100%; ResponseTime is calculated by R90 rule and RecoveryTime is by RT90 rule.\n\n For you to better understand Peak Length, GasIn Length and GasOut Length. First of all, peak is local extremum.\n Lets set x value of peak as e, and the programme would delete the other peaks in (e,e+PeakLength), which aims to filter other local peaks caused by fluctuation.\n In(e-GasInLength,e), the programme would find the GasIn points and T90 points. In (e,e+GasOutLength), find GasOut points and in (e, e+ PeakLength + GasOutLength), find RT90. \n\nv1.3 添加了计算响应时间，恢复时间功能；添加了x轴模式选择；添加了User Guide;优化画图排版  "  # Replace with your guide text
        messagebox.showinfo("User Guide", guide_text)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to display guide: {str(e)}")

def generate_plot():
    try:
        plotting_label.config(text="Plotting...")
        app.update_idletasks()

        filename = file_entry.get()
        startSamplePoint = int(start_entry.get())
        endSamplePoint = int(end_entry.get())
        peaksCounts = int(peaks_entry.get())
        peakLength = int(peak_entry.get())
        gasOutTime = int(gasOut_entry.get())
        gasInTime = int(gasIn_entry.get())
        window_size = int(window_entry.get())
        sample_rate = float(sample_rate_entry.get())
        mode = mode_var.get()

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
        mean_value = np.mean(values)

        if np.sum(values > mean_value) > len(values) / 2:
            mode_type = 'downmode'
            extrema_indices = argrelextrema(values, np.less, order=5)[0]
        else:
            mode_type = 'upmode'
            extrema_indices = argrelextrema(values, np.greater, order=5)[0]

        filtered_extrema_indices = []
        last_index = -peakLength

        for index in extrema_indices:
            if index - last_index >= peakLength:
                filtered_extrema_indices.append(index)
                last_index = index

        starts = []
        for e in filtered_extrema_indices:
            start = max(0, e - gasInTime)
            end = e
            max_diff_slope = 0
            start_index = start
            for i in range(start, end - window_size + 1):
                mid_point = i + window_size // 2
                mean_slope_before = np.mean(np.diff(values[i:mid_point]))
                mean_slope_after = np.mean(np.diff(values[mid_point:mid_point + window_size // 2]))
                diff_slope = abs(mean_slope_after - mean_slope_before)
                if diff_slope > max_diff_slope:
                    max_diff_slope = diff_slope
                    start_index = mid_point
            starts.append(start_index)

        differences = [abs(values[e] - values[s]) for e, s in zip(filtered_extrema_indices, starts)]
        if mode_type == 'downmode':
            valid_pairs = [(diff, e, s) for diff, e, s in zip(differences, filtered_extrema_indices, starts) if
                           values[e] <= values[s]]
        else:
            valid_pairs = [(diff, e, s) for diff, e, s in zip(differences, filtered_extrema_indices, starts) if
                           values[e] >= values[s]]

        valid_pairs.sort(reverse=True, key=lambda x: x[0])
        selected_pairs = valid_pairs[:peaksCounts]

        filtered_extrema_indices = [e for _, e, _ in selected_pairs]
        filtered_starts = [s for _, _, s in selected_pairs]

        responses = []
        filtered_90_responses = []
        response_times = []

        for e, s in zip(filtered_extrema_indices, filtered_starts):
            response = (-values[s] + values[e]) / values[s] * 100
            responses.append(response)

            target_value = (1 + 0.9 * response / 100) * values[s]
            closest_index = s
            closest_value = None

            for i in range(s, e):
                if closest_value is None or abs(values[i] - target_value) < abs(closest_value - target_value):
                    closest_value = values[i]
                    closest_index = i

            filtered_90_responses.append(closest_index)
            response_times.append(closest_index - s)

        release5 = []

        for e in filtered_extrema_indices:
            start = max(0, e - 1 - window_size // 2)
            end = min(len(values), e + gasOutTime)

            max_diff_slope = 0
            release5_index = start
            for i in range(start, end - window_size + 1):
                mid_point = i + window_size // 2
                mean_slope_before = np.mean(np.diff(values[i:mid_point]))
                mean_slope_after = np.mean(np.diff(values[mid_point:mid_point + window_size // 2]))
                diff_slope = abs(mean_slope_after - mean_slope_before)

                if diff_slope > max_diff_slope:
                    max_diff_slope = diff_slope
                    release5_index = mid_point

            release5.append(release5_index)

        recovery_times = []
        rt90_indices = []

        for e, s, resp in zip(filtered_extrema_indices, filtered_starts, responses):
            recovery_base_value = values[s] * (1 + 0.1 * resp / 100)
            start = e
            end = min(len(values), e + gasOutTime)

            closest_index = start
            closest_value = None

            for i in range(start, end):
                if closest_value is None or abs(values[i] - recovery_base_value) < abs(
                        closest_value - recovery_base_value):
                    closest_value = values[i]
                    closest_index = i

            rt90_indices.append(closest_index)
            recovery_times.append(closest_index - e)

        fig, ax = plt.subplots(figsize=(8, 6))
        x_values = np.arange(startSamplePoint, endSamplePoint)

        if mode == "TimeMode":
            x_values = x_values / sample_rate
            ax.set_xlabel('Time (s)')
        else:
            ax.set_xlabel('Sample Index')

        ax.plot(x_values, values, label='Reading')
        ax.margins(y=0.2)

        def format_label(value):
            return f'{value:.4g}'  # Format to 4 significant digits

        y_offset_multiplier = 1 if mode_type == 'downmode' else -1

        if show_peak_value.get():
            ax.scatter(x_values[filtered_extrema_indices], values[filtered_extrema_indices], color='red',
                       label='peakValue')
            for i in filtered_extrema_indices:
                ax.annotate(format_label(values[i]), (x_values[i], values[i]), textcoords="offset points",
                            xytext=(10, -10 * y_offset_multiplier), ha='right', fontsize=8, arrowprops=dict(arrowstyle='->', color='red'))

        if show_gas_in.get():
            ax.scatter(x_values[filtered_starts], values[filtered_starts], color='blue', label='gasIn',
                       marker='^')
            for i in filtered_starts:
                ax.annotate(format_label(values[i]), (x_values[i], values[i]), textcoords="offset points",
                            xytext=(0, 10 * y_offset_multiplier), ha='right', fontsize=8, arrowprops=dict(arrowstyle='->', color='blue'))

        if show_gas_out.get():
            ax.scatter(x_values[release5], values[release5], color='brown', label='gasOut', marker='*')
            for i in release5:
                ax.annotate(format_label(values[i]), (x_values[i], values[i]), textcoords="offset points",
                            xytext=(40, 20 * y_offset_multiplier), ha='right', fontsize=8, arrowprops=dict(arrowstyle='->', color='brown'))

        if show_response.get():
            for i, response in zip(filtered_extrema_indices, responses):
                ax.annotate(f'Resp: {response:.2f}%', (x_values[i], values[i]), textcoords="offset points",
                            xytext=(10, -20 * y_offset_multiplier), ha='right', fontsize=8)

        if show_response_time.get():
            for s, rt, r90 in zip(filtered_starts, response_times, filtered_90_responses):
                response_time_text = rt / sample_rate if mode == "TimeMode" else rt
                ax.annotate(f'T: {response_time_text:.2f}', (x_values[r90], values[r90]),
                            textcoords="offset points", xytext=(5, 5 * y_offset_multiplier), ha='right', fontsize=8)
                ax.scatter(x_values[r90], values[r90], color='green', marker='o')

            ax.scatter([], [], color='green', label='T90', marker='o')

        if show_recovery_time.get():
            for e, rt, rt90 in zip(filtered_extrema_indices, recovery_times, rt90_indices):
                recovery_time_text = rt / sample_rate if mode == "TimeMode" else rt
                ax.annotate(f'RT: {recovery_time_text:.2f}', (x_values[rt90], values[rt90]),
                            textcoords="offset points", xytext=(10, -10 * y_offset_multiplier), ha='right', fontsize=8)
                ax.scatter(x_values[rt90], values[rt90], color='purple', marker='x')

            ax.scatter([], [], color='purple', label='RT90', marker='x')

        ax.set_ylabel('Resistance (ohm)')
        ax.set_title('Gas Sensor Plotting')
        ax.legend(title=f'File: {os.path.basename(filename)}')
        ax.grid(True)
        plt.tight_layout()

        for widget in plot_frame.winfo_children():
            widget.destroy()

        canvas = FigureCanvasTkAgg(fig, master=plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack()

    except Exception as e:
        messagebox.showerror("Error", str(e))
    finally:
        plotting_label.config(text="")

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

tk.Button(input_frame, text="Guide for Users", command=display_guide_text).grid(row=1, column=0, columnspan=3, pady=5)

tk.Label(input_frame, text="Start Sample Point:").grid(row=2, column=0, padx=5, pady=5)
start_entry = tk.Entry(input_frame)
start_entry.insert(0, '0')
start_entry.grid(row=2, column=1, padx=5, pady=5)

tk.Label(input_frame, text="End Sample Point:").grid(row=3, column=0, padx=5, pady=5)
end_entry = tk.Entry(input_frame)
end_entry.insert(0, '13000')
end_entry.grid(row=3, column=1, padx=5, pady=5)

tk.Button(input_frame, text="Preview", command=preview_plot).grid(row=4, column=0, columnspan=3, pady=5)

tk.Label(input_frame, text="Peaks Counts:").grid(row=5, column=0, padx=5, pady=5)
peaks_entry = tk.Entry(input_frame)
peaks_entry.insert(0, '4')
peaks_entry.grid(row=5, column=1, padx=5, pady=5)

tk.Label(input_frame, text="Peak Length:").grid(row=6, column=0, padx=5, pady=5)
peak_entry = tk.Entry(input_frame)
peak_entry.insert(0, '500')
peak_entry.grid(row=6, column=1, padx=5, pady=5)

tk.Label(input_frame, text="Gas Out Length:").grid(row=7, column=0, padx=5, pady=5)
gasOut_entry = tk.Entry(input_frame)
gasOut_entry.insert(0, '700')
gasOut_entry.grid(row=7, column=1, padx=5, pady=5)

tk.Label(input_frame, text="Gas In Length:").grid(row=8, column=0, padx=5, pady=5)
gasIn_entry = tk.Entry(input_frame)
gasIn_entry.insert(0, '700')
gasIn_entry.grid(row=8, column=1, padx=5, pady=5)

tk.Label(input_frame, text="Window Size:").grid(row=9, column=0, padx=5, pady=5)
window_entry = tk.Entry(input_frame)
window_entry.insert(0, '200')
window_entry.grid(row=9, column=1, padx=5, pady=5)

sample_rate_label = tk.Label(input_frame, text="Sample Rate (Samples/s):")
sample_rate_label.grid(row=12, column=1, padx=5, pady=5)
sample_rate_entry = tk.Entry(input_frame)
sample_rate_entry.insert(0, '1')
sample_rate_entry.grid(row=12, column=2, padx=5, pady=5)

show_peak_value = tk.IntVar(value=1)
show_gas_in = tk.IntVar(value=1)
show_gas_out = tk.IntVar(value=1)
show_response = tk.IntVar(value=1)
show_response_time = tk.IntVar(value=1)
show_recovery_time = tk.IntVar(value=1)

tk.Checkbutton(input_frame, text="Show Peak Value", variable=show_peak_value).grid(row=11, column=0, columnspan=2,sticky='w')
tk.Checkbutton(input_frame, text="Show Gas In", variable=show_gas_in).grid(row=12, column=0, columnspan=2,sticky='w')
tk.Checkbutton(input_frame, text="Show Gas Out", variable=show_gas_out).grid(row=13, column=0, columnspan=2,sticky='w')
tk.Checkbutton(input_frame, text="Show Response", variable=show_response).grid(row=14, column=0, columnspan=2,sticky='w')
tk.Checkbutton(input_frame, text="Show Response Time", variable=show_response_time).grid(row=15, column=0, columnspan=2,sticky='w')
tk.Checkbutton(input_frame, text="Show Recovery Time", variable=show_recovery_time).grid(row=16, column=0, columnspan=2,sticky='w')

mode_var = tk.StringVar(value="SamplePoints")
mode_menu = tk.OptionMenu(input_frame, mode_var, "SamplesMode", "TimeMode")
mode_menu.grid(row=11, column=1, columnspan=2)

plotting_label = tk.Label(input_frame, text="")
plotting_label.grid(row=18, column=0, columnspan=3)

tk.Button(input_frame, text="Generate Plot", command=generate_plot).grid(row=19, column=0, columnspan=3, pady=10)
tk.Button(input_frame, text="Save Settings", command=save_variables).grid(row=20, column=0, columnspan=3, pady=5)

plot_frame = tk.Frame(app)
plot_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

load_variables()

app.mainloop()