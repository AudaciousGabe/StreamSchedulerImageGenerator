#!/usr/bin/env python3
"""
StreamSchedulerManager.py
Manages configuration for the Stream Schedule Image Generator with a Flask server and Tkinter UI.
"""

import json
import webbrowser
import sys
import threading
import time
from pathlib import Path
from flask import Flask, jsonify, request
from flask_cors import CORS
import tkinter as tk
from tkinter import ttk, messagebox, font
import tkinter.colorchooser as colorchooser

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

class StreamSchedulerManager:
    def __init__(self):
        self.script_dir = Path(__file__).parent
        self.config_file = self.script_dir / "config.json"
        self.html_file = self.script_dir / "StreamSchedulerImageGenerator.html"
        self.config = self.load_config()
        self.server_thread = None
        self.root = None
        
    def load_config(self):
        """Load configuration from JSON file."""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
        
        # Default configuration
        return {
            "channel": {
                "name": "AudaciousJr",
                "link": "https://www.twitch.tv/audaciousjr"
            },
            "theme": "twilight",
            "timezone": "EST",
            "schedule": {
                "today": {"type": "normal", "title": "Today's Stream"},
                "tomorrow": {"type": "work", "title": "Tomorrow's Stream"}
            }
        }
    
    def save_config(self):
        """Save configuration to JSON file."""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
    
    def start_server(self):
        """Start the Flask server in a separate thread."""
        def run_server():
            app.run(host='127.0.0.1', port=5555, debug=False, use_reloader=False)
        
        self.server_thread = threading.Thread(target=run_server, daemon=True)
        self.server_thread.start()
        print("Local server started on http://127.0.0.1:5555")
    
    def open_html(self):
        """Open the HTML file in the browser."""
        try:
            if not self.html_file.exists():
                messagebox.showerror("Error", f"HTML file not found at {self.html_file}")
                return False
            
            # Open with server URL instead of file URL
            webbrowser.open(f"file:///{self.html_file.absolute()}")
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open HTML: {e}")
            return False
    
    def create_gui(self):
        """Create the Tkinter GUI."""
        self.root = tk.Tk()
        self.root.title("Stream Scheduler Manager")
        self.root.geometry("600x700")
        
        # Configure styles
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure dark theme colors
        bg_color = "#1a1a2e"
        fg_color = "#eee"
        accent_color = "#9146FF"  # Twitch purple
        button_bg = "#16213e"
        entry_bg = "#0f3460"
        
        self.root.configure(bg=bg_color)
        
        # Custom fonts
        title_font = font.Font(family="Segoe UI", size=16, weight="bold")
        header_font = font.Font(family="Segoe UI", size=12, weight="bold")
        normal_font = font.Font(family="Segoe UI", size=10)
        
        # Main container with padding
        main_frame = tk.Frame(self.root, bg=bg_color, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = tk.Label(
            main_frame,
            text="🎮 Stream Scheduler Manager",
            font=title_font,
            bg=bg_color,
            fg=accent_color
        )
        title_label.pack(pady=(0, 20))
        
        # Server Status Frame
        status_frame = tk.LabelFrame(
            main_frame,
            text="Server Status",
            font=header_font,
            bg=bg_color,
            fg=fg_color,
            relief=tk.GROOVE,
            borderwidth=2
        )
        status_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.status_label = tk.Label(
            status_frame,
            text="● Server running on http://127.0.0.1:5555",
            font=normal_font,
            bg=bg_color,
            fg="#50fa7b"  # Green for active
        )
        self.status_label.pack(pady=10, padx=10)
        
        # Channel Configuration Frame
        channel_frame = tk.LabelFrame(
            main_frame,
            text="Channel Configuration",
            font=header_font,
            bg=bg_color,
            fg=fg_color,
            relief=tk.GROOVE,
            borderwidth=2
        )
        channel_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Channel Name
        tk.Label(
            channel_frame,
            text="Channel Name:",
            font=normal_font,
            bg=bg_color,
            fg=fg_color
        ).grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        
        self.name_entry = tk.Entry(
            channel_frame,
            font=normal_font,
            bg=entry_bg,
            fg=fg_color,
            insertbackground=fg_color,
            relief=tk.FLAT,
            width=30
        )
        self.name_entry.grid(row=0, column=1, padx=10, pady=5)
        self.name_entry.insert(0, self.config["channel"]["name"])
        
        # Channel Link
        tk.Label(
            channel_frame,
            text="Twitch Link:",
            font=normal_font,
            bg=bg_color,
            fg=fg_color
        ).grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
        
        self.link_entry = tk.Entry(
            channel_frame,
            font=normal_font,
            bg=entry_bg,
            fg=fg_color,
            insertbackground=fg_color,
            relief=tk.FLAT,
            width=30
        )
        self.link_entry.grid(row=1, column=1, padx=10, pady=5)
        self.link_entry.insert(0, self.config["channel"]["link"])
        
        # Theme Selection Frame
        theme_frame = tk.LabelFrame(
            main_frame,
            text="Theme Selection",
            font=header_font,
            bg=bg_color,
            fg=fg_color,
            relief=tk.GROOVE,
            borderwidth=2
        )
        theme_frame.pack(fill=tk.X, pady=(0, 15))
        
        themes = [
            ("Twilight", "twilight", "#9146FF"),
            ("Sunrise", "sunrise", "#F97316"),
            ("Forest", "forest", "#10B981"),
            ("Oceanic", "oceanic", "#0EA5E9"),
            ("Cyberpunk", "cyberpunk", "#EC4899"),
            ("Pastel", "pastel", "#A78BFA"),
            ("Arctic", "arctic", "#06B6D4")
        ]
        
        self.theme_var = tk.StringVar(value=self.config.get("theme", "twilight"))
        
        theme_buttons_frame = tk.Frame(theme_frame, bg=bg_color)
        theme_buttons_frame.pack(pady=10)
        
        for i, (display_name, theme_value, color) in enumerate(themes):
            row = i // 4
            col = i % 4
            btn = tk.Radiobutton(
                theme_buttons_frame,
                text=display_name,
                variable=self.theme_var,
                value=theme_value,
                font=normal_font,
                bg=bg_color,
                fg=fg_color,
                selectcolor=button_bg,
                activebackground=bg_color,
                activeforeground=color,
                indicatoron=0,
                width=12,
                relief=tk.FLAT,
                bd=1
            )
            btn.grid(row=row, column=col, padx=5, pady=5)
        
        # Schedule Type Frame
        schedule_frame = tk.LabelFrame(
            main_frame,
            text="Schedule Type",
            font=header_font,
            bg=bg_color,
            fg=fg_color,
            relief=tk.GROOVE,
            borderwidth=2
        )
        schedule_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Today's schedule type
        tk.Label(
            schedule_frame,
            text="Today:",
            font=normal_font,
            bg=bg_color,
            fg=fg_color
        ).grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        
        self.today_type = tk.StringVar(value=self.config["schedule"]["today"]["type"])
        today_frame = tk.Frame(schedule_frame, bg=bg_color)
        today_frame.grid(row=0, column=1, padx=10, pady=5)
        
        tk.Radiobutton(
            today_frame,
            text="Normal",
            variable=self.today_type,
            value="normal",
            font=normal_font,
            bg=bg_color,
            fg=fg_color,
            selectcolor=button_bg
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Radiobutton(
            today_frame,
            text="Work",
            variable=self.today_type,
            value="work",
            font=normal_font,
            bg=bg_color,
            fg=fg_color,
            selectcolor=button_bg
        ).pack(side=tk.LEFT, padx=5)
        
        # Tomorrow's schedule type
        tk.Label(
            schedule_frame,
            text="Tomorrow:",
            font=normal_font,
            bg=bg_color,
            fg=fg_color
        ).grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
        
        self.tomorrow_type = tk.StringVar(value=self.config["schedule"]["tomorrow"]["type"])
        tomorrow_frame = tk.Frame(schedule_frame, bg=bg_color)
        tomorrow_frame.grid(row=1, column=1, padx=10, pady=5)
        
        tk.Radiobutton(
            tomorrow_frame,
            text="Normal",
            variable=self.tomorrow_type,
            value="normal",
            font=normal_font,
            bg=bg_color,
            fg=fg_color,
            selectcolor=button_bg
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Radiobutton(
            tomorrow_frame,
            text="Work",
            variable=self.tomorrow_type,
            value="work",
            font=normal_font,
            bg=bg_color,
            fg=fg_color,
            selectcolor=button_bg
        ).pack(side=tk.LEFT, padx=5)
        
        # Action Buttons Frame
        button_frame = tk.Frame(main_frame, bg=bg_color)
        button_frame.pack(fill=tk.X, pady=20)
        
        # Save button
        save_btn = tk.Button(
            button_frame,
            text="💾 Save Configuration",
            font=header_font,
            bg=accent_color,
            fg="white",
            relief=tk.FLAT,
            padx=20,
            pady=10,
            command=self.save_configuration
        )
        save_btn.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        
        # Open HTML button
        open_btn = tk.Button(
            button_frame,
            text="🌐 Open Schedule Generator",
            font=header_font,
            bg="#50fa7b",
            fg=bg_color,
            relief=tk.FLAT,
            padx=20,
            pady=10,
            command=self.open_html
        )
        open_btn.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        
        # Reload button
        reload_btn = tk.Button(
            button_frame,
            text="🔄 Reload Config",
            font=header_font,
            bg="#6272a4",
            fg="white",
            relief=tk.FLAT,
            padx=20,
            pady=10,
            command=self.reload_configuration
        )
        reload_btn.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        
        # Footer
        footer_label = tk.Label(
            main_frame,
            text="Server API: http://127.0.0.1:5555/api/config",
            font=normal_font,
            bg=bg_color,
            fg="#6272a4"
        )
        footer_label.pack(side=tk.BOTTOM, pady=(10, 0))
    
    def save_configuration(self):
        """Save the current GUI configuration."""
        self.config["channel"]["name"] = self.name_entry.get()
        self.config["channel"]["link"] = self.link_entry.get()
        self.config["theme"] = self.theme_var.get()
        self.config["schedule"]["today"]["type"] = self.today_type.get()
        self.config["schedule"]["tomorrow"]["type"] = self.tomorrow_type.get()
        
        if self.save_config():
            messagebox.showinfo("Success", "Configuration saved successfully!")
        else:
            messagebox.showerror("Error", "Failed to save configuration!")
    
    def reload_configuration(self):
        """Reload configuration from file."""
        self.config = self.load_config()
        
        # Update GUI fields
        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, self.config["channel"]["name"])
        
        self.link_entry.delete(0, tk.END)
        self.link_entry.insert(0, self.config["channel"]["link"])
        
        self.theme_var.set(self.config.get("theme", "twilight"))
        self.today_type.set(self.config["schedule"]["today"]["type"])
        self.tomorrow_type.set(self.config["schedule"]["tomorrow"]["type"])
        
        messagebox.showinfo("Success", "Configuration reloaded!")
    
    def run(self):
        """Run the application."""
        # Start the Flask server
        self.start_server()
        
        # Give server time to start
        time.sleep(1)
        
        # Create and run GUI
        self.create_gui()
        
        # Open HTML automatically
        self.open_html()
        
        # Start GUI main loop
        self.root.mainloop()

# Flask routes
manager = None

@app.route('/api/config', methods=['GET'])
def get_config():
    """API endpoint to get the current configuration."""
    if manager:
        return jsonify(manager.config)
    return jsonify({"error": "Manager not initialized"}), 500

@app.route('/api/config', methods=['POST'])
def update_config():
    """API endpoint to update the configuration."""
    if manager:
        data = request.json
        manager.config.update(data)
        manager.save_config()
        return jsonify({"status": "success", "config": manager.config})
    return jsonify({"error": "Manager not initialized"}), 500

def main():
    """Main function."""
    global manager
    manager = StreamSchedulerManager()
    
    try:
        manager.run()
    except KeyboardInterrupt:
        print("\nShutting down...")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
