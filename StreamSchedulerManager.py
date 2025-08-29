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
                "name": "Audacious Gabe",
                "link": "https://www.twitch.tv/audaciousgabe"
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
        self.root.geometry("880x700")
        
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
        
        # Create canvas and scrollbar for scrolling
        canvas = tk.Canvas(self.root, bg=bg_color, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=bg_color)
        
        # Configure canvas to center content
        def configure_canvas(e=None):
            canvas.configure(scrollregion=canvas.bbox("all"))
            # Center the frame horizontally
            canvas_width = canvas.winfo_width()
            frame_width = scrollable_frame.winfo_reqwidth()
            if canvas_width > frame_width:
                x = (canvas_width - frame_width) // 2
            else:
                x = 0
            canvas.coords(frame_window_id, x, 0)
        
        scrollable_frame.bind("<Configure>", configure_canvas)
        frame_window_id = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Update canvas when window is resized
        canvas.bind("<Configure>", configure_canvas)
        
        # Main container with padding
        main_frame = tk.Frame(scrollable_frame, bg=bg_color, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mousewheel for scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Title
        title_label = tk.Label(
            main_frame,
            text="Stream Scheduler Manager",
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
        
        # Export Scope Setting
        export_frame = tk.Frame(schedule_frame, bg=bg_color)
        export_frame.grid(row=2, column=0, columnspan=2, pady=(10, 5))
        
        tk.Label(
            export_frame,
            text="Export Scope:",
            font=normal_font,
            bg=bg_color,
            fg=fg_color
        ).pack(side=tk.LEFT, padx=(10, 5))
        
        self.export_scope = tk.StringVar(value="full")
        tk.Radiobutton(
            export_frame,
            text="Today Only",
            variable=self.export_scope,
            value="today",
            font=normal_font,
            bg=bg_color,
            fg=fg_color,
            selectcolor=button_bg
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Radiobutton(
            export_frame,
            text="Full Schedule",
            variable=self.export_scope,
            value="full",
            font=normal_font,
            bg=bg_color,
            fg=fg_color,
            selectcolor=button_bg
        ).pack(side=tk.LEFT, padx=5)
        
        # Content Editor Frame
        editor_frame = tk.LabelFrame(
            main_frame,
            text="Content Editor",
            font=header_font,
            bg=bg_color,
            fg=fg_color,
            relief=tk.GROOVE,
            borderwidth=2
        )
        editor_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Timezone setting
        tz_frame = tk.Frame(editor_frame, bg=bg_color)
        tz_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        tk.Label(
            tz_frame,
            text="Timezone Text:",
            font=normal_font,
            bg=bg_color,
            fg=fg_color
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.timezone_entry = tk.Entry(
            tz_frame,
            font=normal_font,
            bg=entry_bg,
            fg=fg_color,
            insertbackground=fg_color,
            relief=tk.FLAT,
            width=30
        )
        self.timezone_entry.pack(side=tk.LEFT)
        self.timezone_entry.insert(0, self.config.get("timezone", "EST"))
        
        # Editor Tabs
        tab_frame = tk.Frame(editor_frame, bg=bg_color)
        tab_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.active_tab = tk.StringVar(value="today")
        
        today_tab_btn = tk.Button(
            tab_frame,
            text="Edit Today",
            font=normal_font,
            bg=accent_color if self.active_tab.get() == "today" else button_bg,
            fg="white",
            relief=tk.FLAT,
            padx=15,
            pady=5,
            command=lambda: self.switch_tab("today", today_tab_btn, tomorrow_tab_btn, today_edit_frame, tomorrow_edit_frame, accent_color, button_bg)
        )
        today_tab_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        tomorrow_tab_btn = tk.Button(
            tab_frame,
            text="Edit Tomorrow",
            font=normal_font,
            bg=button_bg,
            fg="white",
            relief=tk.FLAT,
            padx=15,
            pady=5,
            command=lambda: self.switch_tab("tomorrow", today_tab_btn, tomorrow_tab_btn, today_edit_frame, tomorrow_edit_frame, accent_color, button_bg)
        )
        tomorrow_tab_btn.pack(side=tk.LEFT)
        
        # Today's Editor
        today_edit_frame = tk.Frame(editor_frame, bg=bg_color)
        today_edit_frame.pack(fill=tk.X, padx=10, pady=(5, 10))
        
        # Today's Title
        tk.Label(
            today_edit_frame,
            text="Today's Title:",
            font=normal_font,
            bg=bg_color,
            fg=fg_color
        ).grid(row=0, column=0, sticky=tk.W, pady=2)
        
        self.today_title_entry = tk.Entry(
            today_edit_frame,
            font=normal_font,
            bg=entry_bg,
            fg=fg_color,
            insertbackground=fg_color,
            relief=tk.FLAT,
            width=50
        )
        self.today_title_entry.grid(row=0, column=1, pady=2, padx=(10, 0))
        self.today_title_entry.insert(0, "Today's Stream")
        
        # Today's Normal Schedule
        tk.Label(
            today_edit_frame,
            text="Normal Day:",
            font=normal_font,
            bg=bg_color,
            fg=fg_color
        ).grid(row=1, column=0, sticky=tk.W, pady=(10, 2))
        
        # Store entries for later access
        self.today_normal_entries = {}
        for i in range(1, 5):
            tk.Label(
                today_edit_frame,
                text=f"  Slot {i}:",
                font=normal_font,
                bg=bg_color,
                fg=fg_color
            ).grid(row=1+i, column=0, sticky=tk.W, pady=1)
            
            title_entry = tk.Entry(
                today_edit_frame,
                font=normal_font,
                bg=entry_bg,
                fg=fg_color,
                insertbackground=fg_color,
                relief=tk.FLAT,
                width=20
            )
            title_entry.grid(row=1+i, column=1, pady=1, padx=(10, 5))
            
            desc_entry = tk.Entry(
                today_edit_frame,
                font=normal_font,
                bg=entry_bg,
                fg=fg_color,
                insertbackground=fg_color,
                relief=tk.FLAT,
                width=30
            )
            desc_entry.grid(row=1+i, column=2, pady=1)
            
            self.today_normal_entries[f"slot{i}_title"] = title_entry
            self.today_normal_entries[f"slot{i}_desc"] = desc_entry
        
        # Today's Work Schedule
        tk.Label(
            today_edit_frame,
            text="Work Day:",
            font=normal_font,
            bg=bg_color,
            fg=fg_color
        ).grid(row=6, column=0, sticky=tk.W, pady=(10, 2))
        
        self.today_work_entries = {}
        for i in range(1, 3):
            tk.Label(
                today_edit_frame,
                text=f"  Slot {i}:",
                font=normal_font,
                bg=bg_color,
                fg=fg_color
            ).grid(row=6+i, column=0, sticky=tk.W, pady=1)
            
            title_entry = tk.Entry(
                today_edit_frame,
                font=normal_font,
                bg=entry_bg,
                fg=fg_color,
                insertbackground=fg_color,
                relief=tk.FLAT,
                width=20
            )
            title_entry.grid(row=6+i, column=1, pady=1, padx=(10, 5))
            
            desc_entry = tk.Entry(
                today_edit_frame,
                font=normal_font,
                bg=entry_bg,
                fg=fg_color,
                insertbackground=fg_color,
                relief=tk.FLAT,
                width=30
            )
            desc_entry.grid(row=6+i, column=2, pady=1)
            
            self.today_work_entries[f"slot{i}_title"] = title_entry
            self.today_work_entries[f"slot{i}_desc"] = desc_entry
        
        # Tomorrow's Editor (initially hidden)
        tomorrow_edit_frame = tk.Frame(editor_frame, bg=bg_color)
        # Note: not packing initially, will be shown when tab is clicked
        
        # Tomorrow's Title
        tk.Label(
            tomorrow_edit_frame,
            text="Tomorrow's Title:",
            font=normal_font,
            bg=bg_color,
            fg=fg_color
        ).grid(row=0, column=0, sticky=tk.W, pady=2)
        
        self.tomorrow_title_entry = tk.Entry(
            tomorrow_edit_frame,
            font=normal_font,
            bg=entry_bg,
            fg=fg_color,
            insertbackground=fg_color,
            relief=tk.FLAT,
            width=50
        )
        self.tomorrow_title_entry.grid(row=0, column=1, pady=2, padx=(10, 0))
        self.tomorrow_title_entry.insert(0, "Tomorrow's Stream")
        
        # Tomorrow's Normal Schedule
        tk.Label(
            tomorrow_edit_frame,
            text="Normal Day:",
            font=normal_font,
            bg=bg_color,
            fg=fg_color
        ).grid(row=1, column=0, sticky=tk.W, pady=(10, 2))
        
        self.tomorrow_normal_entries = {}
        for i in range(1, 5):
            tk.Label(
                tomorrow_edit_frame,
                text=f"  Slot {i}:",
                font=normal_font,
                bg=bg_color,
                fg=fg_color
            ).grid(row=1+i, column=0, sticky=tk.W, pady=1)
            
            title_entry = tk.Entry(
                tomorrow_edit_frame,
                font=normal_font,
                bg=entry_bg,
                fg=fg_color,
                insertbackground=fg_color,
                relief=tk.FLAT,
                width=20
            )
            title_entry.grid(row=1+i, column=1, pady=1, padx=(10, 5))
            
            desc_entry = tk.Entry(
                tomorrow_edit_frame,
                font=normal_font,
                bg=entry_bg,
                fg=fg_color,
                insertbackground=fg_color,
                relief=tk.FLAT,
                width=30
            )
            desc_entry.grid(row=1+i, column=2, pady=1)
            
            self.tomorrow_normal_entries[f"slot{i}_title"] = title_entry
            self.tomorrow_normal_entries[f"slot{i}_desc"] = desc_entry
        
        # Tomorrow's Work Schedule
        tk.Label(
            tomorrow_edit_frame,
            text="Work Day:",
            font=normal_font,
            bg=bg_color,
            fg=fg_color
        ).grid(row=6, column=0, sticky=tk.W, pady=(10, 2))
        
        self.tomorrow_work_entries = {}
        for i in range(1, 3):
            tk.Label(
                tomorrow_edit_frame,
                text=f"  Slot {i}:",
                font=normal_font,
                bg=bg_color,
                fg=fg_color
            ).grid(row=6+i, column=0, sticky=tk.W, pady=1)
            
            title_entry = tk.Entry(
                tomorrow_edit_frame,
                font=normal_font,
                bg=entry_bg,
                fg=fg_color,
                insertbackground=fg_color,
                relief=tk.FLAT,
                width=20
            )
            title_entry.grid(row=6+i, column=1, pady=1, padx=(10, 5))
            
            desc_entry = tk.Entry(
                tomorrow_edit_frame,
                font=normal_font,
                bg=entry_bg,
                fg=fg_color,
                insertbackground=fg_color,
                relief=tk.FLAT,
                width=30
            )
            desc_entry.grid(row=6+i, column=2, pady=1)
            
            self.tomorrow_work_entries[f"slot{i}_title"] = title_entry
            self.tomorrow_work_entries[f"slot{i}_desc"] = desc_entry
        
        # Layout Customization Frame
        layout_frame = tk.LabelFrame(
            main_frame,
            text="Layout Customization",
            font=header_font,
            bg=bg_color,
            fg=fg_color,
            relief=tk.GROOVE,
            borderwidth=2
        )
        layout_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Outer Padding Section
        outer_padding_label = tk.Label(
            layout_frame,
            text="Outer Padding",
            font=normal_font,
            bg=bg_color,
            fg=fg_color
        )
        outer_padding_label.pack(pady=(10, 5))
        
        outer_padding_frame = tk.Frame(layout_frame, bg=bg_color)
        outer_padding_frame.pack(padx=10, pady=5)
        
        self.outer_padding_vars = {}
        padding_labels = ["Top", "Bottom", "Left", "Right"]
        for i, label in enumerate(padding_labels):
            row = i // 2
            col = i % 2
            
            tk.Label(
                outer_padding_frame,
                text=f"{label}:",
                font=normal_font,
                bg=bg_color,
                fg=fg_color
            ).grid(row=row, column=col*3, sticky=tk.W, padx=(10, 5), pady=2)
            
            var = tk.IntVar(value=32)
            self.outer_padding_vars[label.lower()] = var
            
            scale = tk.Scale(
                outer_padding_frame,
                from_=0,
                to=128,
                orient=tk.HORIZONTAL,
                variable=var,
                bg=bg_color,
                fg=fg_color,
                troughcolor=entry_bg,
                activebackground=accent_color,
                highlightthickness=0,
                length=150
            )
            scale.grid(row=row, column=col*3+1, padx=5, pady=2)
            
            value_label = tk.Label(
                outer_padding_frame,
                text=f"{var.get()}px",
                font=normal_font,
                bg=bg_color,
                fg=fg_color,
                width=5
            )
            value_label.grid(row=row, column=col*3+2, padx=(0, 10), pady=2)
            
            var.trace('w', lambda *args, lbl=value_label, v=var: lbl.config(text=f"{v.get()}px"))
        
        # Inner Padding Section
        inner_padding_label = tk.Label(
            layout_frame,
            text="Inner Padding",
            font=normal_font,
            bg=bg_color,
            fg=fg_color
        )
        inner_padding_label.pack(pady=(10, 5))
        
        inner_padding_frame = tk.Frame(layout_frame, bg=bg_color)
        inner_padding_frame.pack(padx=10, pady=5)
        
        self.inner_padding_vars = {}
        for i, label in enumerate(padding_labels):
            row = i // 2
            col = i % 2
            
            tk.Label(
                inner_padding_frame,
                text=f"{label}:",
                font=normal_font,
                bg=bg_color,
                fg=fg_color
            ).grid(row=row, column=col*3, sticky=tk.W, padx=(10, 5), pady=2)
            
            var = tk.IntVar(value=32)
            self.inner_padding_vars[label.lower()] = var
            
            scale = tk.Scale(
                inner_padding_frame,
                from_=0,
                to=128,
                orient=tk.HORIZONTAL,
                variable=var,
                bg=bg_color,
                fg=fg_color,
                troughcolor=entry_bg,
                activebackground=accent_color,
                highlightthickness=0,
                length=150
            )
            scale.grid(row=row, column=col*3+1, padx=5, pady=2)
            
            value_label = tk.Label(
                inner_padding_frame,
                text=f"{var.get()}px",
                font=normal_font,
                bg=bg_color,
                fg=fg_color,
                width=5
            )
            value_label.grid(row=row, column=col*3+2, padx=(0, 10), pady=2)
            
            var.trace('w', lambda *args, lbl=value_label, v=var: lbl.config(text=f"{v.get()}px"))
        
        # Glow Effects Section
        glow_label = tk.Label(
            layout_frame,
            text="Glow Effects",
            font=normal_font,
            bg=bg_color,
            fg=fg_color
        )
        glow_label.pack(pady=(10, 5))
        
        glow_frame = tk.Frame(layout_frame, bg=bg_color)
        glow_frame.pack(padx=10, pady=(5, 15))
        
        self.glow_vars = {}
        glow_settings = [
            ("Title Glow", "title", 60, 20),
            ("Link Glow", "link", 40, 15),
            ("Panel Glow", "panel", 120, 50),
            ("Glow Intensity", "intensity", 100, 50)
        ]
        
        for i, (label, key, max_val, default) in enumerate(glow_settings):
            row = i // 2
            col = i % 2
            
            tk.Label(
                glow_frame,
                text=f"{label}:",
                font=normal_font,
                bg=bg_color,
                fg=fg_color
            ).grid(row=row, column=col*3, sticky=tk.W, padx=(10, 5), pady=2)
            
            var = tk.IntVar(value=default)
            self.glow_vars[key] = var
            
            scale = tk.Scale(
                glow_frame,
                from_=0,
                to=max_val,
                orient=tk.HORIZONTAL,
                variable=var,
                bg=bg_color,
                fg=fg_color,
                troughcolor=entry_bg,
                activebackground=accent_color,
                highlightthickness=0,
                length=150
            )
            scale.grid(row=row, column=col*3+1, padx=5, pady=2)
            
            unit = "%" if key == "intensity" else "px"
            value_label = tk.Label(
                glow_frame,
                text=f"{var.get()}{unit}",
                font=normal_font,
                bg=bg_color,
                fg=fg_color,
                width=5
            )
            value_label.grid(row=row, column=col*3+2, padx=(0, 10), pady=2)
            
            var.trace('w', lambda *args, lbl=value_label, v=var, u=unit: lbl.config(text=f"{v.get()}{u}"))
        
        # Discord Message Generator Frame
        discord_frame = tk.LabelFrame(
            main_frame,
            text="Discord Message Generator",
            font=header_font,
            bg=bg_color,
            fg=fg_color,
            relief=tk.GROOVE,
            borderwidth=2
        )
        discord_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Announcement Title
        title_frame = tk.Frame(discord_frame, bg=bg_color)
        title_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        tk.Label(
            title_frame,
            text="Announcement Title:",
            font=normal_font,
            bg=bg_color,
            fg=fg_color
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.discord_title_entry = tk.Entry(
            title_frame,
            font=normal_font,
            bg=entry_bg,
            fg=fg_color,
            insertbackground=fg_color,
            relief=tk.FLAT,
            width=40
        )
        self.discord_title_entry.pack(side=tk.LEFT)
        self.discord_title_entry.insert(0, "Doubling our Usual Hours! ✨👏")
        
        # Timestamp settings
        timestamp_frame = tk.Frame(discord_frame, bg=bg_color)
        timestamp_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(
            timestamp_frame,
            text="Timestamp Format:",
            font=normal_font,
            bg=bg_color,
            fg=fg_color
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.timestamp_format = tk.StringVar(value="t")
        timestamp_options = [
            ("t", "Short Time"),
            ("T", "Long Time"),
            ("d", "Short Date"),
            ("D", "Long Date"),
            ("f", "Short Date/Time"),
            ("F", "Long Date/Time"),
            ("R", "Relative Time")
        ]
        
        timestamp_menu = tk.OptionMenu(
            timestamp_frame,
            self.timestamp_format,
            *[opt[0] for opt in timestamp_options]
        )
        timestamp_menu.config(
            bg=entry_bg,
            fg=fg_color,
            activebackground=accent_color,
            activeforeground="white",
            relief=tk.FLAT
        )
        timestamp_menu.pack(side=tk.LEFT, padx=(0, 20))
        
        self.use_timestamps = tk.BooleanVar(value=True)
        tk.Checkbutton(
            timestamp_frame,
            text="Use Discord Timestamps",
            variable=self.use_timestamps,
            font=normal_font,
            bg=bg_color,
            fg=fg_color,
            selectcolor=button_bg,
            activebackground=bg_color
        ).pack(side=tk.LEFT)
        
        # Discord Message Output
        self.discord_output = tk.Text(
            discord_frame,
            font=normal_font,
            bg=entry_bg,
            fg=fg_color,
            insertbackground=fg_color,
            relief=tk.FLAT,
            height=10,
            width=60
        )
        self.discord_output.pack(padx=10, pady=5)
        
        # Copy Message Button
        copy_btn = tk.Button(
            discord_frame,
            text="Copy Message",
            font=normal_font,
            bg=accent_color,
            fg="white",
            relief=tk.FLAT,
            padx=15,
            pady=5,
            command=self.copy_discord_message
        )
        copy_btn.pack(pady=(0, 10))
        
        # Export Schedule Frame
        export_frame = tk.LabelFrame(
            main_frame,
            text="Export Schedule",
            font=header_font,
            bg=bg_color,
            fg=fg_color,
            relief=tk.GROOVE,
            borderwidth=2
        )
        export_frame.pack(fill=tk.X, pady=(0, 15))
        
        export_btn = tk.Button(
            export_frame,
            text="💾 Download Schedule as PNG",
            font=header_font,
            bg=accent_color,
            fg="white",
            relief=tk.FLAT,
            padx=20,
            pady=10,
            command=self.export_schedule
        )
        export_btn.pack(pady=15)
        
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
