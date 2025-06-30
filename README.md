# Backup Toolkit

A desktop application for scheduled folder backups, inspired by the FOCUS Toolkit. This application allows you to:

- Select a source folder to backup
- Choose a backup destination
- Schedule backups on specific days of the week and times
- Perform manual backups
- Optionally clean the source folder after backup
- Enable daily backups
- Save all settings automatically

## Features

- **Dark Theme UI**: Modern dark interface similar to the original FOCUS Toolkit
- **Scheduled Backups**: Set specific days of the week and times for automatic backups
- **Manual Backups**: Instant backup with the "Backup Now" button
- **Folder Selection**: Easy folder selection with dialog boxes
- **Configuration Persistence**: All settings are saved and restored between sessions
- **Background Operation**: Scheduler runs in background thread
- **Safety Features**: Validation checks before performing backups

## Requirements

- Python 3.6 or higher
- tkinter (usually included with Python)
- schedule library (automatically installed)

## Installation & Usage

### Method 1: Using the Launcher (Recommended)

1. Run the launcher script which will automatically install dependencies:
   ```bash
   python3 run_backup_toolkit.py
   ```

### Method 2: Manual Installation

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the application:
   ```bash
   python3 backup_toolkit.py
   ```

## How to Use

1. **Choose Data Source Folder**: Click this button to select the folder you want to backup
2. **Choose Backup Location**: Select where you want the backups to be saved
3. **Set Backup Time**: Enter the time in HH:MM format (24-hour format, e.g., "14:30" for 2:30 PM)
4. **Select Days**: Check the days of the week when you want backups to occur
5. **Click Save**: Save your schedule settings
6. **Optional Settings**:
   - Enable Daily Backup: Backup every day at the specified time
   - Clean Data Source after Backup: Remove files from source after successful backup
   - Auto-launch at login: (Feature placeholder for future implementation)

## Backup Behavior

- Backups are created with timestamps: `[source_folder_name]_backup_[YYYYMMDD_HHMMSS]`
- Original folder structure is preserved
- If "Clean Data Source after Backup" is enabled, the source folder will be emptied after successful backup
- All operations run in background threads to prevent UI freezing

## Configuration

Settings are automatically saved to `backup_config.json` in the application directory. This includes:
- Source and backup folder paths
- Backup schedule settings
- All checkbox options

## Troubleshooting

- Ensure both source and backup folders exist and are accessible
- Check that you have write permissions to the backup location
- Backup time should be in HH:MM format (e.g., "09:00", "14:30")
- The application needs to remain running for scheduled backups to work

## File Structure

```
backup_toolkit.py          # Main application
run_backup_toolkit.py      # Launcher with dependency management  
requirements.txt           # Python dependencies
backup_config.json         # Configuration file (created automatically)
README.md                  # This file
```

## Safety Notes

- Always test with non-critical data first
- The "Clean Data Source after Backup" option will DELETE files from the source folder
- Backups are copies, not moves - original files remain unless cleaning is enabled
- No overwrite protection - multiple backups will create separate timestamped folders

## License

This project is open source and available under the MIT License.