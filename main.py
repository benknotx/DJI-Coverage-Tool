import os
import pandas as pd
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog, messagebox
import folium
import webbrowser
from folium.plugins import HeatMap

def parse_mrk_file(filepath, folder_name):
    data = []
    with open(filepath, 'r') as f:
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) >= 8:
                try:
                    row_num = int(parts[0])
                    lat_str = parts[6]
                    lon_str = parts[7]
                    lat = float(lat_str.split(',')[0])
                    lon = float(lon_str.split(',')[0])
                    unique_row = f"{folder_name}.{row_num}"
                    data.append({'unique_row': unique_row, 'lat': lat, 'lon': lon})
                except (ValueError, IndexError):
                    continue  # Skip invalid lines
    return data

class CoverageCheckerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("DJI Coverage Checker V1.0")
        self.geometry("500x300")
        self.folder_path = None

        # Select folder button
        self.select_btn = tk.Button(self, text="Select Root Folder", command=self.select_folder)
        self.select_btn.pack(pady=10)

        self.folder_label = tk.Label(self, text="No folder selected", wraplength=400)
        self.folder_label.pack(pady=5)

        # Options frame
        options_frame = tk.Frame(self)
        options_frame.pack(pady=20)

        self.scatter_btn = tk.Button(options_frame, text="Scatter Plot", command=self.generate_scatter, state=tk.DISABLED)
        self.scatter_btn.pack(side=tk.LEFT, padx=10)

        self.map_btn = tk.Button(options_frame, text="Visual Map", command=self.generate_map, state=tk.DISABLED)
        self.map_btn.pack(side=tk.LEFT, padx=10)

        self.heatmap_btn = tk.Button(options_frame, text="Generate Heatmap", command=self.generate_heatmap, state=tk.DISABLED)
        self.heatmap_btn.pack(side=tk.LEFT, padx=10)

    def select_folder(self):
        folder = filedialog.askdirectory(title="Select the root folder containing subfolders with MRK files")
        if folder:
            self.folder_path = folder
            self.folder_label.config(text=f"Selected: {os.path.basename(folder)}")
            self.scatter_btn.config(state=tk.NORMAL)
            self.map_btn.config(state=tk.NORMAL)
            self.heatmap_btn.config(state=tk.NORMAL)
            self.map_btn.config(state=tk.NORMAL)

    def generate_scatter(self):
        if not self.folder_path:
            return

        all_data = []
        for subdir, dirs, files in os.walk(self.folder_path):
            mrk_files = [f for f in files if f.lower().endswith('.mrk')]
            if len(mrk_files) == 1:
                mrk_path = os.path.join(subdir, mrk_files[0])
                folder_name = os.path.basename(subdir)
                data = parse_mrk_file(mrk_path, folder_name)
                all_data.extend(data)
            elif len(mrk_files) > 1:
                messagebox.showwarning("Warning", f"Multiple MRK files in {subdir}, skipping.")

        if not all_data:
            messagebox.showerror("Error", "No valid MRK files found.")
            return

        df = pd.DataFrame(all_data)

        plt.figure(figsize=(10, 8))
        plt.scatter(df['lon'], df['lat'], alpha=0.5)
        plt.xlabel('Longitude')
        plt.ylabel('Latitude')
        plt.title('GPS Points Scatter Plot')
        plt.grid(True)
        plt.axis('equal')
        plt.show()

    def generate_map(self):
        if not self.folder_path:
            return

        all_data = []
        for subdir, dirs, files in os.walk(self.folder_path):
            mrk_files = [f for f in files if f.lower().endswith('.mrk')]
            if len(mrk_files) == 1:
                mrk_path = os.path.join(subdir, mrk_files[0])
                folder_name = os.path.basename(subdir)
                data = parse_mrk_file(mrk_path, folder_name)
                all_data.extend(data)
            elif len(mrk_files) > 1:
                messagebox.showwarning("Warning", f"Multiple MRK files in {subdir}, skipping.")

        if not all_data:
            messagebox.showerror("Error", "No valid MRK files found.")
            return

        df = pd.DataFrame(all_data)

        # Create Folium map
        avg_lat = df['lat'].mean()
        avg_lon = df['lon'].mean()
        m = folium.Map(location=[avg_lat, avg_lon], zoom_start=13, tiles='CartoDB positron')

        # Add markers for each point
        for _, row in df.iterrows():
            folium.CircleMarker(
                [row['lat'], row['lon']],
                radius=3,
                color='blue',
                fill=True,
                fill_color='blue',
                popup=row['unique_row']
            ).add_to(m)

        # Save and open the map
        map_file = os.path.join(self.folder_path, 'coverage_map.html')
        m.save(map_file)
        webbrowser.open(map_file)
        messagebox.showinfo("Map Generated", f"Map saved as {map_file} and opened in your default browser.")

    def generate_heatmap(self):
        if not self.folder_path:
            return

        all_data = []
        for subdir, dirs, files in os.walk(self.folder_path):
            mrk_files = [f for f in files if f.lower().endswith('.mrk')]
            if len(mrk_files) == 1:
                mrk_path = os.path.join(subdir, mrk_files[0])
                folder_name = os.path.basename(subdir)
                data = parse_mrk_file(mrk_path, folder_name)
                all_data.extend(data)
            elif len(mrk_files) > 1:
                messagebox.showwarning("Warning", f"Multiple MRK files in {subdir}, skipping.")

        if not all_data:
            messagebox.showerror("Error", "No valid MRK files found.")
            return

        df = pd.DataFrame(all_data)

        # Create Folium heatmap
        avg_lat = df['lat'].mean()
        avg_lon = df['lon'].mean()
        m = folium.Map(location=[avg_lat, avg_lon], zoom_start=13, tiles='CartoDB positron')

        # Prepare data for heatmap (list of [lat, lon] pairs)
        heat_data = [[row['lat'], row['lon']] for _, row in df.iterrows()]

        # Add heatmap layer
        HeatMap(heat_data).add_to(m)

        # Save and open the heatmap
        heatmap_file = os.path.join(self.folder_path, 'coverage_heatmap.html')
        m.save(heatmap_file)
        webbrowser.open(heatmap_file)
        messagebox.showinfo("Heatmap Generated", f"Heatmap saved as {heatmap_file} and opened in your default browser.")

if __name__ == "__main__":
    app = CoverageCheckerApp()
    app.mainloop()