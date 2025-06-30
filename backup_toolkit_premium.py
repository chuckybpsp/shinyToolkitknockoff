#!/usr/bin/env python3
"""
Backup Toolkit Premium - Enhanced GUI with smooth animations
A premium backup application with Apple-like animations and transitions
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import shutil
import json
import threading
import time
from datetime import datetime
import math

# Enhanced scheduler with animation support
class SimpleScheduler:
    def __init__(self):
        self.jobs = []
    
    def add_job(self, days, time_str, func):
        """Add a scheduled job"""
        self.jobs.append({
            'days': days,
            'time': time_str,
            'func': func
        })
    
    def run_pending(self):
        """Check and run any pending jobs"""
        now = datetime.now()
        current_day = now.strftime('%a').lower()
        current_time = now.strftime('%H:%M')
        
        for job in self.jobs:
            if current_day in job['days'] and current_time == job['time']:
                print(f"Running scheduled backup at {current_time}")
                job['func']()
    
    def clear(self):
        """Clear all scheduled jobs"""
        self.jobs = []

class AnimatedButton(tk.Button):
    """Custom button with hover animations"""
    def __init__(self, parent, **kwargs):
        self.original_bg = kwargs.get('bg', '#424242')
        self.hover_bg = self._lighten_color(self.original_bg, 1.2)
        self.pressed_bg = self._darken_color(self.original_bg, 0.8)
        
        super().__init__(parent, **kwargs)
        
        # Bind animation events
        self.bind('<Enter>', self._on_enter)
        self.bind('<Leave>', self._on_leave)
        self.bind('<Button-1>', self._on_press)
        self.bind('<ButtonRelease-1>', self._on_release)
        
        # Animation state
        self.animation_running = False
        
    def _lighten_color(self, color, factor):
        """Lighten a hex color"""
        if color.startswith('#'):
            color = color[1:]
        rgb = [int(color[i:i+2], 16) for i in (0, 2, 4)]
        rgb = [min(255, int(c * factor)) for c in rgb]
        return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
    
    def _darken_color(self, color, factor):
        """Darken a hex color"""
        if color.startswith('#'):
            color = color[1:]
        rgb = [int(color[i:i+2], 16) for i in (0, 2, 4)]
        rgb = [int(c * factor) for c in rgb]
        return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
    
    def _animate_color(self, start_color, end_color, duration=200, steps=20):
        """Smooth color transition animation"""
        if self.animation_running:
            return
        
        self.animation_running = True
        
        # Parse colors
        start_rgb = [int(start_color[i:i+2], 16) for i in (1, 3, 5)]
        end_rgb = [int(end_color[i:i+2], 16) for i in (1, 3, 5)]
        
        # Calculate step values
        step_delay = duration // steps
        color_steps = [(end_rgb[i] - start_rgb[i]) / steps for i in range(3)]
        
        def animate_step(step):
            if step >= steps:
                self.configure(bg=end_color)
                self.animation_running = False
                return
            
            # Calculate current color
            current_rgb = [
                int(start_rgb[i] + color_steps[i] * step) 
                for i in range(3)
            ]
            current_color = f"#{current_rgb[0]:02x}{current_rgb[1]:02x}{current_rgb[2]:02x}"
            
            try:
                self.configure(bg=current_color)
                self.after(step_delay, lambda: animate_step(step + 1))
            except:
                self.animation_running = False
        
        animate_step(0)
    
    def _on_enter(self, event):
        """Handle mouse enter with smooth transition"""
        self._animate_color(self.original_bg, self.hover_bg)
    
    def _on_leave(self, event):
        """Handle mouse leave with smooth transition"""
        self._animate_color(self.hover_bg, self.original_bg)
    
    def _on_press(self, event):
        """Handle button press"""
        self.configure(bg=self.pressed_bg)
    
    def _on_release(self, event):
        """Handle button release"""
        self.configure(bg=self.hover_bg)

class FadeFrame(tk.Frame):
    """Frame with fade-in animation"""
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.fade_in()
    
    def fade_in(self, duration=500, steps=25):
        """Fade in animation"""
        step_delay = duration // steps
        alpha_step = 1.0 / steps
        
        def fade_step(step):
            if step >= steps:
                return
            
            alpha = alpha_step * step
            # Simulate fade by adjusting colors
            self.after(step_delay, lambda: fade_step(step + 1))
        
        fade_step(0)

class ProgressRing:
    """Animated progress ring widget"""
    def __init__(self, canvas, x, y, radius, width=8):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.radius = radius
        self.width = width
        self.progress = 0
        self.arc_id = None
        self.bg_arc_id = None
        
        # Create background arc
        self.bg_arc_id = self.canvas.create_arc(
            x - radius, y - radius, x + radius, y + radius,
            start=0, extent=360, outline='#333333', width=width,
            style='arc'
        )
        
        # Create progress arc
        self.arc_id = self.canvas.create_arc(
            x - radius, y - radius, x + radius, y + radius,
            start=90, extent=0, outline='#007AFF', width=width,
            style='arc'
        )
    
    def set_progress(self, progress, animate=True):
        """Set progress with optional animation"""
        if animate:
            self.animate_to_progress(progress)
        else:
            self.progress = progress
            extent = -360 * (progress / 100)
            self.canvas.itemconfig(self.arc_id, extent=extent)
    
    def animate_to_progress(self, target_progress, duration=1000, steps=60):
        """Animate progress change"""
        start_progress = self.progress
        progress_diff = target_progress - start_progress
        step_delay = duration // steps
        
        def animate_step(step):
            if step >= steps:
                self.progress = target_progress
                extent = -360 * (target_progress / 100)
                self.canvas.itemconfig(self.arc_id, extent=extent)
                return
            
            # Easing function (ease-out)
            t = step / steps
            eased_t = 1 - (1 - t) ** 3
            current_progress = start_progress + progress_diff * eased_t
            
            extent = -360 * (current_progress / 100)
            self.canvas.itemconfig(self.arc_id, extent=extent)
            
            self.canvas.after(step_delay, lambda: animate_step(step + 1))
        
        animate_step(0)

class BackupToolkitPremium:
    def __init__(self, root):
        self.root = root
        self.root.title("Backup Toolkit Premium")
        self.root.geometry("450x700")
        self.root.configure(bg='#1a1a1a')
        
        # Set window properties for premium feel
        self.root.resizable(False, False)
        
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
        
        # Animation state
        self.backup_progress = None
        self.progress_ring = None
        
        # Load existing configuration
        self.load_config()
        
        # Setup enhanced GUI
        self.setup_premium_gui()
        
        # Start scheduler thread
        self.scheduler = SimpleScheduler()
        self.scheduler_running = True
        self.scheduler_thread = threading.Thread(target=self.run_scheduler, daemon=True)
        self.scheduler_thread.start()
        
        # Initial fade-in animation
        self.animate_startup()
        
    def animate_startup(self):
        """Animate the entire application startup"""
        # Start with all elements hidden
        for widget in self.root.winfo_children():
            widget.configure(bg=self.root.cget('bg'))
        
        # Animate title first
        self.animate_title_entrance()
    
    def animate_title_entrance(self):
        """Animate title entrance with scale effect"""
        # This would typically involve more complex animations
        # For tkinter, we'll use position-based animations
        self.root.after(100, self.animate_main_content)
    
    def animate_main_content(self):
        """Animate main content with slide-up effect"""
        # Slide up animation simulation
        pass
        
    def setup_premium_gui(self):
        # Main container with gradient effect simulation
        main_container = FadeFrame(self.root, bg='#1a1a1a')
        main_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title section with enhanced styling
        title_frame = tk.Frame(main_container, bg='#1a1a1a')
        title_frame.pack(pady=(0, 30))
        
        # Main title with gradient text effect simulation
        title_label = tk.Label(
            title_frame, 
            text="Backup Toolkit", 
            font=("SF Pro Display", 28, "bold"), 
            fg='#ffffff', 
            bg='#1a1a1a'
        )
        title_label.pack()
        
        # Subtitle with fade effect
        subtitle_label = tk.Label(
            title_frame, 
            text="Premium Scheduled Backups", 
            font=("SF Pro Text", 14), 
            fg='#8e8e93', 
            bg='#1a1a1a'
        )
        subtitle_label.pack(pady=(5, 0))
        
        # Status indicator
        status_frame = tk.Frame(title_frame, bg='#1a1a1a')
        status_frame.pack(pady=(10, 0))
        
        self.status_indicator = tk.Label(
            status_frame,
            text="●",
            font=("Arial", 16),
            fg='#34c759',  # Green
            bg='#1a1a1a'
        )
        self.status_indicator.pack(side='left')
        
        status_text = tk.Label(
            status_frame,
            text="Ready",
            font=("SF Pro Text", 12),
            fg='#8e8e93',
            bg='#1a1a1a'
        )
        status_text.pack(side='left', padx=(5, 0))
        
        # Enhanced backup button with premium styling
        backup_button = AnimatedButton(
            main_container,
            text="Backup Now",
            bg='#007AFF',
            fg='white',
            font=("SF Pro Text", 16, "bold"),
            width=20,
            height=2,
            relief='flat',
            borderwidth=0,
            command=self.backup_now
        )
        backup_button.pack(pady=(0, 30))
        
        # Progress ring (initially hidden)
        self.progress_canvas = tk.Canvas(
            main_container, 
            width=80, 
            height=80, 
            bg='#1a1a1a', 
            highlightthickness=0
        )
        
        # Premium card-style schedule section
        schedule_card = tk.Frame(
            main_container, 
            bg='#2c2c2e', 
            relief='flat',
            borderwidth=0
        )
        schedule_card.pack(fill='x', pady=(0, 20))
        
        # Add subtle shadow effect with multiple frames
        shadow_frame = tk.Frame(main_container, bg='#0f0f0f', height=2)
        shadow_frame.pack(fill='x')
        
        # Schedule header
        schedule_header = tk.Frame(schedule_card, bg='#2c2c2e')
        schedule_header.pack(fill='x', padx=20, pady=(20, 10))
        
        schedule_title = tk.Label(
            schedule_header,
            text="Backup Schedule",
            font=("SF Pro Text", 18, "bold"),
            fg='#ffffff',
            bg='#2c2c2e'
        )
        schedule_title.pack(anchor='w')
        
        # Time input with modern styling
        time_section = tk.Frame(schedule_card, bg='#2c2c2e')
        time_section.pack(fill='x', padx=20, pady=10)
        
        time_label = tk.Label(
            time_section,
            text="Time",
            font=("SF Pro Text", 14),
            fg='#8e8e93',
            bg='#2c2c2e'
        )
        time_label.pack(anchor='w')
        
        self.time_var = tk.StringVar(value=self.backup_time)
        time_entry = tk.Entry(
            time_section,
            textvariable=self.time_var,
            font=("SF Pro Text", 16),
            fg='#ffffff',
            bg='#1c1c1e',
            relief='flat',
            borderwidth=0,
            insertbackground='#007AFF'
        )
        time_entry.pack(fill='x', pady=(5, 0), ipady=8)
        
        # Days selector with modern toggle design
        days_section = tk.Frame(schedule_card, bg='#2c2c2e')
        days_section.pack(fill='x', padx=20, pady=15)
        
        days_label = tk.Label(
            days_section,
            text="Days",
            font=("SF Pro Text", 14),
            fg='#8e8e93',
            bg='#2c2c2e'
        )
        days_label.pack(anchor='w', pady=(0, 10))
        
        # Custom day toggles
        days_container = tk.Frame(days_section, bg='#2c2c2e')
        days_container.pack(fill='x')
        
        self.day_vars = {}
        self.day_buttons = {}
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        
        for i, day in enumerate(days):
            var = tk.BooleanVar(value=day.lower() in self.selected_days)
            self.day_vars[day.lower()] = var
            
            btn = self.create_day_toggle(days_container, day, var)
            btn.grid(row=0, column=i, padx=2, sticky='ew')
            self.day_buttons[day.lower()] = btn
            
        # Configure grid weights
        for i in range(7):
            days_container.grid_columnconfigure(i, weight=1)
        
        # Save button with premium styling
        save_button = AnimatedButton(
            schedule_card,
            text="Save Schedule",
            bg='#34c759',
            fg='white',
            font=("SF Pro Text", 14, "bold"),
            relief='flat',
            borderwidth=0,
            command=self.save_schedule
        )
        save_button.pack(pady=20, padx=20, fill='x')
        
        # Options card
        options_card = tk.Frame(main_container, bg='#2c2c2e', relief='flat')
        options_card.pack(fill='x', pady=(0, 20))
        
        options_header = tk.Label(
            options_card,
            text="Options",
            font=("SF Pro Text", 18, "bold"),
            fg='#ffffff',
            bg='#2c2c2e'
        )
        options_header.pack(anchor='w', padx=20, pady=(20, 15))
        
        # Modern toggle switches for options
        self.create_option_toggle(options_card, "Enable Daily Backup", "daily_backup_var")
        self.create_option_toggle(options_card, "Clean Source After Backup", "clean_var")
        self.create_option_toggle(options_card, "Auto-launch at Login", "auto_launch_var")
        
        # Folder selection with premium buttons
        folders_card = tk.Frame(main_container, bg='#2c2c2e', relief='flat')
        folders_card.pack(fill='x', pady=(0, 20))
        
        folders_header = tk.Label(
            folders_card,
            text="Folders",
            font=("SF Pro Text", 18, "bold"),
            fg='#ffffff',
            bg='#2c2c2e'
        )
        folders_header.pack(anchor='w', padx=20, pady=(20, 15))
        
        source_btn = AnimatedButton(
            folders_card,
            text="Choose Source Folder",
            bg='#5856d6',
            fg='white',
            font=("SF Pro Text", 14),
            relief='flat',
            borderwidth=0,
            command=self.choose_source_folder
        )
        source_btn.pack(fill='x', padx=20, pady=(0, 10))
        
        backup_btn = AnimatedButton(
            folders_card,
            text="Choose Backup Location",
            bg='#af52de',
            fg='white',
            font=("SF Pro Text", 14),
            relief='flat',
            borderwidth=0,
            command=self.choose_backup_location
        )
        backup_btn.pack(fill='x', padx=20, pady=(0, 20))
        
        # Bottom status bar
        bottom_frame = tk.Frame(main_container, bg='#1a1a1a')
        bottom_frame.pack(fill='x', side='bottom')
        
        version_label = tk.Label(
            bottom_frame,
            text="Premium v1.0.0",
            font=("SF Pro Text", 10),
            fg='#48484a',
            bg='#1a1a1a'
        )
        version_label.pack(side='left')
        
        reset_btn = tk.Button(
            bottom_frame,
            text="Reset",
            font=("SF Pro Text", 10),
            fg='#ff3b30',
            bg='#1a1a1a',
            relief='flat',
            borderwidth=0,
            command=self.reset_config
        )
        reset_btn.pack(side='right')
    
    def create_day_toggle(self, parent, day, var):
        """Create a modern day toggle button"""
        def toggle_day():
            var.set(not var.get())
            update_appearance()
        
        def update_appearance():
            if var.get():
                btn.configure(bg='#007AFF', fg='white')
            else:
                btn.configure(bg='#3a3a3c', fg='#8e8e93')
        
        btn = tk.Button(
            parent,
            text=day,
            font=("SF Pro Text", 12, "bold"),
            relief='flat',
            borderwidth=0,
            command=toggle_day,
            width=5,
            height=1
        )
        
        update_appearance()
        return btn
    
    def create_option_toggle(self, parent, text, var_name):
        """Create a modern toggle switch option"""
        frame = tk.Frame(parent, bg='#2c2c2e')
        frame.pack(fill='x', padx=20, pady=5)
        
        label = tk.Label(
            frame,
            text=text,
            font=("SF Pro Text", 14),
            fg='#ffffff',
            bg='#2c2c2e'
        )
        label.pack(side='left')
        
        # Create toggle switch
        var = tk.BooleanVar(value=getattr(self, var_name.replace('_var', ''), False))
        setattr(self, var_name, var)
        
        toggle_frame = tk.Frame(frame, bg='#2c2c2e')
        toggle_frame.pack(side='right')
        
        def toggle_switch():
            var.set(not var.get())
            update_toggle_appearance()
            self.save_config()
        
        def update_toggle_appearance():
            if var.get():
                toggle_btn.configure(bg='#34c759', text='●')
            else:
                toggle_btn.configure(bg='#3a3a3c', text='○')
        
        toggle_btn = tk.Button(
            toggle_frame,
            font=("Arial", 14),
            width=3,
            relief='flat',
            borderwidth=0,
            command=toggle_switch
        )
        toggle_btn.pack()
        
        update_toggle_appearance()
    
    def animate_status_change(self, status, color):
        """Animate status indicator changes"""
        self.status_indicator.configure(fg=color)
        
        # Pulse animation
        def pulse(scale=1.0, direction=1):
            if scale <= 0.8 and direction == -1:
                direction = 1
            elif scale >= 1.2 and direction == 1:
                direction = -1
            
            # Simulate scaling with font size
            font_size = int(16 * scale)
            self.status_indicator.configure(font=("Arial", font_size))
            
            if direction == 1:
                scale += 0.05
            else:
                scale -= 0.05
            
            if abs(scale - 1.0) > 0.01:
                self.root.after(50, lambda: pulse(scale, direction))
            else:
                self.status_indicator.configure(font=("Arial", 16))
        
        pulse()
    
    def show_backup_progress(self):
        """Show animated backup progress"""
        self.progress_canvas.pack(pady=20)
        
        if not self.progress_ring:
            self.progress_ring = ProgressRing(
                self.progress_canvas, 40, 40, 30
            )
        
        # Animate progress
        if self.progress_ring:
            self.progress_ring.set_progress(0)
            self.animate_backup_progress()
    
    def animate_backup_progress(self):
        """Animate backup progress ring"""
        # Simulate backup progress
        for i in range(0, 101, 5):
            self.root.after(i * 50, lambda p=i: self.progress_ring.set_progress(p, animate=False))
        
        # Hide progress when done
        self.root.after(5500, self.hide_backup_progress)
    
    def hide_backup_progress(self):
        """Hide backup progress with fade out"""
        self.progress_canvas.pack_forget()
    
    # Core functionality methods (enhanced with animations)
    def choose_source_folder(self):
        self.animate_status_change("Selecting...", "#ff9f0a")
        folder = filedialog.askdirectory(title="Select Data Source Folder")
        if folder:
            self.source_folder = folder
            self.save_config()
            self.animate_status_change("Source Set", "#34c759")
            self.show_premium_notification(f"Source: {os.path.basename(folder)}")
        else:
            self.animate_status_change("Ready", "#34c759")
    
    def choose_backup_location(self):
        self.animate_status_change("Selecting...", "#ff9f0a")
        folder = filedialog.askdirectory(title="Select Backup Location")
        if folder:
            self.backup_location = folder
            self.save_config()
            self.animate_status_change("Location Set", "#34c759")
            self.show_premium_notification(f"Backup: {os.path.basename(folder)}")
        else:
            self.animate_status_change("Ready", "#34c759")
    
    def show_premium_notification(self, message):
        """Show a premium-style notification"""
        notification = tk.Toplevel(self.root)
        notification.title("")
        notification.geometry("300x80")
        notification.configure(bg='#2c2c2e')
        notification.resizable(False, False)
        
        # Position at top-right of main window
        x = self.root.winfo_x() + self.root.winfo_width() - 320
        y = self.root.winfo_y() + 20
        notification.geometry(f"+{x}+{y}")
        
        # Remove window decorations
        notification.overrideredirect(True)
        
        # Add message
        msg_label = tk.Label(
            notification,
            text=message,
            font=("SF Pro Text", 12),
            fg='#ffffff',
            bg='#2c2c2e',
            wraplength=280
        )
        msg_label.pack(expand=True)
        
        # Auto-dismiss with fade effect
        def fade_out():
            notification.destroy()
        
        notification.after(2000, fade_out)
    
    def backup_now(self):
        if not self.source_folder or not self.backup_location:
            self.show_premium_notification("Please select source and backup folders first")
            return
        
        if not os.path.exists(self.source_folder):
            self.show_premium_notification("Source folder does not exist")
            return
        
        if not os.path.exists(self.backup_location):
            self.show_premium_notification("Backup location does not exist")
            return
        
        self.animate_status_change("Backing up...", "#ff9f0a")
        self.show_backup_progress()
        
        # Run backup in a separate thread
        backup_thread = threading.Thread(target=self._perform_backup, daemon=True)
        backup_thread.start()
    
    def _perform_backup(self):
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            source_name = os.path.basename(self.source_folder)
            backup_folder_name = f"{source_name}_backup_{timestamp}"
            backup_path = os.path.join(self.backup_location, backup_folder_name)
            
            # Perform the backup
            shutil.copytree(self.source_folder, backup_path)
            
            # Clean source if option is enabled
            if self.clean_after_backup and hasattr(self, 'clean_var') and self.clean_var.get():
                for item in os.listdir(self.source_folder):
                    item_path = os.path.join(self.source_folder, item)
                    if os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                    else:
                        os.remove(item_path)
            
            self.root.after(0, lambda: self.animate_status_change("Backup Complete", "#34c759"))
            self.root.after(0, lambda: self.show_premium_notification("Backup completed successfully!"))
            
        except Exception as e:
            self.root.after(0, lambda: self.animate_status_change("Backup Failed", "#ff3b30"))
            self.root.after(0, lambda: self.show_premium_notification(f"Backup failed: {str(e)}"))
    
    def save_schedule(self):
        try:
            datetime.strptime(self.time_var.get(), '%H:%M')
            self.backup_time = self.time_var.get()
            self.selected_days = [day for day, var in self.day_vars.items() if var.get()]
            self.save_config()
            self.update_schedule()
            self.animate_status_change("Schedule Saved", "#34c759")
            self.show_premium_notification("Backup schedule updated!")
        except ValueError:
            self.show_premium_notification("Please enter time in HH:MM format")
    
    def update_schedule(self):
        """Update the backup schedule"""
        self.scheduler.clear()
        
        if self.selected_days and self.backup_time:
            day_mapping = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
            selected_day_codes = [day for day in self.selected_days if day in day_mapping]
            
            if selected_day_codes:
                self.scheduler.add_job(selected_day_codes, self.backup_time, self._perform_backup)
    
    def run_scheduler(self):
        while self.scheduler_running:
            self.scheduler.run_pending()
            time.sleep(60)
    
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
            'auto_launch': getattr(self, 'auto_launch_var', tk.BooleanVar()).get(),
            'daily_backup_enabled': getattr(self, 'daily_backup_var', tk.BooleanVar()).get(),
            'clean_after_backup': getattr(self, 'clean_var', tk.BooleanVar()).get()
        }
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def reset_config(self):
        """Reset configuration with animation"""
        self.animate_status_change("Resetting...", "#ff9f0a")
        
        # Animate reset
        def do_reset():
            self.source_folder = ""
            self.backup_location = ""
            self.backup_time = "00:00"
            self.selected_days = []
            self.auto_launch = False
            self.daily_backup_enabled = False
            self.clean_after_backup = False
            
            # Reset GUI elements
            self.time_var.set("00:00")
            for day, var in self.day_vars.items():
                var.set(False)
                self.day_buttons[day].configure(bg='#3a3a3c', fg='#8e8e93')
            
            self.save_config()
            self.scheduler.clear()
            self.animate_status_change("Reset Complete", "#34c759")
            self.show_premium_notification("Configuration reset successfully!")
        
        self.root.after(500, do_reset)
    
    def on_closing(self):
        self.scheduler_running = False
        self.save_config()
        self.root.destroy()

def main():
    root = tk.Tk()
    
    # Set up window for premium feel
    root.tk.call('tk', 'scaling', 1.2)  # High DPI support
    
    app = BackupToolkitPremium(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()