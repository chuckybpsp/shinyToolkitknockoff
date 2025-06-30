#!/usr/bin/env python3
"""
Backup Toolkit - A scheduled backup application
Clone of FOCUS Toolkit for backing up folders on a schedule
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import shutil
import json
import threading
import time
from datetime import datetime, timedelta
import schedule
from pathlib import Path

class BackupToolkit:
    def __init__(self, root):
        self.root = root
        self.root.title("Backup Toolkit")
        self.root.geometry("400x600")
        self.root.configure(bg='#2b2b2b')
        
        # Configuration file
        self.config_file = "backup_config.json"
        
        # Default values
        self.source_folder = ""
        self.backup_location = ""
        self.backup_time = "00:00"
        self.selected_days = []
        self.auto_launch = False
        self.daily_backup_enabled = False
        self.clean_after_backup = False
        
        # Load existing configuration
        self.load_config()
        
        # Setup GUI
        self.setup_gui()
        
        # Start scheduler thread
        self.scheduler_running = True
        self.scheduler_thread = threading.Thread(target=self.run_scheduler, daemon=True)
        self.scheduler_thread.start()
        
    def setup_gui(self):
        # Title
        title_frame = tk.Frame(self.root, bg='#2b2b2b')
        title_frame.pack(pady=20)
        
        title_label = tk.Label(title_frame, text="Backup Toolkit", 
                              font=("Arial", 18, "bold"), 
                              fg='white', bg='#2b2b2b')
        title_label.pack()
        
        subtitle_label = tk.Label(title_frame, text="Scheduled Backups for Data Sources", 
                                 font=("Arial", 10), 
                                 fg='#cccccc', bg='#2b2b2b')
        subtitle_label.pack()
        
        # Reset button
        reset_button = tk.Button(title_frame, text="Reset", 
                                bg='#d32f2f', fg='white',
                                font=("Arial", 10, "bold"),
                                command=self.reset_config)
        reset_button.pack(side='right', padx=(20, 0))
        
        # Manual backup button
        backup_button = tk.Button(self.root, text="Backup Now",
                                 bg='#424242', fg='white',
                                 font=("Arial", 12, "bold"),
                                 width=15, height=2,
                                 command=self.backup_now)
        backup_button.pack(pady=20)
        
        # Backup Schedule Section
        schedule_frame = tk.LabelFrame(self.root, text="Backup Schedule",
                                      fg='white', bg='#2b2b2b',
                                      font=("Arial", 12, "bold"))
        schedule_frame.pack(fill='x', padx=20, pady=10)
        
        # Backup Time
        time_frame = tk.Frame(schedule_frame, bg='#2b2b2b')
        time_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Label(time_frame, text="Backup Time:", 
                fg='white', bg='#2b2b2b').pack(side='left')
        
        self.time_var = tk.StringVar(value=self.backup_time)
        time_entry = tk.Entry(time_frame, textvariable=self.time_var, width=10)
        time_entry.pack(side='left', padx=(10, 0))
        
        # Help icon (simplified as text)
        tk.Label(time_frame, text="ⓘ", fg='#888888', bg='#2b2b2b').pack(side='left', padx=(5, 0))
        
        # Days of week
        days_frame = tk.Frame(schedule_frame, bg='#2b2b2b')
        days_frame.pack(fill='x', padx=10, pady=10)
        
        self.day_vars = {}
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        
        for i, day in enumerate(days):
            var = tk.BooleanVar(value=day.lower() in self.selected_days)
            self.day_vars[day.lower()] = var
            
            cb = tk.Checkbutton(days_frame, text=day, variable=var,
                               fg='white', bg='#2b2b2b', 
                               selectcolor='#424242',
                               activebackground='#2b2b2b',
                               activeforeground='white')
            cb.grid(row=0, column=i, padx=5, sticky='w')
        
        # Save button
        save_button = tk.Button(schedule_frame, text="Save",
                               bg='#424242', fg='white',
                               font=("Arial", 10, "bold"),
                               command=self.save_schedule)
        save_button.pack(pady=10)
        
        # Options
        options_frame = tk.Frame(self.root, bg='#2b2b2b')
        options_frame.pack(fill='x', padx=20, pady=20)
        
        # Auto-launch checkbox
        self.auto_launch_var = tk.BooleanVar(value=self.auto_launch)
        auto_launch_cb = tk.Checkbutton(options_frame, text="Auto-launch at login:",
                                       variable=self.auto_launch_var,
                                       fg='white', bg='#2b2b2b',
                                       selectcolor='#424242',
                                       activebackground='#2b2b2b',
                                       activeforeground='white',
                                       command=self.save_config)
        auto_launch_cb.pack(anchor='w')
        
        # Enable Daily Backup checkbox
        self.daily_backup_var = tk.BooleanVar(value=self.daily_backup_enabled)
        daily_backup_cb = tk.Checkbutton(options_frame, text="Enable Daily Backup",
                                        variable=self.daily_backup_var,
                                        fg='white', bg='#2b2b2b',
                                        selectcolor='#424242',
                                        activebackground='#2b2b2b',
                                        activeforeground='white',
                                        command=self.save_config)
        daily_backup_cb.pack(anchor='w', pady=(10, 0))
        
        # Clean Data Source after Backup checkbox
        self.clean_var = tk.BooleanVar(value=self.clean_after_backup)
        clean_cb = tk.Checkbutton(options_frame, text="Clean Data Source after Backup?",
                                 variable=self.clean_var,
                                 fg='white', bg='#2b2b2b',
                                 selectcolor='#424242',
                                 activebackground='#2b2b2b',
                                 activeforeground='white',
                                 command=self.save_config)
        clean_cb.pack(anchor='w', pady=(10, 0))
        
        # Folder selection buttons
        buttons_frame = tk.Frame(self.root, bg='#2b2b2b')
        buttons_frame.pack(fill='x', padx=20, pady=20)
        
        source_button = tk.Button(buttons_frame, text="Choose Data Source Folder",
                                 bg='#424242', fg='white',
                                 font=("Arial", 10, "bold"),
                                 command=self.choose_source_folder)
        source_button.pack(fill='x', pady=(0, 10))
        
        backup_button = tk.Button(buttons_frame, text="Choose Backup Location",
                                 bg='#424242', fg='white',
                                 font=("Arial", 10, "bold"),
                                 command=self.choose_backup_location)
        backup_button.pack(fill='x')
        
        # Status frame
        status_frame = tk.Frame(self.root, bg='#2b2b2b')
        status_frame.pack(fill='x', padx=20, pady=(20, 10))
        
        # Version info
        version_label = tk.Label(status_frame, text="v1.0.0-20241220-1539",
                                font=("Arial", 8),
                                fg='#888888', bg='#2b2b2b')
        version_label.pack(side='left')
        
        # Debug menu (placeholder)
        debug_label = tk.Label(status_frame, text="Debug Menu",
                              font=("Arial", 8),
                              fg='#888888', bg='#2b2b2b')
        debug_label.pack(side='right')
    
    def choose_source_folder(self):
        folder = filedialog.askdirectory(title="Select Data Source Folder")
        if folder:
            self.source_folder = folder
            self.save_config()
            messagebox.showinfo("Source Folder", f"Selected: {folder}")
    
    def choose_backup_location(self):
        folder = filedialog.askdirectory(title="Select Backup Location")
        if folder:
            self.backup_location = folder
            self.save_config()
            messagebox.showinfo("Backup Location", f"Selected: {folder}")
    
    def save_schedule(self):
        self.backup_time = self.time_var.get()
        self.selected_days = [day for day, var in self.day_vars.items() if var.get()]
        self.save_config()
        self.update_schedule()
        messagebox.showinfo("Schedule Saved", "Backup schedule has been updated!")
    
    def backup_now(self):
        if not self.source_folder or not self.backup_location:
            messagebox.showerror("Error", "Please select both source folder and backup location first!")
            return
        
        if not os.path.exists(self.source_folder):
            messagebox.showerror("Error", "Source folder does not exist!")
            return
        
        if not os.path.exists(self.backup_location):
            messagebox.showerror("Error", "Backup location does not exist!")
            return
        
        # Run backup in a separate thread
        backup_thread = threading.Thread(target=self._perform_backup, daemon=True)
        backup_thread.start()
    
    def _perform_backup(self):
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            source_name = os.path.basename(self.source_folder)
            backup_folder_name = f"{source_name}_backup_{timestamp}"
            backup_path = os.path.join(self.backup_location, backup_folder_name)
            
            # Show progress (simplified)
            self.root.after(0, lambda: messagebox.showinfo("Backup Started", "Backup in progress..."))
            
            # Perform the backup
            shutil.copytree(self.source_folder, backup_path)
            
            # Clean source if option is enabled
            if self.clean_after_backup and self.clean_var.get():
                for item in os.listdir(self.source_folder):
                    item_path = os.path.join(self.source_folder, item)
                    if os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                    else:
                        os.remove(item_path)
            
            self.root.after(0, lambda: messagebox.showinfo("Backup Complete", 
                                                           f"Backup completed successfully!\nSaved to: {backup_path}"))
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Backup Failed", f"Error during backup: {str(e)}"))
    
    def update_schedule(self):
        # Clear existing schedule
        schedule.clear()
        
        # Add new scheduled jobs
        if self.selected_days and self.backup_time:
            try:
                for day in self.selected_days:
                    if day == 'mon':
                        schedule.every().monday.at(self.backup_time).do(self._scheduled_backup)
                    elif day == 'tue':
                        schedule.every().tuesday.at(self.backup_time).do(self._scheduled_backup)
                    elif day == 'wed':
                        schedule.every().wednesday.at(self.backup_time).do(self._scheduled_backup)
                    elif day == 'thu':
                        schedule.every().thursday.at(self.backup_time).do(self._scheduled_backup)
                    elif day == 'fri':
                        schedule.every().friday.at(self.backup_time).do(self._scheduled_backup)
                    elif day == 'sat':
                        schedule.every().saturday.at(self.backup_time).do(self._scheduled_backup)
                    elif day == 'sun':
                        schedule.every().sunday.at(self.backup_time).do(self._scheduled_backup)
                
                # Add daily backup if enabled
                if self.daily_backup_enabled and self.daily_backup_var.get():
                    schedule.every().day.at(self.backup_time).do(self._scheduled_backup)
                    
            except Exception as e:
                print(f"Error setting up schedule: {e}")
    
    def _scheduled_backup(self):
        if self.source_folder and self.backup_location:
            self._perform_backup()
    
    def run_scheduler(self):
        while self.scheduler_running:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    def load_config(self):
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.source_folder = config.get('source_folder', '')
                    self.backup_location = config.get('backup_location', '')
                    self.backup_time = config.get('backup_time', '00:00')
                    self.selected_days = config.get('selected_days', [])
                    self.auto_launch = config.get('auto_launch', False)
                    self.daily_backup_enabled = config.get('daily_backup_enabled', False)
                    self.clean_after_backup = config.get('clean_after_backup', False)
        except Exception as e:
            print(f"Error loading config: {e}")
    
    def save_config(self):
        config = {
            'source_folder': self.source_folder,
            'backup_location': self.backup_location,
            'backup_time': self.backup_time,
            'selected_days': self.selected_days,
            'auto_launch': self.auto_launch_var.get() if hasattr(self, 'auto_launch_var') else self.auto_launch,
            'daily_backup_enabled': self.daily_backup_var.get() if hasattr(self, 'daily_backup_var') else self.daily_backup_enabled,
            'clean_after_backup': self.clean_var.get() if hasattr(self, 'clean_var') else self.clean_after_backup
        }
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def reset_config(self):
        if messagebox.askyesno("Reset Configuration", "Are you sure you want to reset all settings?"):
            self.source_folder = ""
            self.backup_location = ""
            self.backup_time = "00:00"
            self.selected_days = []
            self.auto_launch = False
            self.daily_backup_enabled = False
            self.clean_after_backup = False
            
            # Reset GUI elements
            self.time_var.set("00:00")
            for var in self.day_vars.values():
                var.set(False)
            self.auto_launch_var.set(False)
            self.daily_backup_var.set(False)
            self.clean_var.set(False)
            
            self.save_config()
            schedule.clear()
            messagebox.showinfo("Reset Complete", "Configuration has been reset!")
    
    def on_closing(self):
        self.scheduler_running = False
        self.save_config()
        self.root.destroy()

def main():
    root = tk.Tk()
    app = BackupToolkit(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()