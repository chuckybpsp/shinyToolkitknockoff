#!/usr/bin/env python3
"""
Backup Toolkit CLI - Command Line Interface version
A scheduled backup application without GUI dependencies
"""

import os
import shutil
import json
import threading
import time
from datetime import datetime
import argparse

# Simple scheduler replacement for when the schedule library isn't available
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

class BackupToolkitCLI:
    def __init__(self):
        self.config_file = "backup_config.json"
        
        # Default values
        self.source_folder = ""
        self.backup_location = ""
        self.backup_time = "00:00"
        self.selected_days = []
        self.daily_backup_enabled = False
        self.clean_after_backup = False
        
        # Load existing configuration
        self.load_config()
        
        # Simple scheduler
        self.scheduler = SimpleScheduler()
        self.scheduler_running = False
        self.scheduler_thread = None
        
    def set_source_folder(self, folder):
        """Set the source folder to backup"""
        if os.path.exists(folder):
            self.source_folder = folder
            self.save_config()
            print(f"Source folder set to: {folder}")
            return True
        else:
            print(f"Error: Folder '{folder}' does not exist")
            return False
    
    def set_backup_location(self, folder):
        """Set the backup destination folder"""
        if os.path.exists(folder):
            self.backup_location = folder
            self.save_config()
            print(f"Backup location set to: {folder}")
            return True
        else:
            print(f"Error: Folder '{folder}' does not exist")
            return False
    
    def set_schedule(self, time_str, days):
        """Set backup schedule"""
        try:
            # Validate time format
            datetime.strptime(time_str, '%H:%M')
            self.backup_time = time_str
            self.selected_days = [day.lower() for day in days]
            self.save_config()
            self.update_schedule()
            print(f"Schedule set: {time_str} on {', '.join(days)}")
            return True
        except ValueError:
            print("Error: Time must be in HH:MM format (e.g., '14:30')")
            return False
    
    def backup_now(self):
        """Perform an immediate backup"""
        if not self.source_folder or not self.backup_location:
            print("Error: Please set both source folder and backup location first!")
            return False
        
        if not os.path.exists(self.source_folder):
            print("Error: Source folder does not exist!")
            return False
        
        if not os.path.exists(self.backup_location):
            print("Error: Backup location does not exist!")
            return False
        
        return self._perform_backup()
    
    def _perform_backup(self):
        """Internal backup function"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            source_name = os.path.basename(self.source_folder)
            backup_folder_name = f"{source_name}_backup_{timestamp}"
            backup_path = os.path.join(self.backup_location, backup_folder_name)
            
            print(f"Starting backup from {self.source_folder} to {backup_path}")
            
            # Perform the backup
            shutil.copytree(self.source_folder, backup_path)
            
            # Clean source if option is enabled
            if self.clean_after_backup:
                print("Cleaning source folder...")
                for item in os.listdir(self.source_folder):
                    item_path = os.path.join(self.source_folder, item)
                    if os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                    else:
                        os.remove(item_path)
                print("Source folder cleaned")
            
            print(f"Backup completed successfully!\nSaved to: {backup_path}")
            return True
            
        except Exception as e:
            print(f"Backup failed: {str(e)}")
            return False
    
    def update_schedule(self):
        """Update the backup schedule"""
        self.scheduler.clear()
        
        if self.selected_days and self.backup_time:
            self.scheduler.add_job(self.selected_days, self.backup_time, self._perform_backup)
            print(f"Scheduler updated: {self.backup_time} on {', '.join(self.selected_days)}")
    
    def start_scheduler(self):
        """Start the backup scheduler"""
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            print("Scheduler is already running")
            return
        
        self.scheduler_running = True
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()
        print("Backup scheduler started")
    
    def stop_scheduler(self):
        """Stop the backup scheduler"""
        self.scheduler_running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=1)
        print("Backup scheduler stopped")
    
    def _run_scheduler(self):
        """Run the scheduler loop"""
        while self.scheduler_running:
            self.scheduler.run_pending()
            time.sleep(60)  # Check every minute
    
    def load_config(self):
        """Load configuration from file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.source_folder = config.get('source_folder', '')
                    self.backup_location = config.get('backup_location', '')
                    self.backup_time = config.get('backup_time', '00:00')
                    self.selected_days = config.get('selected_days', [])
                    self.daily_backup_enabled = config.get('daily_backup_enabled', False)
                    self.clean_after_backup = config.get('clean_after_backup', False)
                print("Configuration loaded")
        except Exception as e:
            print(f"Error loading config: {e}")
    
    def save_config(self):
        """Save configuration to file"""
        config = {
            'source_folder': self.source_folder,
            'backup_location': self.backup_location,
            'backup_time': self.backup_time,
            'selected_days': self.selected_days,
            'daily_backup_enabled': self.daily_backup_enabled,
            'clean_after_backup': self.clean_after_backup
        }
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            print("Configuration saved")
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def show_status(self):
        """Display current configuration"""
        print("\n=== Backup Toolkit Status ===")
        print(f"Source folder: {self.source_folder or 'Not set'}")
        print(f"Backup location: {self.backup_location or 'Not set'}")
        print(f"Backup time: {self.backup_time}")
        print(f"Scheduled days: {', '.join(self.selected_days) if self.selected_days else 'None'}")
        print(f"Daily backup: {'Enabled' if self.daily_backup_enabled else 'Disabled'}")
        print(f"Clean after backup: {'Enabled' if self.clean_after_backup else 'Disabled'}")
        print(f"Scheduler: {'Running' if self.scheduler_running else 'Stopped'}")
        print("=" * 30)

def main():
    parser = argparse.ArgumentParser(description='Backup Toolkit CLI')
    parser.add_argument('--source', help='Set source folder to backup')
    parser.add_argument('--destination', help='Set backup destination folder')
    parser.add_argument('--time', help='Set backup time (HH:MM format)')
    parser.add_argument('--days', nargs='+', help='Set backup days (mon tue wed thu fri sat sun)')
    parser.add_argument('--backup-now', action='store_true', help='Perform backup immediately')
    parser.add_argument('--start-scheduler', action='store_true', help='Start the backup scheduler')
    parser.add_argument('--status', action='store_true', help='Show current configuration')
    parser.add_argument('--clean', action='store_true', help='Enable cleaning source after backup')
    parser.add_argument('--no-clean', action='store_true', help='Disable cleaning source after backup')
    
    args = parser.parse_args()
    
    # Create backup toolkit instance
    toolkit = BackupToolkitCLI()
    
    # Handle command line arguments
    if args.source:
        toolkit.set_source_folder(args.source)
    
    if args.destination:
        toolkit.set_backup_location(args.destination)
    
    if args.time and args.days:
        toolkit.set_schedule(args.time, args.days)
    
    if args.clean:
        toolkit.clean_after_backup = True
        toolkit.save_config()
        print("Source cleaning enabled")
    
    if args.no_clean:
        toolkit.clean_after_backup = False
        toolkit.save_config()
        print("Source cleaning disabled")
    
    if args.backup_now:
        toolkit.backup_now()
    
    if args.start_scheduler:
        toolkit.start_scheduler()
        try:
            print("Scheduler running. Press Ctrl+C to stop.")
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopping scheduler...")
            toolkit.stop_scheduler()
    
    if args.status or not any(vars(args).values()):
        toolkit.show_status()
        
        if not any(vars(args).values()):
            print("\nUsage examples:")
            print("  python3 backup_cli.py --source /path/to/source --destination /path/to/backup")
            print("  python3 backup_cli.py --time 14:30 --days mon wed fri")
            print("  python3 backup_cli.py --backup-now")
            print("  python3 backup_cli.py --start-scheduler")
            print("  python3 backup_cli.py --status")

if __name__ == "__main__":
    main()