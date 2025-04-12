import tkinter as tk
from tkinter import ttk
import psutil
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import deque
import time
import platform
import subprocess

class SystemMonitor:
    def __init__(self, root):
        self.root = root
        self.root.title("System Monitor")
        self.root.configure(bg='#727070')
        
        # Initialize data storage
        self.latency_history = deque(maxlen=10)  # Last 10 measurements
        self.time_points = deque(maxlen=10)      # Stores time indices
        self.cpu_percent = 0
        self.ram_percent = 0
        self.disk_percent = 0
        self.net_latency = 0
        self.update_counter = 0
        
        # Setup GUI
        self.create_widgets()
        self.update_interval = 1000  # 1 second
        
        # Start updates
        self.update_data()

    def create_widgets(self):
        # Create main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.configure(style='Dark.TFrame')
        
        # Custom style configuration
        style = ttk.Style()
        style.configure('Dark.TFrame', background='#727070')
        style.configure('Dark.TLabel', background='#727070', foreground='white')
        
        # Stats labels
        stats_frame = ttk.LabelFrame(main_frame, text="Current Status", padding="10", style='Dark.TFrame')
        stats_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        self.cpu_label = ttk.Label(stats_frame, text="CPU Usage: -", style='Dark.TLabel')
        self.cpu_label.grid(row=0, column=0, sticky=tk.W)
        
        self.ram_label = ttk.Label(stats_frame, text="RAM Usage: -", style='Dark.TLabel')
        self.ram_label.grid(row=1, column=0, sticky=tk.W)
        
        self.disk_label = ttk.Label(stats_frame, text="Disk Usage: -", style='Dark.TLabel')
        self.disk_label.grid(row=2, column=0, sticky=tk.W)
        
        self.net_label = ttk.Label(stats_frame, text="Network Latency: -", style='Dark.TLabel')
        self.net_label.grid(row=3, column=0, sticky=tk.W)
        
        # Graph frame
        graph_frame = ttk.Frame(main_frame, style='Dark.TFrame')
        graph_frame.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Create 2x2 grid of subplots
        self.fig = plt.figure(figsize=(8, 6), facecolor='#727070')
        self.axs = [
            self.fig.add_subplot(221),
            self.fig.add_subplot(222),
            self.fig.add_subplot(223),
            self.fig.add_subplot(224)
        ]
        
        # Configure plot appearance
        for ax in self.axs:
            ax.set_facecolor('#727070')
            ax.tick_params(axis='both', colors='white', labelsize=8)
            for spine in ax.spines.values():
                spine.set_color('white')
        
        # Special configuration for latency graph
        self.axs[3].set_xlabel('Time Sequence', color='white', fontsize=8)
        self.axs[3].set_ylabel('Latency (ms)', color='white', fontsize=8)
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=graph_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def get_network_latency(self):
        try:
            # Windows-specific flags to hide console window
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            
            param = '-n' if platform.system().lower() == 'windows' else '-c'
            command = ['ping', param, '1', '8.8.8.8']
            
            output = subprocess.check_output(
                command,
                timeout=0.8,
                startupinfo=startupinfo,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NO_WINDOW if platform.system() == 'Windows' else 0
            ).decode(errors='ignore')

            # Parse different ping output formats
            if 'time=' in output:
                time_part = output.split('time=')[-1].split()[0]
                latency = float(time_part.replace('ms', ''))
            elif 'time<' in output:
                time_part = output.split('time<')[-1].split()[0]
                latency = float(time_part.replace('ms', ''))
            else:
                return None
                
            return latency
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired,
                ValueError, IndexError, UnicodeDecodeError):
            return None
        

    def update_data(self):
        # Get metrics
        self.cpu_percent = psutil.cpu_percent()
        self.ram_percent = psutil.virtual_memory().percent
        self.disk_percent = psutil.disk_usage('/').percent
        net_latency = self.get_network_latency()
        
        # Update latency data with time indices
        if net_latency is not None:
            self.net_latency = net_latency
            self.time_points.append(self.update_counter)
            self.latency_history.append(net_latency)
            self.update_counter += 1
        
        # Update labels
        self.cpu_label.config(text=f"CPU Usage: {self.cpu_percent}%")
        self.ram_label.config(text=f"RAM Usage: {self.ram_percent}%")
        self.disk_label.config(text=f"Disk Usage: {self.disk_percent}%")
        latency_text = f"{self.net_latency:.1f} ms" if net_latency else "Timeout"
        self.net_label.config(text=f"Network Latency: {latency_text}")
        
        # Update plots
        self.update_plots()
        
        # Schedule next update
        self.root.after(self.update_interval, self.update_data)

    def update_plots(self):
        # Donut charts for system resources
        metrics = [
            (self.axs[0], "CPU Usage", self.cpu_percent, 100),
            (self.axs[1], "RAM Usage", self.ram_percent, 100),
            (self.axs[2], "Disk Usage", self.disk_percent, 100)
        ]
        
        for ax, title, value, max_val in metrics:
            ax.clear()
            remaining = max(0, max_val - value)
            wedges, _ = ax.pie(
                [value, remaining],
                colors=['#1775A4', 'white'],
                startangle=90,
                wedgeprops={
                    'width': 0.4,
                    'edgecolor': '#727070',
                    'linewidth': 0.5
                }
            )
            ax.set_title(title, color='white', pad=10, fontsize=10)
            ax.text(0, 0, f'{value:.1f}%', 
                    ha='center', va='center', 
                    color='white', fontsize=9)
            ax.axis('equal')
            ax.set_xticks([])
            ax.set_yticks([])
        
        # Updated latency line graph
        self.axs[3].clear()
        if self.latency_history:
            self.axs[3].plot(
                self.time_points,
                self.latency_history,
                color='#1775A4',
                linestyle='-',
                linewidth=1,
                marker='o',
                markersize=4,
                markerfacecolor='white'
            )
            
            # Configure axes
            self.axs[3].set_title('Network Latency History', color='white', pad=10, fontsize=10)
            self.axs[3].set_ylim(0, max(self.latency_history) * 1.2)
            self.axs[3].grid(True, color='white', alpha=0.2)
            
            # Handle x-axis ticks
            if len(self.time_points) > 0:
                visible_ticks = list(self.time_points)[::2]  # Show every other tick
                self.axs[3].set_xticks(visible_ticks)
                self.axs[3].set_xticklabels(
                    [str(t) for t in visible_ticks],
                    rotation=45,
                    fontsize=7
                )
        
        self.fig.tight_layout()
        self.canvas.draw()

if __name__ == "__main__":
    root = tk.Tk()
    app = SystemMonitor(root)
    root.mainloop()
