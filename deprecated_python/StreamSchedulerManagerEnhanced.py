#!/usr/bin/env python3
"""
StreamSchedulerManagerEnhanced.py
Enhanced version with dynamic slot management, time editing, and add/delete functionality.
"""

import json
import webbrowser
import sys
import subprocess
import threading
import time
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, font
import tkinter.colorchooser as colorchooser
from datetime import datetime, timedelta

class TimePickerDialog:
    """Custom time picker dialog for selecting stream times."""
    
    def __init__(self, parent, initial_time="9:30 AM"):
        self.result = None
        self.parent = parent
        
        # Parse initial time
        try:
            time_parts = initial_time.strip().split()
            hour_min = time_parts[0].split(':')
            self.hour = int(hour_min[0])
            self.minute = int(hour_min[1])
            self.ampm = time_parts[1] if len(time_parts) > 1 else "AM"
        except:
            self.hour = 9
            self.minute = 30
            self.ampm = "AM"
        
        self.create_dialog()
    
    def create_dialog(self):
        """Create the time picker dialog."""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Select Time")
        self.dialog.geometry("300x200")
        self.dialog.resizable(False, False)
        
        # Center the dialog
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Configure colors
        bg_color = "#1a1a2e"
        fg_color = "#eee"
        entry_bg = "#0f3460"
        
        self.dialog.configure(bg=bg_color)
        
        # Time selection frame
        time_frame = tk.Frame(self.dialog, bg=bg_color)
        time_frame.pack(pady=20)
        
        # Hour spinner
        tk.Label(time_frame, text="Hour:", bg=bg_color, fg=fg_color).grid(row=0, column=0, padx=5)
        self.hour_var = tk.StringVar(value=str(self.hour))
        hour_spin = tk.Spinbox(
            time_frame,
            from_=1, to=12,
            textvariable=self.hour_var,
            width=5,
            bg=entry_bg,
            fg=fg_color,
            buttonbackground=entry_bg
        )
        hour_spin.grid(row=0, column=1, padx=5)
        
        # Minute spinner
        tk.Label(time_frame, text="Min:", bg=bg_color, fg=fg_color).grid(row=0, column=2, padx=5)
        self.minute_var = tk.StringVar(value=f"{self.minute:02d}")
        minute_spin = tk.Spinbox(
            time_frame,
            from_=0, to=59,
            increment=5,
            textvariable=self.minute_var,
            width=5,
            bg=entry_bg,
            fg=fg_color,
            buttonbackground=entry_bg,
            format="%02.0f"
        )
        minute_spin.grid(row=0, column=3, padx=5)
        
        # AM/PM selection
        ampm_frame = tk.Frame(time_frame, bg=bg_color)
        ampm_frame.grid(row=0, column=4, padx=10)
        
        self.ampm_var = tk.StringVar(value=self.ampm)
        tk.Radiobutton(
            ampm_frame,
            text="AM",
            variable=self.ampm_var,
            value="AM",
            bg=bg_color,
            fg=fg_color,
            selectcolor=entry_bg
        ).pack()
        tk.Radiobutton(
            ampm_frame,
            text="PM",
            variable=self.ampm_var,
            value="PM",
            bg=bg_color,
            fg=fg_color,
            selectcolor=entry_bg
        ).pack()
        
        # Buttons
        button_frame = tk.Frame(self.dialog, bg=bg_color)
        button_frame.pack(pady=20)
        
        tk.Button(
            button_frame,
            text="OK",
            command=self.ok_clicked,
            bg="#9146FF",
            fg="white",
            padx=20,
            pady=5
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame,
            text="Cancel",
            command=self.cancel_clicked,
            bg="#6272a4",
            fg="white",
            padx=20,
            pady=5
        ).pack(side=tk.LEFT, padx=5)
    
    def ok_clicked(self):
        """Handle OK button click."""
        hour = int(self.hour_var.get())
        minute = int(self.minute_var.get())
        ampm = self.ampm_var.get()
        self.result = f"{hour}:{minute:02d} {ampm}"
        self.dialog.destroy()
    
    def cancel_clicked(self):
        """Handle Cancel button click."""
        self.result = None
        self.dialog.destroy()
    
    def show(self):
        """Show the dialog and return the result."""
        self.dialog.wait_window()
        return self.result


class SlotEditorFrame(tk.Frame):
    """Frame for editing a single schedule slot."""
    
    def __init__(self, parent, slot_data, slot_index, on_delete=None, on_update=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.slot_data = slot_data
        self.slot_index = slot_index
        self.on_delete = on_delete
        self.on_update = on_update
        
        bg_color = kwargs.get('bg', '#1a1a2e')
        fg_color = '#eee'
        entry_bg = '#0f3460'
        
        self.configure(bg=bg_color)
        
        # Time frame
        time_frame = tk.Frame(self, bg=bg_color)
        time_frame.pack(side=tk.LEFT, padx=5)
        
        # Parse time
        try:
            start_time, end_time = slot_data.get('time', '9:30 AM - 12:30 PM').split(' - ')
        except:
            start_time, end_time = "9:30 AM", "12:30 PM"
        
        # Start time button
        self.start_time_btn = tk.Button(
            time_frame,
            text=start_time,
            command=self.edit_start_time,
            bg=entry_bg,
            fg=fg_color,
            width=10
        )
        self.start_time_btn.pack(side=tk.LEFT, padx=2)
        
        tk.Label(time_frame, text="–", bg=bg_color, fg=fg_color).pack(side=tk.LEFT, padx=2)
        
        # End time button
        self.end_time_btn = tk.Button(
            time_frame,
            text=end_time,
            command=self.edit_end_time,
            bg=entry_bg,
            fg=fg_color,
            width=10
        )
        self.end_time_btn.pack(side=tk.LEFT, padx=2)
        
        # Content frame
        content_frame = tk.Frame(self, bg=bg_color)
        content_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Title entry
        self.title_entry = tk.Entry(
            content_frame,
            bg=entry_bg,
            fg=fg_color,
            insertbackground=fg_color,
            width=25
        )
        self.title_entry.pack(side=tk.LEFT, padx=2)
        self.title_entry.insert(0, slot_data.get('title', ''))
        self.title_entry.bind('<KeyRelease>', self.on_content_change)
        
        # Description entry
        self.desc_entry = tk.Entry(
            content_frame,
            bg=entry_bg,
            fg=fg_color,
            insertbackground=fg_color,
            width=40
        )
        self.desc_entry.pack(side=tk.LEFT, padx=2)
        self.desc_entry.insert(0, slot_data.get('desc', ''))
        self.desc_entry.bind('<KeyRelease>', self.on_content_change)
        
        # Delete button
        if self.on_delete:
            delete_btn = tk.Button(
                self,
                text="🗑",
                command=lambda: self.on_delete(self.slot_index),
                bg="#ff4444",
                fg="white",
                width=3
            )
            delete_btn.pack(side=tk.LEFT, padx=5)
    
    def edit_start_time(self):
        """Edit the start time."""
        current_time = self.start_time_btn['text']
        picker = TimePickerDialog(self, current_time)
        new_time = picker.show()
        if new_time:
            self.start_time_btn.config(text=new_time)
            self.update_slot_time()
    
    def edit_end_time(self):
        """Edit the end time."""
        current_time = self.end_time_btn['text']
        picker = TimePickerDialog(self, current_time)
        new_time = picker.show()
        if new_time:
            self.end_time_btn.config(text=new_time)
            self.update_slot_time()
    
    def update_slot_time(self):
        """Update the slot time and notify parent."""
        start = self.start_time_btn['text']
        end = self.end_time_btn['text']
        self.slot_data['time'] = f"{start} - {end}"
        if self.on_update:
            self.on_update(self.slot_index, self.slot_data)
    
    def on_content_change(self, event=None):
        """Handle content changes."""
        self.slot_data['title'] = self.title_entry.get()
        self.slot_data['desc'] = self.desc_entry.get()
        if self.on_update:
            self.on_update(self.slot_index, self.slot_data)
    
    def get_slot_data(self):
        """Get the current slot data."""
        return {
            'time': f"{self.start_time_btn['text']} - {self.end_time_btn['text']}",
            'title': self.title_entry.get(),
            'desc': self.desc_entry.get()
        }


class StreamSchedulerManager:
    def __init__(self):
        self.script_dir = Path(__file__).parent
        # Use the config.json in the HTML directory (parent directory) for sharing with Node.js server
        self.config_file = self.script_dir.parent / "config.json"
        self.html_file = self.script_dir.parent / "StreamSchedulerImageGenerator.html"
        self.config = self.load_config()
        self.server_thread = None
        self.root = None
        self.slot_frames = {
            'today_normal': [],
            'today_work': [],
            'tomorrow_normal': [],
            'tomorrow_work': []
        }
        
    def load_config(self):
        """Load configuration from JSON file."""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # Ensure slots are lists, not dicts
                    for day in ['today', 'tomorrow']:
                        for type in ['normal', 'work']:
                            if isinstance(config['schedule'][day][type], dict):
                                # Convert dict to list
                                slots = []
                                for key in sorted(config['schedule'][day][type].keys()):
                                    slots.append(config['schedule'][day][type][key])
                                config['schedule'][day][type] = slots
                    return config
        except Exception as e:
            print(f"Error loading config: {e}")
        
        # Default configuration with enhanced features
        return {
            "channel": {
                "name": "Audacious Gabe",
                "link": "https://www.twitch.tv/audaciousgabe"
            },
            "theme": "twilight",
            "timezone": "All times are in EST",
            "exportScope": "full",
            "schedule": {
                "today": {
                    "type": "normal",
                    "title": "Today's Stream",
                    "normal": [
                        {"time": "9:30 AM - 12:30 PM", "title": "Morning Warmup", "desc": "Clearing admin tasks, then jumping into chill development."},
                        {"time": "1:00 PM - 4:00 PM", "title": "Focused Development + Prototype Speedrun", "desc": "Getting stuff done and making things happen ✨👏"},
                        {"time": "5:00 PM - 8:00 PM", "title": "Greenlight Development", "desc": "You picked it, now we're building it."},
                        {"time": "9:00 PM - 12:00 AM", "title": "Late Night Admin", "desc": "Winding down with some chill development."}
                    ],
                    "work": [
                        {"time": "9:30 AM - 12:30 PM", "title": "Morning Warmup", "desc": "Clearing admin tasks, then jumping into chill development."},
                        {"time": "12:30 PM - 3:30 PM", "title": "Focused Development + Prototype Speedrun", "desc": "Getting stuff done and making things happen ✨👏"}
                    ]
                },
                "tomorrow": {
                    "type": "work",
                    "title": "Tomorrow's Stream",
                    "normal": [
                        {"time": "9:30 AM - 12:30 PM", "title": "Morning Warmup", "desc": "Clearing admin tasks, then jumping into chill development."},
                        {"time": "1:00 PM - 4:00 PM", "title": "Focused Development + Prototype Speedrun", "desc": "Getting stuff done and making things happen ✨👏"},
                        {"time": "5:00 PM - 8:00 PM", "title": "Greenlight Development", "desc": "You picked it, now we're building it."},
                        {"time": "9:00 PM - 12:00 AM", "title": "Late Night Admin", "desc": "Winding down with some chill development."}
                    ],
                    "work": [
                        {"time": "9:30 AM - 12:30 PM", "title": "Morning Warmup", "desc": "Clearing admin tasks, then jumping into chill development."},
                        {"time": "12:30 PM - 3:30 PM", "title": "Focused Development + Prototype Speedrun", "desc": "Getting stuff done and making things happen ✨👏"}
                    ]
                }
            },
            "layout": {
                "outerPadding": {"top": 32, "bottom": 32, "left": 32, "right": 32},
                "innerPadding": {"top": 32, "bottom": 32, "left": 32, "right": 32},
                "glow": {"title": 20, "link": 15, "panel": 50, "intensity": 50}
            },
            "discord": {
                "templates": [
                    {
                        "name": "Stream Starting Soon",
                        "title": "🔴 Stream Starting Soon! 🔴",
                        "message": "@everyone Hey folks! Stream is starting soon!\n\n🎮 **Today's Schedule:**\n[today]\n\n📺 Join us at: [link]",
                        "useTimestamp": True,
                        "timestampFormat": "R"
                    },
                    {
                        "name": "Stream Live",
                        "title": "🔴 WE'RE LIVE! 🔴",
                        "message": "@everyone We're live right now!\n\n🎮 **Today's Schedule:**\n[today]\n\n📺 Watch at: [link]",
                        "useTimestamp": True,
                        "timestampFormat": "t"
                    },
                    {
                        "name": "Schedule Update",
                        "title": "📅 Schedule Update 📅",
                        "message": "Hey everyone! Here's our streaming schedule:\n\n**Today:**\n[today]\n\n**Tomorrow:**\n[tomorrow]\n\n[timezone]",
                        "useTimestamp": True,
                        "timestampFormat": "f"
                    },
                    {
                        "name": "Custom Stream Schedule",
                        "title": "Doubling our Usual Hours! ✨👏",
                        "message": "@Twitch Enjoyers : [title]\n\nI will be streaming on Twitch ``Today`` from:\n\n[today]\n\n``Tomorrow`` I'll be streaming from:\n\n[tomorrow]\n\n[timezone]\n\n[link]",
                        "useTimestamp": True,
                        "timestampFormat": "t"
                    }
                ],
                "currentTemplate": 3,
                "customMessage": {
                    "title": "Doubling our Usual Hours! ✨👏",
                    "message": "",
                    "useTimestamp": True,
                    "timestampFormat": "t"
                }
            }
        }
    
    def save_config(self):
        """Save configuration to JSON file."""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
    
    def start_server(self):
        """Start the npm server in the HTML directory."""
        html_dir = self.html_file.parent
        
        def run_npm_server():
            try:
                # Check if npm is available
                subprocess.run(["npm", "--version"], check=True, capture_output=True, text=True)
                
                # Run npm start in the HTML directory
                print(f"Starting npm server in {html_dir}...")
                process = subprocess.Popen(
                    ["npm", "start"],
                    cwd=html_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    shell=True
                )
                
                # Monitor the output
                for line in process.stdout:
                    if "Server running" in line or "localhost:5555" in line:
                        print(line.strip())
                        break
                    print(line.strip())
                
                # Keep the process running
                process.wait()
                
            except subprocess.CalledProcessError:
                print("Error: npm is not installed or not in PATH")
                print("Please install Node.js and npm to use the server functionality")
            except FileNotFoundError:
                print("Error: npm command not found")
                print("Please install Node.js and npm from https://nodejs.org/")
            except Exception as e:
                print(f"Error starting npm server: {e}")
        
        self.server_thread = threading.Thread(target=run_npm_server, daemon=True)
        self.server_thread.start()
        
        # Give the server a moment to start
        time.sleep(2)
        print("Server starting... Check console for details.")
    
    def open_html(self):
        """Open the HTML file in the browser."""
        try:
            if not self.html_file.exists():
                messagebox.showerror("Error", f"HTML file not found at {self.html_file}")
                return False
            
            webbrowser.open(f"file:///{self.html_file.absolute()}")
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open HTML: {e}")
            return False
    
    def create_schedule_editor(self, parent, day, schedule_type):
        """Create a schedule editor with dynamic slots."""
        bg_color = "#1a1a2e"
        fg_color = "#eee"
        
        container = tk.Frame(parent, bg=bg_color)
        
        # Slots container
        slots_frame = tk.Frame(container, bg=bg_color)
        slots_frame.pack(fill=tk.BOTH, expand=True)
        
        # Store reference
        frame_key = f"{day}_{schedule_type}"
        self.slot_frames[frame_key] = []
        
        # Load existing slots
        slots = self.config["schedule"][day][schedule_type]
        for i, slot in enumerate(slots):
            self.add_slot_editor(slots_frame, frame_key, slot, i)
        
        # Add slot button
        add_btn = tk.Button(
            container,
            text="+ Add Stream Slot",
            command=lambda: self.add_new_slot(slots_frame, frame_key),
            bg="#9146FF",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            pady=5
        )
        add_btn.pack(fill=tk.X, pady=5)
        
        return container
    
    def add_slot_editor(self, parent, frame_key, slot_data, index):
        """Add a slot editor frame."""
        def on_delete(idx):
            self.delete_slot(frame_key, idx)
        
        def on_update(idx, data):
            self.update_slot(frame_key, idx, data)
        
        editor = SlotEditorFrame(
            parent,
            slot_data,
            index,
            on_delete=on_delete if index > 0 else None,  # Can't delete first slot
            on_update=on_update,
            bg="#1a1a2e"
        )
        editor.pack(fill=tk.X, pady=2)
        self.slot_frames[frame_key].append(editor)
    
    def add_new_slot(self, parent, frame_key):
        """Add a new slot to the schedule."""
        # Determine default time based on last slot
        day, stype = frame_key.split('_')
        slots = self.config["schedule"][day][stype]
        
        # Calculate new time based on last slot
        if slots:
            last_slot = slots[-1]
            try:
                _, end_time = last_slot['time'].split(' - ')
                # Parse end time and add 30 minutes
                time_parts = end_time.split()
                hour_min = time_parts[0].split(':')
                hour = int(hour_min[0])
                minute = int(hour_min[1])
                ampm = time_parts[1]
                
                # Add 30 minutes
                minute += 30
                if minute >= 60:
                    hour += 1
                    minute -= 60
                    if hour > 12:
                        hour = 1
                    elif hour == 12 and ampm == "AM":
                        ampm = "PM"
                    elif hour == 12 and ampm == "PM":
                        ampm = "AM"
                
                start_time = f"{hour}:{minute:02d} {ampm}"
                
                # Calculate end time (3 hours later)
                end_hour = hour + 3
                end_ampm = ampm
                if end_hour > 12:
                    end_hour -= 12
                    end_ampm = "PM" if ampm == "AM" else "AM"
                elif end_hour == 12:
                    end_ampm = "PM" if ampm == "AM" else "AM"
                
                end_time = f"{end_hour}:{minute:02d} {end_ampm}"
                new_time = f"{start_time} - {end_time}"
            except:
                new_time = "2:00 PM - 5:00 PM"
        else:
            new_time = "9:30 AM - 12:30 PM"
        
        new_slot = {
            "time": new_time,
            "title": "New Stream Session",
            "desc": "Description of this stream session"
        }
        
        slots.append(new_slot)
        index = len(slots) - 1
        
        # Add editor
        self.add_slot_editor(parent, frame_key, new_slot, index)
        
        # Save config
        self.save_config()
    
    def delete_slot(self, frame_key, index):
        """Delete a slot from the schedule."""
        day, stype = frame_key.split('_')
        slots = self.config["schedule"][day][stype]
        
        if len(slots) <= 1:
            messagebox.showwarning("Cannot Delete", "You must have at least one stream slot!")
            return
        
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this stream slot?"):
            # Remove from config
            slots.pop(index)
            
            # Remove frame
            frame = self.slot_frames[frame_key][index]
            frame.destroy()
            self.slot_frames[frame_key].pop(index)
            
            # Update indices for remaining frames
            for i, frame in enumerate(self.slot_frames[frame_key]):
                frame.slot_index = i
            
            # Save config
            self.save_config()
    
    def update_slot(self, frame_key, index, data):
        """Update a slot in the schedule."""
        day, stype = frame_key.split('_')
        self.config["schedule"][day][stype][index] = data
        # Don't save on every keystroke, maybe add a save button
    
    def create_gui(self):
        """Create the Tkinter GUI."""
        self.root = tk.Tk()
        self.root.title("Stream Scheduler Manager - Enhanced")
        self.root.geometry("1000x800")
        
        # Configure styles
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure dark theme colors
        bg_color = "#1a1a2e"
        fg_color = "#eee"
        accent_color = "#9146FF"
        button_bg = "#16213e"
        entry_bg = "#0f3460"
        
        self.root.configure(bg=bg_color)
        
        # Custom fonts
        title_font = font.Font(family="Segoe UI", size=16, weight="bold")
        header_font = font.Font(family="Segoe UI", size=12, weight="bold")
        normal_font = font.Font(family="Segoe UI", size=10)
        
        # Main notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Configure notebook style
        style.configure('TNotebook', background=bg_color, borderwidth=0)
        style.configure('TNotebook.Tab', 
                       background=button_bg,
                       foreground=fg_color,
                       padding=[20, 10])
        style.map('TNotebook.Tab',
                 background=[('selected', accent_color)],
                 foreground=[('selected', 'white')])
        
        # Tab 1: Basic Settings
        basic_frame = tk.Frame(notebook, bg=bg_color)
        notebook.add(basic_frame, text="Basic Settings")
        
        self.create_basic_settings(basic_frame, bg_color, fg_color, entry_bg, 
                                 header_font, normal_font)
        
        # Tab 2: Today's Schedule
        today_frame = tk.Frame(notebook, bg=bg_color)
        notebook.add(today_frame, text="Today's Schedule")
        
        self.create_schedule_tab(today_frame, "today", bg_color, fg_color, 
                                header_font, normal_font)
        
        # Tab 3: Tomorrow's Schedule
        tomorrow_frame = tk.Frame(notebook, bg=bg_color)
        notebook.add(tomorrow_frame, text="Tomorrow's Schedule")
        
        self.create_schedule_tab(tomorrow_frame, "tomorrow", bg_color, fg_color,
                                header_font, normal_font)
        
        # Tab 4: Discord & Export
        discord_frame = tk.Frame(notebook, bg=bg_color)
        notebook.add(discord_frame, text="Discord & Export")
        
        self.create_discord_tab(discord_frame, bg_color, fg_color, entry_bg,
                              header_font, normal_font, accent_color, button_bg)
        
        # Bottom action bar
        action_frame = tk.Frame(self.root, bg=bg_color)
        action_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Button(
            action_frame,
            text="💾 Save All Changes",
            command=self.save_all_changes,
            bg=accent_color,
            fg="white",
            font=header_font,
            padx=20,
            pady=10
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            action_frame,
            text="🌐 Open HTML",
            command=self.open_html,
            bg="#50fa7b",
            fg=bg_color,
            font=header_font,
            padx=20,
            pady=10
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            action_frame,
            text="🔄 Reload",
            command=self.reload_configuration,
            bg="#6272a4",
            fg="white",
            font=header_font,
            padx=20,
            pady=10
        ).pack(side=tk.LEFT, padx=5)
    
    def create_basic_settings(self, parent, bg_color, fg_color, entry_bg, header_font, normal_font):
        """Create basic settings controls."""
        # Scrollable frame
        canvas = tk.Canvas(parent, bg=bg_color)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=bg_color)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Channel settings
        channel_frame = tk.LabelFrame(
            scrollable_frame,
            text="Channel Configuration",
            font=header_font,
            bg=bg_color,
            fg=fg_color
        )
        channel_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(channel_frame, text="Channel Name:", bg=bg_color, fg=fg_color).grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        self.name_entry = tk.Entry(channel_frame, bg=entry_bg, fg=fg_color, width=30)
        self.name_entry.grid(row=0, column=1, padx=10, pady=5)
        self.name_entry.insert(0, self.config["channel"]["name"])
        
        tk.Label(channel_frame, text="Twitch Link:", bg=bg_color, fg=fg_color).grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
        self.link_entry = tk.Entry(channel_frame, bg=entry_bg, fg=fg_color, width=30)
        self.link_entry.grid(row=1, column=1, padx=10, pady=5)
        self.link_entry.insert(0, self.config["channel"]["link"])
        
        tk.Label(channel_frame, text="Timezone Message:", bg=bg_color, fg=fg_color).grid(row=2, column=0, sticky=tk.W, padx=10, pady=5)
        self.timezone_entry = tk.Entry(channel_frame, bg=entry_bg, fg=fg_color, width=30)
        self.timezone_entry.grid(row=2, column=1, padx=10, pady=5)
        self.timezone_entry.insert(0, self.config.get("timezone", "All times are in EST"))
        
        # Theme selection
        theme_frame = tk.LabelFrame(
            scrollable_frame,
            text="Theme Selection",
            font=header_font,
            bg=bg_color,
            fg=fg_color
        )
        theme_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.theme_var = tk.StringVar(value=self.config.get("theme", "twilight"))
        themes = [
            ("Twilight", "twilight"),
            ("Sunrise", "sunrise"),
            ("Forest", "forest"),
            ("Oceanic", "oceanic"),
            ("Cyberpunk", "cyberpunk"),
            ("Pastel", "pastel"),
            ("Arctic", "arctic")
        ]
        
        theme_buttons_frame = tk.Frame(theme_frame, bg=bg_color)
        theme_buttons_frame.pack(pady=10)
        
        for i, (display_name, theme_value) in enumerate(themes):
            row = i // 4
            col = i % 4
            tk.Radiobutton(
                theme_buttons_frame,
                text=display_name,
                variable=self.theme_var,
                value=theme_value,
                bg=bg_color,
                fg=fg_color,
                selectcolor=entry_bg
            ).grid(row=row, column=col, padx=5, pady=5)
        
        # Export scope
        export_frame = tk.LabelFrame(
            scrollable_frame,
            text="Export Settings",
            font=header_font,
            bg=bg_color,
            fg=fg_color
        )
        export_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.export_scope = tk.StringVar(value=self.config.get("exportScope", "full"))
        tk.Radiobutton(
            export_frame,
            text="Today Only",
            variable=self.export_scope,
            value="today",
            bg=bg_color,
            fg=fg_color,
            selectcolor=entry_bg
        ).pack(side=tk.LEFT, padx=10, pady=10)
        
        tk.Radiobutton(
            export_frame,
            text="Full Schedule",
            variable=self.export_scope,
            value="full",
            bg=bg_color,
            fg=fg_color,
            selectcolor=entry_bg
        ).pack(side=tk.LEFT, padx=10, pady=10)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def create_schedule_tab(self, parent, day, bg_color, fg_color, header_font, normal_font):
        """Create a schedule tab for a specific day."""
        # Title
        title_frame = tk.Frame(parent, bg=bg_color)
        title_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(
            title_frame,
            text=f"{day.capitalize()}'s Title:",
            bg=bg_color,
            fg=fg_color,
            font=normal_font
        ).pack(side=tk.LEFT, padx=5)
        
        title_entry = tk.Entry(
            title_frame,
            bg="#0f3460",
            fg=fg_color,
            font=normal_font,
            width=50
        )
        title_entry.pack(side=tk.LEFT, padx=5)
        title_entry.insert(0, self.config["schedule"][day]["title"])
        
        # Store reference
        if day == "today":
            self.today_title_entry = title_entry
        else:
            self.tomorrow_title_entry = title_entry
        
        # Schedule type selection
        type_frame = tk.Frame(parent, bg=bg_color)
        type_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(
            type_frame,
            text="Schedule Type:",
            bg=bg_color,
            fg=fg_color,
            font=normal_font
        ).pack(side=tk.LEFT, padx=5)
        
        type_var = tk.StringVar(value=self.config["schedule"][day]["type"])
        
        # Store reference
        if day == "today":
            self.today_type = type_var
        else:
            self.tomorrow_type = type_var
        
        tk.Radiobutton(
            type_frame,
            text="Normal",
            variable=type_var,
            value="normal",
            bg=bg_color,
            fg=fg_color,
            selectcolor="#0f3460"
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Radiobutton(
            type_frame,
            text="Work",
            variable=type_var,
            value="work",
            bg=bg_color,
            fg=fg_color,
            selectcolor="#0f3460"
        ).pack(side=tk.LEFT, padx=5)
        
        # Create notebook for normal/work schedules
        schedule_notebook = ttk.Notebook(parent)
        schedule_notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Normal schedule tab
        normal_frame = tk.Frame(schedule_notebook, bg=bg_color)
        schedule_notebook.add(normal_frame, text="Normal Day Schedule")
        
        normal_editor = self.create_schedule_editor(normal_frame, day, "normal")
        normal_editor.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Work schedule tab
        work_frame = tk.Frame(schedule_notebook, bg=bg_color)
        schedule_notebook.add(work_frame, text="Work Day Schedule")
        
        work_editor = self.create_schedule_editor(work_frame, day, "work")
        work_editor.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def create_discord_tab(self, parent, bg_color, fg_color, entry_bg, header_font, normal_font, accent_color, button_bg):
        """Create Discord and export tab."""
        # Discord frame
        discord_frame = tk.LabelFrame(
            parent,
            text="Discord Message Generator",
            font=header_font,
            bg=bg_color,
            fg=fg_color
        )
        discord_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Template selection
        template_frame = tk.Frame(discord_frame, bg=bg_color)
        template_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(
            template_frame,
            text="Template:",
            font=normal_font,
            bg=bg_color,
            fg=fg_color
        ).pack(side=tk.LEFT, padx=5)
        
        # Get current template index and convert to name
        current_template_index = self.config["discord"].get("currentTemplate", 3)
        template_names = [t["name"] for t in self.config["discord"]["templates"]]
        current_template_name = template_names[current_template_index] if current_template_index < len(template_names) else template_names[0]
        
        self.discord_template_var = tk.StringVar(value=current_template_name)
        self.template_combo = ttk.Combobox(
            template_frame,
            textvariable=self.discord_template_var,
            values=template_names,
            state="readonly",
            width=30
        )
        self.template_combo.pack(side=tk.LEFT, padx=5)
        self.template_combo.bind('<<ComboboxSelected>>', lambda e: self.on_template_selected())
        
        # Add template management buttons
        template_btn_frame = tk.Frame(template_frame, bg=bg_color)
        template_btn_frame.pack(side=tk.LEFT, padx=20)
        
        tk.Button(
            template_btn_frame,
            text="Edit",
            command=self.edit_template,
            bg=button_bg,
            fg=fg_color,
            padx=10
        ).pack(side=tk.LEFT, padx=2)
        
        tk.Button(
            template_btn_frame,
            text="New",
            command=self.new_template,
            bg=button_bg,
            fg=fg_color,
            padx=10
        ).pack(side=tk.LEFT, padx=2)
        
        tk.Button(
            template_btn_frame,
            text="Delete",
            command=self.delete_template,
            bg=button_bg,
            fg=fg_color,
            padx=10
        ).pack(side=tk.LEFT, padx=2)
        
        # Template title and message
        template_edit_frame = tk.LabelFrame(
            discord_frame,
            text="Template Editor",
            font=normal_font,
            bg=bg_color,
            fg=fg_color
        )
        template_edit_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title entry
        title_frame = tk.Frame(template_edit_frame, bg=bg_color)
        title_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(
            title_frame,
            text="Title:",
            font=normal_font,
            bg=bg_color,
            fg=fg_color,
            width=10
        ).pack(side=tk.LEFT)
        
        self.discord_title_entry = tk.Entry(
            title_frame,
            bg=entry_bg,
            fg=fg_color,
            font=normal_font,
            insertbackground=fg_color
        )
        self.discord_title_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Message template text
        message_frame = tk.Frame(template_edit_frame, bg=bg_color)
        message_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        tk.Label(
            message_frame,
            text="Message Template:",
            font=normal_font,
            bg=bg_color,
            fg=fg_color
        ).pack(anchor=tk.W)
        
        # Template text area with scrollbar
        text_frame = tk.Frame(message_frame, bg=bg_color)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.discord_template_text = tk.Text(
            text_frame,
            bg=entry_bg,
            fg=fg_color,
            font=('Consolas', 10),
            height=8,
            width=60,
            wrap=tk.WORD,
            insertbackground=fg_color,
            yscrollcommand=scrollbar.set
        )
        self.discord_template_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.discord_template_text.yview)
        
        # Placeholder help text
        help_frame = tk.Frame(template_edit_frame, bg=bg_color)
        help_frame.pack(fill=tk.X, padx=10, pady=5)
        
        help_text = "Available placeholders: [title], [today], [tomorrow], [link], [timezone]"
        tk.Label(
            help_frame,
            text=help_text,
            font=('Segoe UI', 9),
            bg=bg_color,
            fg=fg_color,
            wraplength=500
        ).pack()
        
        # Timestamp settings
        timestamp_frame = tk.Frame(template_edit_frame, bg=bg_color)
        timestamp_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.use_timestamps = tk.BooleanVar(value=True)
        tk.Checkbutton(
            timestamp_frame,
            text="Use Discord Timestamps",
            variable=self.use_timestamps,
            font=normal_font,
            bg=bg_color,
            fg=fg_color,
            selectcolor=button_bg,
            command=self.update_template_settings
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Label(
            timestamp_frame,
            text="Format:",
            font=normal_font,
            bg=bg_color,
            fg=fg_color
        ).pack(side=tk.LEFT, padx=5)
        
        self.timestamp_format_var = tk.StringVar(value="R")
        timestamp_formats = [
            ("R", "Relative (in 2 hours)"),
            ("t", "Short Time (10:30 AM)"),
            ("T", "Long Time (10:30:00 AM)"),
            ("f", "Short Date/Time"),
            ("F", "Long Date/Time")
        ]
        
        self.timestamp_format_combo = ttk.Combobox(
            timestamp_frame,
            textvariable=self.timestamp_format_var,
            values=[f"{code} - {desc}" for code, desc in timestamp_formats],
            state="readonly",
            width=25
        )
        self.timestamp_format_combo.pack(side=tk.LEFT, padx=5)
        self.timestamp_format_combo.bind('<<ComboboxSelected>>', lambda e: self.update_template_settings())
        
        # Preview frame
        preview_frame = tk.LabelFrame(
            discord_frame,
            text="Message Preview",
            font=normal_font,
            bg=bg_color,
            fg=fg_color
        )
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Discord output
        preview_text_frame = tk.Frame(preview_frame, bg=bg_color)
        preview_text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        preview_scrollbar = tk.Scrollbar(preview_text_frame)
        preview_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.discord_output = tk.Text(
            preview_text_frame,
            font=('Consolas', 10),
            bg=entry_bg,
            fg=fg_color,
            height=10,
            width=60,
            wrap=tk.WORD,
            yscrollcommand=preview_scrollbar.set
        )
        self.discord_output.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        preview_scrollbar.config(command=self.discord_output.yview)
        
        # Buttons
        button_frame = tk.Frame(preview_frame, bg=bg_color)
        button_frame.pack(pady=10)
        
        tk.Button(
            button_frame,
            text="Save Template",
            font=normal_font,
            bg="#50fa7b",
            fg=bg_color,
            command=self.save_template_changes,
            padx=15,
            pady=5
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame,
            text="Generate Message",
            font=normal_font,
            bg="#6272a4",
            fg="white",
            command=self.generate_discord_message,
            padx=15,
            pady=5
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame,
            text="Copy Message",
            font=normal_font,
            bg=accent_color,
            fg="white",
            command=self.copy_discord_message,
            padx=15,
            pady=5
        ).pack(side=tk.LEFT, padx=5)
        
        # Initialize with first template
        self.on_template_selected()
    
    def on_template_selected(self, event=None):
        """Handle template selection from combobox."""
        template_name = self.discord_template_var.get()
        
        # Find the selected template
        template = None
        for t in self.config["discord"]["templates"]:
            if t["name"] == template_name:
                template = t
                break
        
        if template:
            # Load template into editor
            self.discord_title_entry.delete(0, tk.END)
            self.discord_title_entry.insert(0, template.get("title", ""))
            
            self.discord_template_text.delete("1.0", tk.END)
            self.discord_template_text.insert("1.0", template.get("message", ""))
            
            self.use_timestamps.set(template.get("useTimestamp", True))
            
            # Set timestamp format
            format_code = template.get("timestampFormat", "R")
            format_map = {
                "R": "R - Relative (in 2 hours)",
                "t": "t - Short Time (10:30 AM)",
                "T": "T - Long Time (10:30:00 AM)",
                "f": "f - Short Date/Time",
                "F": "F - Long Date/Time"
            }
            if format_code in format_map:
                self.timestamp_format_var.set(format_map[format_code])
            
            # Generate preview
            self.generate_discord_message()
    
    def edit_template(self):
        """Edit the selected template."""
        # Current template is already loaded in the editor
        messagebox.showinfo("Edit Template", "You can now edit the template. Click 'Save Template' when done.")
    
    def new_template(self):
        """Create a new template."""
        # Ask for template name
        dialog = tk.Toplevel(self.root)
        dialog.title("New Template")
        dialog.geometry("400x150")
        dialog.transient(self.root)
        dialog.grab_set()
        
        bg_color = "#1a1a2e"
        fg_color = "#eee"
        entry_bg = "#0f3460"
        
        dialog.configure(bg=bg_color)
        
        tk.Label(
            dialog,
            text="Template Name:",
            bg=bg_color,
            fg=fg_color
        ).pack(pady=10)
        
        name_entry = tk.Entry(
            dialog,
            bg=entry_bg,
            fg=fg_color,
            width=40
        )
        name_entry.pack(pady=5)
        
        def create_template():
            name = name_entry.get().strip()
            if name:
                # Check if name already exists
                for t in self.config["discord"]["templates"]:
                    if t["name"] == name:
                        messagebox.showerror("Error", "Template with this name already exists!")
                        return
                
                # Create new template
                new_template = {
                    "name": name,
                    "title": "🔴 Stream Announcement 🔴",
                    "message": "@everyone\n\n🎮 **Today's Schedule:**\n[today]\n\n📺 Join us at: [link]",
                    "useTimestamp": True,
                    "timestampFormat": "R"
                }
                
                self.config["discord"]["templates"].append(new_template)
                
                # Update combobox
                self.template_combo['values'] = [t["name"] for t in self.config["discord"]["templates"]]
                self.discord_template_var.set(name)
                self.on_template_selected()
                
                dialog.destroy()
        
        button_frame = tk.Frame(dialog, bg=bg_color)
        button_frame.pack(pady=20)
        
        tk.Button(
            button_frame,
            text="Create",
            command=create_template,
            bg="#9146FF",
            fg="white",
            padx=20,
            pady=5
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame,
            text="Cancel",
            command=dialog.destroy,
            bg="#6272a4",
            fg="white",
            padx=20,
            pady=5
        ).pack(side=tk.LEFT, padx=5)
    
    def delete_template(self):
        """Delete the selected template."""
        template_name = self.discord_template_var.get()
        
        if len(self.config["discord"]["templates"]) <= 1:
            messagebox.showerror("Error", "You must have at least one template!")
            return
        
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete the template '{template_name}'?"):
            # Remove template
            self.config["discord"]["templates"] = [
                t for t in self.config["discord"]["templates"] if t["name"] != template_name
            ]
            
            # Update combobox
            self.template_combo['values'] = [t["name"] for t in self.config["discord"]["templates"]]
            if self.config["discord"]["templates"]:
                self.discord_template_var.set(self.config["discord"]["templates"][0]["name"])
                self.on_template_selected()
    
    def save_template_changes(self):
        """Save changes to the current template."""
        template_name = self.discord_template_var.get()
        
        # Find and update the template
        for template in self.config["discord"]["templates"]:
            if template["name"] == template_name:
                template["title"] = self.discord_title_entry.get()
                template["message"] = self.discord_template_text.get("1.0", tk.END).strip()
                template["useTimestamp"] = self.use_timestamps.get()
                
                # Extract format code from combo selection
                format_str = self.timestamp_format_var.get()
                if format_str:
                    template["timestampFormat"] = format_str.split()[0]
                
                messagebox.showinfo("Success", f"Template '{template_name}' has been updated!")
                self.generate_discord_message()
                break
    
    def update_template_settings(self):
        """Update template settings and regenerate preview."""
        self.generate_discord_message()
    
    def parse_time_string(self, time_str):
        """Parse time string to hours and minutes."""
        import re
        match = re.match(r'(\d{1,2}):(\d{2})\s*(AM|PM)', time_str, re.IGNORECASE)
        if not match:
            return None
        
        hours = int(match.group(1))
        minutes = int(match.group(2))
        ampm = match.group(3).upper()
        
        # Convert to 24-hour format
        if ampm == 'PM' and hours != 12:
            hours += 12
        elif ampm == 'AM' and hours == 12:
            hours = 0
        
        return {'hours': hours, 'minutes': minutes}
    
    def get_timestamp(self, date, hours, minutes):
        """Get Unix timestamp for Discord."""
        from datetime import datetime
        d = datetime(date.year, date.month, date.day, hours, minutes, 0)
        return int(d.timestamp())
    
    def generate_discord_message(self):
        """Generate Discord message based on current settings."""
        try:
            # Get current template from editor
            message = self.discord_template_text.get("1.0", tk.END).strip()
            title = self.discord_title_entry.get()
            
            if not message or not title:
                return
            
            from datetime import datetime, timedelta
            today = datetime.now()
            tomorrow = today + timedelta(days=1)
            
            # Get schedule data
            today_type = self.config["schedule"]["today"]["type"]
            tomorrow_type = self.config["schedule"]["tomorrow"]["type"]
            today_schedule = self.config["schedule"]["today"][today_type]
            tomorrow_schedule = self.config["schedule"]["tomorrow"][tomorrow_type]
            
            # Format schedule times based on timestamp setting
            use_timestamps = self.use_timestamps.get()
            format_str = self.timestamp_format_var.get()
            format_char = format_str.split()[0] if format_str else "t"
            
            # Format today's times
            today_times = ""
            for i, slot in enumerate(today_schedule):
                if i > 0:
                    today_times += "\n"
                
                if use_timestamps:
                    # Parse time range
                    time_parts = slot['time'].split(' - ')
                    if len(time_parts) == 2:
                        start_time = self.parse_time_string(time_parts[0])
                        end_time = self.parse_time_string(time_parts[1])
                        
                        if start_time and end_time:
                            # Check if end time is midnight or past midnight
                            end_date = today
                            if end_time['hours'] < start_time['hours'] or (end_time['hours'] == 0 and end_time['minutes'] == 0):
                                end_date = tomorrow
                            
                            start_ts = self.get_timestamp(today, start_time['hours'], start_time['minutes'])
                            end_ts = self.get_timestamp(end_date, end_time['hours'], end_time['minutes'])
                            today_times += f"• <t:{start_ts}:{format_char}> to <t:{end_ts}:{format_char}> - **{slot['title']}**: {slot['desc']}"
                        else:
                            today_times += f"• **{slot['time']}** - {slot['title']}: {slot['desc']}"
                    else:
                        today_times += f"• **{slot['time']}** - {slot['title']}: {slot['desc']}"
                else:
                    today_times += f"• **{slot['time']}** - {slot['title']}: {slot['desc']}"
            
            # Format tomorrow's times
            tomorrow_times = ""
            day_after = tomorrow + timedelta(days=1)
            for i, slot in enumerate(tomorrow_schedule):
                if i > 0:
                    tomorrow_times += "\n"
                
                if use_timestamps:
                    # Parse time range
                    time_parts = slot['time'].split(' - ')
                    if len(time_parts) == 2:
                        start_time = self.parse_time_string(time_parts[0])
                        end_time = self.parse_time_string(time_parts[1])
                        
                        if start_time and end_time:
                            # Check if end time is midnight or past midnight
                            end_date = tomorrow
                            if end_time['hours'] < start_time['hours'] or (end_time['hours'] == 0 and end_time['minutes'] == 0):
                                end_date = day_after
                            
                            start_ts = self.get_timestamp(tomorrow, start_time['hours'], start_time['minutes'])
                            end_ts = self.get_timestamp(end_date, end_time['hours'], end_time['minutes'])
                            tomorrow_times += f"• <t:{start_ts}:{format_char}> to <t:{end_ts}:{format_char}> - **{slot['title']}**: {slot['desc']}"
                        else:
                            tomorrow_times += f"• **{slot['time']}** - {slot['title']}: {slot['desc']}"
                    else:
                        tomorrow_times += f"• **{slot['time']}** - {slot['title']}: {slot['desc']}"
                else:
                    tomorrow_times += f"• **{slot['time']}** - {slot['title']}: {slot['desc']}"
            
            # Dynamic timezone text
            timezone_text = f"``Times auto-adjust to your timezone!``" if use_timestamps else f"``{self.config['timezone']}``"
            
            # Replace placeholders (matching HTML implementation)
            replacements = {
                "[title]": title,
                "[today]": today_times,
                "[tomorrow]": tomorrow_times,
                "[timezone]": timezone_text,
                "[link]": self.config["channel"]["link"]
            }
            
            output_message = message
            for key, value in replacements.items():
                output_message = output_message.replace(key, value)
            
            # Final output (title is already in the message template)
            self.discord_output.delete("1.0", tk.END)
            self.discord_output.insert("1.0", output_message)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate message: {e}")
    
    # This method is no longer needed as formatting is done in generate_discord_message
    
    def copy_discord_message(self):
        """Copy Discord message to clipboard."""
        try:
            message = self.discord_output.get("1.0", tk.END).strip()
            if message:
                self.root.clipboard_clear()
                self.root.clipboard_append(message)
                messagebox.showinfo("Success", "Message copied to clipboard!")
            else:
                messagebox.showwarning("Warning", "No message to copy!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy message: {e}")
    
    def save_all_changes(self):
        """Save all changes from all tabs."""
        # Update config from GUI
        self.config["channel"]["name"] = self.name_entry.get()
        self.config["channel"]["link"] = self.link_entry.get()
        self.config["timezone"] = self.timezone_entry.get()
        self.config["theme"] = self.theme_var.get()
        self.config["exportScope"] = self.export_scope.get()
        
        # Update schedule types and titles
        self.config["schedule"]["today"]["type"] = self.today_type.get()
        self.config["schedule"]["today"]["title"] = self.today_title_entry.get()
        self.config["schedule"]["tomorrow"]["type"] = self.tomorrow_type.get()
        self.config["schedule"]["tomorrow"]["title"] = self.tomorrow_title_entry.get()
        
        # Update all slots from editors
        for frame_key, frames in self.slot_frames.items():
            day, stype = frame_key.split('_')
            slots = []
            for frame in frames:
                slots.append(frame.get_slot_data())
            self.config["schedule"][day][stype] = slots
        
        if self.save_config():
            messagebox.showinfo("Success", "All changes saved successfully!")
        else:
            messagebox.showerror("Error", "Failed to save configuration!")
    
    def reload_configuration(self):
        """Reload configuration from file."""
        if messagebox.askyesno("Confirm Reload", "This will discard any unsaved changes. Continue?"):
            self.config = self.load_config()
            # Refresh GUI - would need to recreate widgets
            messagebox.showinfo("Success", "Configuration reloaded! Please restart the application to see changes.")
    
    def run(self):
        """Run the application."""
        # Ask user if they want to start the server
        response = messagebox.askyesno(
            "Start Server",
            "Would you like to start the npm server?\n\n" +
            "This will run 'npm start' in the HTML directory.\n" +
            "Make sure Node.js and npm are installed."
        )
        
        if response:
            self.start_server()
        
        self.create_gui()
        self.generate_discord_message()
        self.root.mainloop()


def main():
    """Main function."""
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
