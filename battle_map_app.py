import sys
import os
import folium
import pandas as pd
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QMessageBox
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile

class MapApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Interactive Battle Map")

        # Set a custom cache path to avoid permission issues
        cache_path = os.path.join(os.getcwd(), 'QtWebEngine_Cache')
        if not os.path.exists(cache_path):
            os.makedirs(cache_path)

        profile = QWebEngineProfile.defaultProfile()
        profile.setCachePath(cache_path)
        profile.setPersistentStoragePath(cache_path)

        # Directly reference the CSV file by name
        csv_file = 'Top_25_Battles_Updated.csv'  # Ensure this file is in the same directory as your script

        # Load the battle data
        try:
            df = pd.read_csv(csv_file)
        except Exception as e:
            QMessageBox.critical(self, "Error Loading CSV", f"Failed to load CSV file: {e}")
            sys.exit()

        # Check if 'Latitude' and 'Longitude' columns exist
        if 'Latitude' not in df.columns or 'Longitude' not in df.columns:
            QMessageBox.critical(self, "Missing Columns", "The CSV file does not contain 'Latitude' and 'Longitude' columns.")
            sys.exit()

        # Create the folium map centered around a rough center point (e.g., Europe)
        battle_map = folium.Map(location=[50, 10], zoom_start=3)

        # Function to manually format the date in MM-DD-YYYY format
        def format_date(date_str):
            try:
                parts = date_str.split('-')
                if len(parts) == 3:
                    return f"{parts[1]}-{parts[2]}-{parts[0]}"
                return date_str
            except Exception:
                return date_str

        # Function to format numbers with commas and labels
        def format_number(number, label='participants'):
            return f"{number:,} {label}"

        # Function to format faction data for readability
        def format_factions(factions):
            # Ensure factions is a list of strings, then join with line breaks
            if isinstance(factions, str):
                factions = eval(factions)  # Convert string representation of list to an actual list
            return "<br>".join(factions)

        # Function to create a popup with battle details
        def create_popup(row):
            popup_content = f"""
            <h4>{row['Battle Name']} ({format_date(row['Date'])})</h4>
            <p><b>Location:</b> {row['Location']}</p>
            <p><b>Total Participants:</b> {format_number(row['Total Participants'])}</p>
            <p><b>Side A Participants:</b> {format_number(row['Side A Participants'])} ({format_factions(row['Side A Factions'])})</p>
            <p><b>Side B Participants:</b> {format_number(row['Side B Participants'])} ({format_factions(row['Side B Factions'])})</p>
            <p><b>Flags/Markings:</b> <br> 
            <img src="{row['Flags/Markings Side A']}" alt="Flag A" width="50" height="30"> 
            <img src="{row['Flags/Markings Side B']}" alt="Flag B" width="50" height="30">
            </p>
            """
            return folium.Popup(popup_content, max_width=450)

        # Loop through the DataFrame and add markers for each battle
        for index, row in df.iterrows():
            folium.Marker(
                location=[row['Latitude'], row['Longitude']],  # Use the GPS coordinates
                popup=create_popup(row),
                tooltip=f"{row['Battle Name']} ({format_date(row['Date'])[:4]})"
            ).add_to(battle_map)

            # Add label (battle name) next to each marker
            folium.Marker(
                location=[row['Latitude'], row['Longitude']],  # Use the GPS coordinates
                icon=folium.DivIcon(
                    html=f"""<div style="font-size: 12px; font-weight: bold;">{row['Battle Name']}</div>"""
                )
            ).add_to(battle_map)

        # Save the map to an HTML file
        map_file = 'battle_map.html'
        battle_map.save(map_file)

        # Set up the QWebEngineView widget
        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl.fromLocalFile(os.path.abspath(map_file)))

        # Set the layout
        layout = QVBoxLayout()
        layout.addWidget(self.browser)

        # Set the central widget
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MapApp()
    main_window.show()
    sys.exit(app.exec_())
