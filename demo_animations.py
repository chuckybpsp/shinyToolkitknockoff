#!/usr/bin/env python3
"""
Premium Animation Demo
Demonstrates the smooth animations and transitions in the Premium Backup Toolkit
"""

import tkinter as tk
from datetime import datetime
import time
import threading

class AnimationDemo:
    def __init__(self, root):
        self.root = root
        self.root.title("Premium Animation Demo")
        self.root.geometry("500x600")
        self.root.configure(bg='#1a1a1a')
        
        self.setup_demo()
    
    def setup_demo(self):
        # Title
        title = tk.Label(
            self.root,
            text="Premium Animation Demo",
            font=("SF Pro Display", 24, "bold"),
            fg='#ffffff',
            bg='#1a1a1a'
        )
        title.pack(pady=30)
        
        # Animated button demo
        self.create_animated_button_demo()
        
        # Progress ring demo
        self.create_progress_ring_demo()
        
        # Status indicator demo
        self.create_status_demo()
        
        # Notification demo
        self.create_notification_demo()
    
    def create_animated_button_demo(self):
        frame = tk.Frame(self.root, bg='#2c2c2e')
        frame.pack(fill='x', padx=20, pady=10)
        
        label = tk.Label(
            frame,
            text="Animated Buttons",
            font=("SF Pro Text", 16, "bold"),
            fg='#ffffff',
            bg='#2c2c2e'
        )
        label.pack(pady=10)
        
        # Create animated buttons with different colors
        colors = [
            ('#007AFF', 'Primary'),
            ('#34c759', 'Success'),
            ('#ff3b30', 'Danger'),
            ('#5856d6', 'Purple'),
            ('#af52de', 'Violet')
        ]
        
        for color, name in colors:
            btn = self.create_hover_button(frame, name, color)
            btn.pack(pady=5, padx=20, fill='x')
    
    def create_hover_button(self, parent, text, color):
        """Create a button with hover animation"""
        original_bg = color
        hover_bg = self.lighten_color(color, 1.3)
        
        btn = tk.Button(
            parent,
            text=text,
            bg=original_bg,
            fg='white',
            font=("SF Pro Text", 14, "bold"),
            relief='flat',
            borderwidth=0,
            command=lambda: self.button_clicked(text)
        )
        
        def on_enter(event):
            self.animate_color(btn, original_bg, hover_bg)
        
        def on_leave(event):
            self.animate_color(btn, hover_bg, original_bg)
        
        btn.bind('<Enter>', on_enter)
        btn.bind('<Leave>', on_leave)
        
        return btn
    
    def lighten_color(self, color, factor):
        """Lighten a hex color"""
        if color.startswith('#'):
            color = color[1:]
        rgb = [int(color[i:i+2], 16) for i in (0, 2, 4)]
        rgb = [min(255, int(c * factor)) for c in rgb]
        return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
    
    def animate_color(self, widget, start_color, end_color, duration=200, steps=20):
        """Smooth color transition animation"""
        start_rgb = [int(start_color[i:i+2], 16) for i in (1, 3, 5)]
        end_rgb = [int(end_color[i:i+2], 16) for i in (1, 3, 5)]
        
        step_delay = duration // steps
        color_steps = [(end_rgb[i] - start_rgb[i]) / steps for i in range(3)]
        
        def animate_step(step):
            if step >= steps:
                widget.configure(bg=end_color)
                return
            
            current_rgb = [
                int(start_rgb[i] + color_steps[i] * step) 
                for i in range(3)
            ]
            current_color = f"#{current_rgb[0]:02x}{current_rgb[1]:02x}{current_rgb[2]:02x}"
            
            try:
                widget.configure(bg=current_color)
                self.root.after(step_delay, lambda: animate_step(step + 1))
            except:
                pass
        
        animate_step(0)
    
    def create_progress_ring_demo(self):
        frame = tk.Frame(self.root, bg='#2c2c2e')
        frame.pack(fill='x', padx=20, pady=10)
        
        label = tk.Label(
            frame,
            text="Animated Progress Ring",
            font=("SF Pro Text", 16, "bold"),
            fg='#ffffff',
            bg='#2c2c2e'
        )
        label.pack(pady=10)
        
        # Canvas for progress ring
        canvas = tk.Canvas(
            frame,
            width=100,
            height=100,
            bg='#2c2c2e',
            highlightthickness=0
        )
        canvas.pack(pady=10)
        
        # Create progress ring
        self.progress_ring = self.create_progress_ring(canvas, 50, 50, 40)
        
        # Button to start animation
        progress_btn = tk.Button(
            frame,
            text="Start Progress Animation",
            bg='#007AFF',
            fg='white',
            font=("SF Pro Text", 12),
            relief='flat',
            borderwidth=0,
            command=self.animate_progress
        )
        progress_btn.pack(pady=10)
    
    def create_progress_ring(self, canvas, x, y, radius, width=6):
        """Create an animated progress ring"""
        # Background arc
        bg_arc = canvas.create_arc(
            x - radius, y - radius, x + radius, y + radius,
            start=0, extent=360, outline='#333333', width=width,
            style='arc'
        )
        
        # Progress arc
        progress_arc = canvas.create_arc(
            x - radius, y - radius, x + radius, y + radius,
            start=90, extent=0, outline='#007AFF', width=width,
            style='arc'
        )
        
        return {'canvas': canvas, 'arc': progress_arc, 'progress': 0}
    
    def animate_progress(self):
        """Animate the progress ring"""
        def update_progress(target_progress, current_step=0, total_steps=60):
            if current_step >= total_steps:
                return
            
            # Easing function (ease-out)
            t = current_step / total_steps
            eased_t = 1 - (1 - t) ** 3
            current_progress = target_progress * eased_t
            
            extent = -360 * (current_progress / 100)
            self.progress_ring['canvas'].itemconfig(
                self.progress_ring['arc'], 
                extent=extent
            )
            
            self.root.after(
                16,  # ~60 FPS
                lambda: update_progress(target_progress, current_step + 1, total_steps)
            )
        
        # Animate to 75%
        update_progress(75)
    
    def create_status_demo(self):
        frame = tk.Frame(self.root, bg='#2c2c2e')
        frame.pack(fill='x', padx=20, pady=10)
        
        label = tk.Label(
            frame,
            text="Status Animations",
            font=("SF Pro Text", 16, "bold"),
            fg='#ffffff',
            bg='#2c2c2e'
        )
        label.pack(pady=10)
        
        # Status indicator
        self.status_indicator = tk.Label(
            frame,
            text="●",
            font=("Arial", 20),
            fg='#34c759',
            bg='#2c2c2e'
        )
        self.status_indicator.pack(pady=10)
        
        # Buttons to change status
        status_frame = tk.Frame(frame, bg='#2c2c2e')
        status_frame.pack(pady=10)
        
        statuses = [
            ('Ready', '#34c759'),
            ('Working', '#ff9f0a'),
            ('Error', '#ff3b30'),
            ('Success', '#007AFF')
        ]
        
        for status, color in statuses:
            btn = tk.Button(
                status_frame,
                text=status,
                bg=color,
                fg='white',
                font=("SF Pro Text", 10),
                relief='flat',
                borderwidth=0,
                command=lambda c=color: self.animate_status(c)
            )
            btn.pack(side='left', padx=5)
    
    def animate_status(self, color):
        """Animate status indicator with pulse effect"""
        self.status_indicator.configure(fg=color)
        
        def pulse(scale=1.0, direction=1, steps=20):
            if steps <= 0:
                self.status_indicator.configure(font=("Arial", 20))
                return
            
            if scale <= 0.8:
                direction = 1
            elif scale >= 1.4:
                direction = -1
            
            font_size = int(20 * scale)
            self.status_indicator.configure(font=("Arial", font_size))
            
            if direction == 1:
                scale += 0.03
            else:
                scale -= 0.03
            
            self.root.after(30, lambda: pulse(scale, direction, steps - 1))
        
        pulse()
    
    def create_notification_demo(self):
        frame = tk.Frame(self.root, bg='#2c2c2e')
        frame.pack(fill='x', padx=20, pady=10)
        
        label = tk.Label(
            frame,
            text="Premium Notifications",
            font=("SF Pro Text", 16, "bold"),
            fg='#ffffff',
            bg='#2c2c2e'
        )
        label.pack(pady=10)
        
        btn = tk.Button(
            frame,
            text="Show Notification",
            bg='#5856d6',
            fg='white',
            font=("SF Pro Text", 12),
            relief='flat',
            borderwidth=0,
            command=self.show_notification
        )
        btn.pack(pady=10)
    
    def show_notification(self):
        """Show a premium-style notification"""
        notification = tk.Toplevel(self.root)
        notification.title("")
        notification.geometry("320x100")
        notification.configure(bg='#2c2c2e')
        notification.resizable(False, False)
        
        # Position at top-right
        x = self.root.winfo_x() + self.root.winfo_width() - 340
        y = self.root.winfo_y() + 50
        notification.geometry(f"+{x}+{y}")
        
        # Remove window decorations
        notification.overrideredirect(True)
        
        # Add content
        content_frame = tk.Frame(notification, bg='#2c2c2e')
        content_frame.pack(fill='both', expand=True, padx=15, pady=15)
        
        title_label = tk.Label(
            content_frame,
            text="Animation Demo",
            font=("SF Pro Text", 14, "bold"),
            fg='#ffffff',
            bg='#2c2c2e'
        )
        title_label.pack(anchor='w')
        
        msg_label = tk.Label(
            content_frame,
            text=f"Notification shown at {datetime.now().strftime('%H:%M:%S')}",
            font=("SF Pro Text", 12),
            fg='#8e8e93',
            bg='#2c2c2e'
        )
        msg_label.pack(anchor='w')
        
        # Slide in animation
        def slide_in(step=0, total_steps=20):
            if step >= total_steps:
                # Auto-dismiss after delay
                self.root.after(3000, notification.destroy)
                return
            
            # Easing function
            t = step / total_steps
            eased_t = t * t * (3 - 2 * t)  # smoothstep
            
            target_x = self.root.winfo_x() + self.root.winfo_width() - 340
            start_x = target_x + 350
            current_x = int(start_x + (target_x - start_x) * eased_t)
            
            notification.geometry(f"+{current_x}+{y}")
            
            self.root.after(16, lambda: slide_in(step + 1, total_steps))
        
        slide_in()
    
    def button_clicked(self, button_name):
        print(f"Button clicked: {button_name}")

def main():
    print("Premium Animation Demo")
    print("======================")
    print("This demo showcases the smooth animations available in the Premium Backup Toolkit:")
    print("• Hover over buttons to see color transitions")
    print("• Click 'Start Progress Animation' to see the animated ring")
    print("• Click status buttons to see pulsing animations")
    print("• Click 'Show Notification' to see slide-in notifications")
    print()
    
    root = tk.Tk()
    try:
        app = AnimationDemo(root)
        root.mainloop()
    except Exception as e:
        print(f"Demo requires GUI support. Error: {e}")
        print("Run this on a system with tkinter GUI support to see the animations.")

if __name__ == "__main__":
    main()