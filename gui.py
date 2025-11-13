import os
os.environ['TK_SILENCE_DEPRECATION'] = '1'

import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from files_org import (
    load_config_from_file,
    save_config_to_file,
    organize_dir,
    validate_config,
    get_default_config,
    load_settings,
    save_settings,
    get_default_settings,
    get_latest_log_file,
    read_log_file
)

# Global variables
current_config = get_default_config()
selected_folder_index = None
selected_extension_index = None

def show_status(message, message_type="info"):
    """Show a message in the status label"""
    if message_type == "error":
        status_label.configure(foreground="red")
    elif message_type == "warning":
        status_label.configure(foreground="orange")
    else:
        status_label.configure(foreground="green")
    status_label.configure(text=message)
    # Clear the message after 3 seconds
    root.after(3000, lambda: status_label.configure(text=""))

def show_message(title, message, message_type="info"):
    """Show a message box and ensure focus returns to the main window"""
    if message_type == "info":
        messagebox.showinfo(title, message)
    elif message_type == "warning":
        messagebox.showwarning(title, message)
    elif message_type == "error":
        messagebox.showerror(title, message)
    root.focus_force()  # Force focus back to main window
    root.lift()  # Bring window to front

def browse_folder():
    folder_path = filedialog.askdirectory()
    if folder_path:
        entry_path.delete(0, tk.END)
        entry_path.insert(0, folder_path)
        root.focus_force()  # Ensure focus returns to main window

def organize():
    folder_path = entry_path.get()
    if not folder_path:
        show_status("Please select a folder to organize", "warning")
        return
    
    # Clear log text before organizing
    log_text.delete('1.0', tk.END)
    
    if organize_dir(folder_path, current_config):
        show_status("Files organized successfully!")
        # Update logs if checkbox is checked
        if show_logs_var.get():
            log_file = get_latest_log_file()
            if log_file:
                content = read_log_file(log_file)
                log_text.delete('1.0', tk.END)
                log_text.insert('1.0', content)
                log_text.see(tk.END)  # Scroll to bottom
    else:
        show_status("Failed to organize files", "error")

def close_app():
    root.destroy()

def add_folder():
    global selected_folder_index
    folder = folder_entry.get().strip()
    if folder:
        folder_listbox.insert(tk.END, folder)
        folder_entry.delete(0, tk.END)
        current_config["folders"][folder] = []
        # Select the newly added folder
        new_index = folder_listbox.size() - 1
        folder_listbox.selection_clear(0, tk.END)
        folder_listbox.selection_set(new_index)
        folder_listbox.see(new_index)
        selected_folder_index = new_index
        update_extension_listbox()
        root.focus_force()  # Ensure focus returns to main window

def remove_folder():
    global selected_folder_index
    try:
        selected = folder_listbox.curselection()[0]
        folder = folder_listbox.get(selected)
        folder_listbox.delete(selected)
        if folder in current_config["folders"]:
            del current_config["folders"][folder]
        # Select the next folder if available
        if folder_listbox.size() > 0:
            new_selection = min(selected, folder_listbox.size() - 1)
            folder_listbox.selection_set(new_selection)
            selected_folder_index = new_selection
            update_extension_listbox()
        else:
            selected_folder_index = None
            extension_listbox.delete(0, tk.END)
        root.focus_force()  # Ensure focus returns to main window
    except:
        show_status("Please select a folder to remove", "warning")

def add_extension():
    global selected_folder_index
    extension = extension_entry.get().strip()
    if extension and not extension.startswith('.'):
        extension = '.' + extension
    if extension:
        try:
            if selected_folder_index is not None:
                folder = folder_listbox.get(selected_folder_index)
                if folder not in current_config["folders"]:
                    current_config["folders"][folder] = []
                if extension not in current_config["folders"][folder]:
                    current_config["folders"][folder].append(extension)
                    extension_listbox.insert(tk.END, extension)
                extension_entry.delete(0, tk.END)
                root.focus_force()  # Ensure focus returns to main window
        except:
            show_status("Please select a folder first", "warning")

def remove_extension():
    global selected_folder_index
    try:
        if selected_folder_index is not None:
            selected_extension = extension_listbox.curselection()[0]
            folder = folder_listbox.get(selected_folder_index)
            extension = extension_listbox.get(selected_extension)
            if folder in current_config["folders"] and extension in current_config["folders"][folder]:
                current_config["folders"][folder].remove(extension)
                extension_listbox.delete(selected_extension)
                root.focus_force()  # Ensure focus returns to main window
    except:
        show_status("Please select an extension to remove", "warning")

def update_extension_listbox():
    """Update the extension listbox based on the selected folder"""
    extension_listbox.delete(0, tk.END)
    if selected_folder_index is not None:
        folder = folder_listbox.get(selected_folder_index)
        if folder in current_config["folders"]:
            for ext in current_config["folders"][folder]:
                extension_listbox.insert(tk.END, ext)

def on_folder_select(event):
    """Handle folder selection"""
    global selected_folder_index
    try:
        selected_folder_index = folder_listbox.curselection()[0]
        update_extension_listbox()
        root.focus_force()  # Ensure focus returns to main window
    except:
        pass

def on_extension_select(event):
    """Handle extension selection"""
    root.focus_force()  # Ensure focus returns to main window

def save_config():
    file_path = filedialog.asksaveasfilename(
        defaultextension=".json",
        filetypes=[("JSON files", "*.json")]
    )
    if file_path:
        try:
            save_config_to_file(file_path, current_config)
            show_status("Configuration saved successfully!")
        except Exception as e:
            show_status(str(e), "error")

def load_config():
    file_path = filedialog.askopenfilename(
        filetypes=[("JSON files", "*.json")]
    )
    if file_path:
        load_config_file(file_path)

def load_config_file(file_path, show_success=True):
    """Load configuration from a file and update the UI"""
    global current_config, selected_folder_index
    try:
        config = load_config_from_file(file_path)
        if validate_config(config):
            current_config = config
            folder_listbox.delete(0, tk.END)
            for folder in config["folders"].keys():
                folder_listbox.insert(tk.END, folder)
            # Select first folder if available
            if folder_listbox.size() > 0:
                folder_listbox.selection_set(0)
                selected_folder_index = 0
                update_extension_listbox()
            if show_success:
                show_status("Configuration loaded successfully!")
        else:
            show_status("Invalid configuration file format", "error")
    except Exception as e:
        show_status(str(e), "error")
        # Fallback to default config
        current_config = get_default_config()
        folder_listbox.delete(0, tk.END)
        for folder in current_config["folders"].keys():
            folder_listbox.insert(tk.END, folder)
        if folder_listbox.size() > 0:
            folder_listbox.selection_set(0)
            selected_folder_index = 0
            update_extension_listbox()

def reset_to_default():
    """Reset the configuration to default values"""
    global current_config, selected_folder_index
    current_config = get_default_config()
    folder_listbox.delete(0, tk.END)
    for folder in current_config["folders"].keys():
        folder_listbox.insert(tk.END, folder)
    if folder_listbox.size() > 0:
        folder_listbox.selection_set(0)
        selected_folder_index = 0
        update_extension_listbox()
    show_status("Configuration reset to default values")

def save_settings():
    """Save current settings"""
    try:
        current_config["settings"] = {
            "log_location": log_location_var.get()
        }
        save_config_to_file('config.json', current_config)
        show_status("Settings saved successfully!")
    except Exception as e:
        show_status(str(e), "error")

def load_settings_ui():
    """Load settings into UI"""
    log_location_var.set(current_config.get("settings", {}).get("log_location", "app"))

def show_logs():
    """Show the log viewer window"""
    log_window = tk.Toplevel(root)
    log_window.title("File Organization Logs")
    log_window.geometry("600x400")
    
    # Create text widget with scrollbar
    frame = ttk.Frame(log_window)
    frame.pack(expand=True, fill='both', padx=10, pady=10)
    
    scrollbar = ttk.Scrollbar(frame)
    scrollbar.pack(side='right', fill='y')
    
    log_text = tk.Text(frame, wrap='word', yscrollcommand=scrollbar.set)
    log_text.pack(expand=True, fill='both')
    scrollbar.config(command=log_text.yview)
    
    def update_logs():
        """Update the log display"""
        log_file = get_latest_log_file()
        if log_file:
            content = read_log_file(log_file)
            log_text.delete('1.0', tk.END)
            log_text.insert('1.0', content)
            log_text.see(tk.END)  # Scroll to bottom
        log_window.after(1000, update_logs)  # Update every second
    
    # Start updating logs
    update_logs()
    
    # Add close button
    ttk.Button(log_window, text="Close", command=log_window.destroy).pack(pady=5)

# Create the main window
root = tk.Tk()
root.title("File Organizer")

# Configure root window
root.configure(bg='white')
root.option_add('*TFrame.background', 'white')
root.option_add('*TLabel.background', 'white')

# Make sure the window stays on top initially
root.lift()
root.attributes('-topmost', True)
root.after_idle(root.attributes, '-topmost', False)

# Create notebook (tabbed interface)
notebook = ttk.Notebook(root)
notebook.pack(expand=True, fill='both')

# Main tab
main_tab = ttk.Frame(notebook)
notebook.add(main_tab, text='Main')

# Settings tab
settings_tab = ttk.Frame(notebook)
notebook.add(settings_tab, text='Settings')

# Main tab content
frame = ttk.Frame(main_tab)
frame.pack(padx=20, pady=20)

# Top row with path input
label_path = ttk.Label(frame, text="Folder Path:")
label_path.grid(row=0, column=0, sticky='w')

entry_path = ttk.Entry(frame, width=50)
entry_path.grid(row=0, column=1, padx=5)

button_browse = ttk.Button(frame, text="Browse", command=browse_folder)
button_browse.grid(row=0, column=2, padx=5)

# Center frame for buttons and checkbox
button_frame = ttk.Frame(frame)
button_frame.grid(row=1, column=0, columnspan=3, pady=10)

# Create a container for organize button and checkbox
organize_container = ttk.Frame(button_frame)
organize_container.pack(pady=5)

button_organize = ttk.Button(organize_container, text="Organize Files", command=organize)
button_organize.pack(side='left', padx=(0, 10))

show_logs_var = tk.BooleanVar(value=False)
show_logs_checkbox = ttk.Checkbutton(organize_container, text="Show Logs", variable=show_logs_var)
show_logs_checkbox.pack(side='left')

# Log viewer frame (initially hidden)
log_frame = ttk.LabelFrame(frame, text="File Organization Logs")
log_frame.grid(row=2, column=0, columnspan=3, sticky='nsew', pady=10)

# Create text widget with scrollbar
log_container = ttk.Frame(log_frame)
log_container.pack(expand=True, fill='both', padx=5, pady=5)

scrollbar = ttk.Scrollbar(log_container)
scrollbar.pack(side='right', fill='y')

log_text = tk.Text(log_container, wrap='word', yscrollcommand=scrollbar.set, height=10)
log_text.pack(expand=True, fill='both')
scrollbar.config(command=log_text.yview)

# Initially hide the log frame
log_frame.grid_remove()

# Function to toggle log visibility
def toggle_logs():
    if show_logs_var.get():
        log_frame.grid()
    else:
        log_frame.grid_remove()

# Bind checkbox to toggle function
show_logs_checkbox.configure(command=toggle_logs)

# Settings tab content
settings_frame = ttk.Frame(settings_tab)
settings_frame.pack(padx=20, pady=20, expand=True, fill='both')

# Create a frame for the listboxes and buttons
lists_frame = ttk.Frame(settings_frame)
lists_frame.pack(expand=True, fill='both', pady=10)

# Left side - Folders
folders_frame = ttk.Frame(lists_frame)
folders_frame.pack(side='left', expand=True, fill='both', padx=5)

ttk.Label(folders_frame, text="Folders").pack(pady=5)

# Create a container for listbox and input
folder_container = ttk.Frame(folders_frame)
folder_container.pack(expand=True, fill='both')

# Listbox takes most of the space
folder_listbox = tk.Listbox(folder_container, height=10)
folder_listbox.pack(expand=True, fill='both')
folder_listbox.bind('<<ListboxSelect>>', on_folder_select)

# Input and buttons at the bottom
folder_input_frame = ttk.Frame(folder_container)
folder_input_frame.pack(fill='x', pady=0)

# Input takes 2/3 of the space
folder_entry = ttk.Entry(folder_input_frame)
folder_entry.pack(side='left', fill='x', expand=True)

# Buttons take 1/3 of the space
folder_buttons_container = ttk.Frame(folder_input_frame)
folder_buttons_container.pack(side='left', padx=0)

# Style for buttons to match entry height
style = ttk.Style()
style.configure('Custom.TButton', padding=0)
style.layout('Custom.TButton', [
    ('Button.padding', {'children': [
        ('Button.label', {'sticky': 'nswe'})
    ], 'sticky': 'nswe'})
])

ttk.Button(folder_buttons_container, text="+", command=add_folder, width=3, style='Custom.TButton').pack(side='left', padx=0)
ttk.Button(folder_buttons_container, text="-", command=remove_folder, width=3, style='Custom.TButton').pack(side='left', padx=0)

# Middle - Configuration buttons
config_frame = ttk.Frame(lists_frame)
config_frame.pack(side='left', padx=20)

# Create a frame for each button to ensure same width
save_frame = ttk.Frame(config_frame)
save_frame.pack(fill='x', pady=5)
save_button = ttk.Button(save_frame, text="Save Config", command=save_config)
save_button.pack(fill='x')

load_frame = ttk.Frame(config_frame)
load_frame.pack(fill='x', pady=5)
load_button = ttk.Button(load_frame, text="Load Config", command=load_config)
load_button.pack(fill='x')

reset_frame = ttk.Frame(config_frame)
reset_frame.pack(fill='x', pady=5)
reset_button = ttk.Button(reset_frame, text="Reset to Default", command=reset_to_default)
reset_button.pack(fill='x')

# Right side - Extensions
extensions_frame = ttk.Frame(lists_frame)
extensions_frame.pack(side='left', expand=True, fill='both', padx=5)

ttk.Label(extensions_frame, text="Extensions").pack(pady=5)

# Create a container for listbox and input
extension_container = ttk.Frame(extensions_frame)
extension_container.pack(expand=True, fill='both')

# Listbox takes most of the space
extension_listbox = tk.Listbox(extension_container, height=10)
extension_listbox.pack(expand=True, fill='both')
extension_listbox.bind('<<ListboxSelect>>', on_extension_select)

# Input and buttons at the bottom
extension_input_frame = ttk.Frame(extension_container)
extension_input_frame.pack(fill='x', pady=0)

# Input takes 2/3 of the space
extension_entry = ttk.Entry(extension_input_frame)
extension_entry.pack(side='left', fill='x', expand=True)

# Buttons take 1/3 of the space
extension_buttons_container = ttk.Frame(extension_input_frame)
extension_buttons_container.pack(side='left', padx=0)

ttk.Button(extension_buttons_container, text="+", command=add_extension, width=3, style='Custom.TButton').pack(side='left', padx=0)
ttk.Button(extension_buttons_container, text="-", command=remove_extension, width=3, style='Custom.TButton').pack(side='left', padx=0)

# Add status label at the bottom
status_label = ttk.Label(root, text="", anchor='e', background='white')
status_label.place(relx=1.0, rely=1.0, x=-20, y=-5, anchor='se')

# Add settings section at the bottom of settings tab
settings_section = ttk.LabelFrame(settings_frame, text="Settings")
settings_section.pack(fill='x', pady=10)

# Log location setting
log_location_frame = ttk.Frame(settings_section)
log_location_frame.pack(fill='x', padx=5, pady=5)

ttk.Label(log_location_frame, text="Log File Location:").pack(side='left', padx=5)
log_location_var = tk.StringVar(value="app")
ttk.Radiobutton(log_location_frame, text="Next to Application", variable=log_location_var, value="app").pack(side='left', padx=5)
ttk.Radiobutton(log_location_frame, text="In Target Folder", variable=log_location_var, value="target").pack(side='left', padx=5)

# Save settings button
ttk.Button(settings_section, text="Save Settings", command=save_settings).pack(pady=5)

# Try to load config.json on startup, fallback to default if not found
if os.path.exists('config.json'):
    load_config_file('config.json', show_success=False)
else:
    # Initialize with default config
    folder_listbox.delete(0, tk.END)
    for folder in current_config["folders"].keys():
        folder_listbox.insert(tk.END, folder)
    if folder_listbox.size() > 0:
        folder_listbox.selection_set(0)
        selected_folder_index = 0
        update_extension_listbox()

# Load settings when starting
load_settings_ui()

root.mainloop()
