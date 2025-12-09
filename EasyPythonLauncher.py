import os
import sys
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
from pathlib import Path
import threading
import json
import string
import shutil


class PythonScriptRunner:
    def __init__(self, root):
        self.root = root
        self.root.title("Easy Python Launcher")
        self.root.geometry("1000x600")
        self.root.resizable(0, 0)
        
        # Configuration file
        # Get the directory where the executable/script is located
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            app_dir = os.path.dirname(sys.executable)
        else:
            # Running as script
            app_dir = os.path.dirname(os.path.abspath(__file__))
        
        self.config_file = os.path.join(app_dir, 'EasyPythonLauncher.config.json')
        
        # Variables
        self.selected_file = None
        self.running_processes = {}  # Dictionary: {script_path: process_object}
        self.dark_mode = self.load_theme_preference()
        
        # Menu bar
        menubar = tk.Menu(root)
        root.config(menu=menubar)
        
        # Display Menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Display", menu=view_menu)
        self.theme_var = tk.BooleanVar(value=self.dark_mode)
        view_menu.add_checkbutton(label="Dark Mode", variable=self.theme_var, 
                                   command=self.toggle_theme)
        
        # Settings Menu
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Settings", menu=settings_menu)
        settings_menu.add_command(label="Select Python Interpreter...", command=self.select_python_interpreter)
        
        # Main display grid configuration
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Main Frame
        main_frame = ttk.Frame(root, padding="5")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        
        # PanedWindow for left/right split
        paned = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Left Frame - Folder tree
        left_frame = ttk.Frame(paned, padding="5")
        paned.add(left_frame, weight=1)
        
        ttk.Label(left_frame, text="Folders:", font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        
        # Treeview
        self.tree_folders = ttk.Treeview(left_frame, selectmode='browse')
        tree_scroll_y = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.tree_folders.yview)
        tree_scroll_x = ttk.Scrollbar(left_frame, orient=tk.HORIZONTAL, command=self.tree_folders.xview)
        self.tree_folders.configure(yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set)
        
        self.tree_folders.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.tree_folders.bind('<<TreeviewSelect>>', self.on_folder_select)
        
        # Right Frame - List of .py files and console
        right_frame = ttk.Frame(paned, padding="5")
        paned.add(right_frame, weight=2)
        
        # py files Frame
        files_frame = ttk.Frame(right_frame)
        files_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(files_frame, text="Python Script Files (.py):", font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        
        # Listbox for .py files
        list_frame = ttk.Frame(files_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        list_scroll = ttk.Scrollbar(list_frame, orient=tk.VERTICAL)
        self.files_listbox = tk.Listbox(list_frame, yscrollcommand=list_scroll.set, 
                                        font=('Courier', 10), selectmode=tk.SINGLE)
        list_scroll.config(command=self.files_listbox.yview)
        
        self.files_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        list_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.files_listbox.bind('<<ListboxSelect>>', self.on_file_select)
        self.files_listbox.bind('<Double-Button-1>', lambda e: self.run_script())
        
        # Frame for buttons and information
        control_frame = ttk.Frame(right_frame)
        control_frame.pack(fill=tk.X, pady=10)
        
        # Label for selected file
        self.selected_label = ttk.Label(control_frame, text="No file selected", 
                                       foreground='gray', font=('Arial', 9))
        self.selected_label.pack(side=tk.LEFT, padx=5)
        
        # Button Run
        self.run_button = ttk.Button(control_frame, text="▶ Run", command=self.run_script, 
                                     state=tk.DISABLED, width=12)
        self.run_button.pack(side=tk.RIGHT, padx=5)
        
        # Button Stop
        self.stop_button = ttk.Button(control_frame, text="⬛ Stop", command=self.stop_script, 
                                      state=tk.DISABLED, width=12)
        self.stop_button.pack(side=tk.RIGHT, padx=5)
        
        # Output console
        console_frame = ttk.LabelFrame(right_frame, text="Console", padding="5")
        console_frame.pack(fill=tk.BOTH, expand=False, pady=(10, 0))
        
        self.console = scrolledtext.ScrolledText(console_frame, height=5, 
                                                 font=('Courier', 9), wrap=tk.WORD)
        self.console.pack(fill=tk.BOTH, expand=False)
        
        # Apply initial theme
        self.apply_theme()
        
        # Initialize folder tree and drives
        self.populate_tree()
    
    def get_python_executable(self):
        """Get the correct Python executable path, even when frozen with PyInstaller"""
        # First, check if we have a saved Python path in config
        saved_python = self.load_python_path()
        if saved_python and os.path.exists(saved_python):
            return saved_python
        
        # Check if running as a PyInstaller bundle
        if getattr(sys, 'frozen', False):
            # Running as compiled executable - find Python in PATH
            # Try pythonw first (no console window), fallback to python
            python_exec = shutil.which('pythonw')
            if not python_exec:
                python_exec = shutil.which('python')
            if not python_exec:
                # Try python3 on Linux/Mac
                python_exec = shutil.which('python3')
            if not python_exec:
                # Try common Windows locations (pythonw.exe preferred)
                common_paths = [
                    r'C:\Python313\pythonw.exe',
                    r'C:\Python312\pythonw.exe',
                    r'C:\Python311\pythonw.exe',
                    r'C:\Python310\pythonw.exe',
                    r'C:\Python39\pythonw.exe',
                    r'C:\Program Files\Python313\pythonw.exe',
                    r'C:\Program Files\Python312\pythonw.exe',
                    r'C:\Program Files\Python311\pythonw.exe',
                    r'C:\Program Files\Python310\pythonw.exe',
                    r'C:\Program Files\Python39\pythonw.exe',
                    os.path.expandvars(r'%LOCALAPPDATA%\Programs\Python\Python313\pythonw.exe'),
                    os.path.expandvars(r'%LOCALAPPDATA%\Programs\Python\Python312\pythonw.exe'),
                    os.path.expandvars(r'%LOCALAPPDATA%\Programs\Python\Python311\pythonw.exe'),
                    os.path.expandvars(r'%LOCALAPPDATA%\Programs\Python\Python310\pythonw.exe'),
                    os.path.expandvars(r'%LOCALAPPDATA%\Programs\Python\Python39\pythonw.exe'),
                    # Fallback to python.exe if pythonw.exe not found
                    r'C:\Python313\python.exe',
                    r'C:\Python312\python.exe',
                    r'C:\Python311\python.exe',
                    r'C:\Python310\python.exe',
                    r'C:\Python39\python.exe',
                    r'C:\Program Files\Python313\python.exe',
                    r'C:\Program Files\Python312\python.exe',
                    r'C:\Program Files\Python311\python.exe',
                    r'C:\Program Files\Python310\python.exe',
                    r'C:\Program Files\Python39\python.exe',
                    os.path.expandvars(r'%LOCALAPPDATA%\Programs\Python\Python313\python.exe'),
                    os.path.expandvars(r'%LOCALAPPDATA%\Programs\Python\Python312\python.exe'),
                    os.path.expandvars(r'%LOCALAPPDATA%\Programs\Python\Python311\python.exe'),
                    os.path.expandvars(r'%LOCALAPPDATA%\Programs\Python\Python310\python.exe'),
                    os.path.expandvars(r'%LOCALAPPDATA%\Programs\Python\Python39\python.exe'),
                ]
                for path in common_paths:
                    if os.path.exists(path):
                        python_exec = path
                        break
            
            if not python_exec:
                # Python not found - ask user to select it
                python_exec = self.ask_for_python_path()
                if not python_exec:
                    raise FileNotFoundError(
                        "Python interpreter not found!\n\n"
                        "Please install Python or select its location via Settings > Select Python Interpreter."
                    )
            
            # Save the found Python path for future use
            self.save_python_path(python_exec)
            return python_exec
        else:
            # Running as a normal Python script
            python_exec = sys.executable
            self.save_python_path(python_exec)
            return python_exec
    
    def ask_for_python_path(self):
        """Ask user to manually select the Python executable"""
        result = messagebox.askyesno(
            "Python Not Found",
            "Python interpreter was not found automatically.\n\n"
            "Would you like to select the location of python.exe or pythonw.exe manually?\n\n"
            "Note: pythonw.exe is recommended (no console window)."
        )
        
        if result:
            if sys.platform == 'win32':
                filetypes = [("Python Executable", "python*.exe"), 
                           ("Python (no console)", "pythonw.exe"),
                           ("Python (with console)", "python.exe"),
                           ("All Files", "*.*")]
            else:
                filetypes = [("Python Executable", "python*"), ("All Files", "*.*")]
            
            filename = filedialog.askopenfilename(
                title="Select Python Interpreter",
                filetypes=filetypes
            )
            
            if filename and os.path.exists(filename):
                # Verify it's actually a Python executable
                try:
                    result = subprocess.run([filename, "--version"], 
                                          capture_output=True, 
                                          text=True, 
                                          timeout=5)
                    if "Python" in result.stdout or "Python" in result.stderr:
                        return filename
                    else:
                        messagebox.showerror("Invalid File", 
                                           "The selected file doesn't appear to be a valid Python interpreter.")
                except Exception:
                    messagebox.showerror("Invalid File", 
                                       "The selected file doesn't appear to be a valid Python interpreter.")
        
        return None
    
    def select_python_interpreter(self):
        """Menu option to manually select Python interpreter"""
        if sys.platform == 'win32':
            filetypes = [("Python Executable", "python*.exe"), 
                       ("Python (no console)", "pythonw.exe"),
                       ("Python (with console)", "python.exe"),
                       ("All Files", "*.*")]
        else:
            filetypes = [("Python Executable", "python*"), ("All Files", "*.*")]
        
        filename = filedialog.askopenfilename(
            title="Select Python Interpreter (pythonw.exe recommended)",
            filetypes=filetypes
        )
        
        if filename and os.path.exists(filename):
            # Verify it's actually a Python executable
            try:
                result = subprocess.run([filename, "--version"], 
                                      capture_output=True, 
                                      text=True, 
                                      timeout=5)
                if "Python" in result.stdout or "Python" in result.stderr:
                    self.save_python_path(filename)
                    version_info = result.stdout.strip() or result.stderr.strip()
                    exe_type = "pythonw.exe (no console)" if "pythonw" in filename.lower() else "python.exe (with console)"
                    messagebox.showinfo("Success", 
                                      f"Python interpreter set successfully!\n\n{version_info}\nType: {exe_type}\n\nLocation: {filename}")
                else:
                    messagebox.showerror("Invalid File", 
                                       "The selected file doesn't appear to be a valid Python interpreter.")
            except Exception as e:
                messagebox.showerror("Error", 
                                   f"Could not verify Python executable:\n{str(e)}")
    
    def save_python_path(self, python_path):
        """Save the Python executable path to config"""
        try:
            config = {}
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
            
            config['python_path'] = python_path
            
            with open(self.config_file, 'w') as f:
                json.dump(config, f)
        except Exception as e:
            print(f"Error while saving Python path: {e}")
    
    def load_python_path(self):
        """Load the saved Python executable path from config"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    return config.get('python_path', None)
        except Exception:
            pass
        return None
        
    def populate_tree(self):
        """Generate tree content with folders and all drives"""
        if sys.platform == 'win32':
            # Windows : show all drives (C:, D:, etc.)
            drives = self.get_available_drives()
            for drive in drives:
                root_node = self.tree_folders.insert('', 'end', text=drive, 
                                                    values=[drive], open=False)
                # Add dummy for expansion
                self.tree_folders.insert(root_node, 'end')
        else:
            # Linux/Mac : start from root
            root_path = '/'
            root_node = self.tree_folders.insert('', 'end', text=root_path, 
                                                values=[root_path], open=True)
            self.load_subdirectories(root_node, root_path)
        
        # Restore last opened folder
        last_folder = self.load_last_folder()
        if last_folder and os.path.exists(last_folder):
            self.expand_to_folder(last_folder)
    
    def get_available_drives(self):
        """Returns the list of all available drives for Windows"""
        if sys.platform != 'win32':
            return ['/']
        
        drives = []
        for letter in string.ascii_uppercase:
            drive = f"{letter}:\\"
            if os.path.exists(drive):
                drives.append(drive)
        return drives
    
    def expand_to_folder(self, folder_path):
        """Expand the tree and select a specific folder"""
        # Normalize path
        folder_path = os.path.normpath(folder_path)
        
        # Find the root node that contains this path
        for root_item in self.tree_folders.get_children():
            root_path = self.tree_folders.item(root_item)['values'][0]
            root_path = os.path.normpath(root_path)
            
            # Check if folder_path is under this root
            if folder_path.startswith(root_path):
                # Expand this root
                self._expand_node(root_item, root_path)
                
                # Build the path segments
                relative_path = folder_path[len(root_path):].strip(os.sep)
                if relative_path:
                    path_parts = relative_path.split(os.sep)
                    current_item = root_item
                    current_path = root_path
                    
                    # Navigate through each part of the path
                    for part in path_parts:
                        current_path = os.path.join(current_path, part)
                        found = False
                        
                        # Search for this part in the children
                        for child in self.tree_folders.get_children(current_item):
                            child_path = self.tree_folders.item(child)['values'][0]
                            if os.path.normpath(child_path) == os.path.normpath(current_path):
                                self._expand_node(child, child_path)
                                current_item = child
                                found = True
                                break
                        
                        if not found:
                            break
                    
                    # Select and show the final folder
                    if os.path.normpath(self.tree_folders.item(current_item)['values'][0]) == folder_path:
                        self.tree_folders.selection_set(current_item)
                        self.tree_folders.see(current_item)
                        self.display_python_files(folder_path)
                break
    
    def _expand_node(self, item, path):
        """Expand a tree node and load its subdirectories"""
        children = self.tree_folders.get_children(item)
        # Check if node has a dummy child (not yet expanded)
        if len(children) == 1 and not self.tree_folders.item(children[0])['values']:
            self.tree_folders.delete(children[0])
            self.load_subdirectories(item, path)
        self.tree_folders.item(item, open=True)
        
    def load_subdirectories(self, parent, path):
        """Load all subdirectories of a folder"""
        try:
            items = []
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                if os.path.isdir(item_path) and not item.startswith('.'):
                    items.append((item, item_path))
            
            # Sort by name
            items.sort(key=lambda x: x[0].lower())
            
            for item_name, item_path in items:
                node = self.tree_folders.insert(parent, 'end', text=item_name, 
                                               values=[item_path])
                # Add dummy for expansion
                self.tree_folders.insert(node, 'end')
                
        except PermissionError:
            pass
    
    def on_folder_select(self, event):
        """Called when a folder is selected"""
        selection = self.tree_folders.selection()
        if not selection:
            return
        
        item = selection[0]
        
        # Load subdirectories if needed
        children = self.tree_folders.get_children(item)
        if len(children) == 1 and not self.tree_folders.item(children[0])['values']:
            self.tree_folders.delete(children[0])
            folder_path = self.tree_folders.item(item)['values'][0]
            self.load_subdirectories(item, folder_path)
        
        # List all .py files in the selected folder
        folder_path = self.tree_folders.item(item)['values'][0]
        self.display_python_files(folder_path)
        self.save_last_folder(folder_path)
    
    def display_python_files(self, folder_path):
        """Display all .py files in the selected folder"""
        self.files_listbox.delete(0, tk.END)
        self.selected_file = None
        self.run_button.config(state=tk.DISABLED)
        self.selected_label.config(text="No file selected", foreground='gray')
        
        try:
            py_files = [f for f in os.listdir(folder_path) 
                       if f.endswith('.py') and os.path.isfile(os.path.join(folder_path, f))]
            py_files.sort(key=lambda x: x.lower())
            
            for py_file in py_files:
                self.files_listbox.insert(tk.END, py_file)
                
            if not py_files:
                self.files_listbox.insert(tk.END, "(No .py file in this folder)")
                self.files_listbox.config(foreground='gray')
            else:
                self.files_listbox.config(foreground='black')
                
        except PermissionError:
            self.files_listbox.insert(tk.END, "(Access denied)")
            self.files_listbox.config(foreground='red')
    
    def on_file_select(self, event):
        """Called when a .py file is selected"""
        selection = self.files_listbox.curselection()
        if not selection:
            return
        
        filename = self.files_listbox.get(selection[0])
        if filename.startswith('('):  # information
            return
        
        # Get full path
        folder_selection = self.tree_folders.selection()
        if folder_selection:
            folder_path = self.tree_folders.item(folder_selection[0])['values'][0]
            self.selected_file = os.path.join(folder_path, filename)
            self.run_button.config(state=tk.NORMAL)
            
            # Update Stop button state based on whether this script is running
            if self.selected_file in self.running_processes:
                self.stop_button.config(state=tk.NORMAL)
                self.selected_label.config(text=f"Selected: {filename} (Running ▶)", foreground='green')
            else:
                self.stop_button.config(state=tk.DISABLED)
                self.selected_label.config(text=f"Selected: {filename}", foreground='yellow')
    
    def run_script(self):
        """Execute the selected script"""
        if not self.selected_file:
            return
        
        # Check if script is already running
        if self.selected_file in self.running_processes:
            messagebox.showwarning("Already Running", 
                                  f"This script is already running!\n{os.path.basename(self.selected_file)}")
            return
        
        self.console.delete(1.0, tk.END)
        self.console.insert(tk.END, f"=== Executing {os.path.basename(self.selected_file)} ===\n\n")
        
        # Enable the Stop button (Run button stays enabled for other scripts)
        self.stop_button.config(state=tk.NORMAL)
        
        # Update label to show running status
        filename = os.path.basename(self.selected_file)
        self.selected_label.config(text=f"Selected: {filename} (Running ▶)", foreground='green')
        
        # Launch the script in a new thread
        script_path = self.selected_file
        thread = threading.Thread(target=self._execute_script, args=(script_path,), daemon=True)
        thread.start()
    
    def _execute_script(self, script_path):
        """Execute script (called in a new thread)"""
        try:
            # Get script path
            script_dir = os.path.dirname(script_path)
            
            # Get the correct Python executable
            python_exec = self.get_python_executable()
            
            # Start the process
            process = subprocess.Popen(
                [python_exec, script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                cwd=script_dir,
                universal_newlines=True
            )
            
            # Store the process in the dictionary
            self.running_processes[script_path] = process
            
            # Read the output line by line
            for line in process.stdout:
                self.console.insert(tk.END, line)
                self.console.see(tk.END)
                self.root.update_idletasks()
            
            # Wait for the end of the process
            return_code = process.wait()
            
            self.console.insert(tk.END, f"\n=== Terminated (code: {return_code}) ===\n")
            self.console.see(tk.END)
            
        except Exception as e:
            self.console.insert(tk.END, f"\n❌ Error: {str(e)}\n")
            self.console.see(tk.END)
        finally:
            # Remove process from running processes
            if script_path in self.running_processes:
                del self.running_processes[script_path]
            
            # Update UI if this is the currently selected script
            if self.selected_file == script_path:
                self.root.after(0, lambda: self.stop_button.config(state=tk.DISABLED))
                filename = os.path.basename(script_path)
                self.root.after(0, lambda: self.selected_label.config(
                    text=f"Selected: {filename}", foreground='yellow'))
    
    def stop_script(self):
        """Stop the currently selected running script"""
        if not self.selected_file:
            return
        
        if self.selected_file in self.running_processes:
            try:
                process = self.running_processes[self.selected_file]
                process.terminate()
                self.console.insert(tk.END, f"\n⚠ Script interrupted by user: {os.path.basename(self.selected_file)}\n")
                self.console.see(tk.END)
                
                # Update UI
                self.stop_button.config(state=tk.DISABLED)
                filename = os.path.basename(self.selected_file)
                self.selected_label.config(text=f"Selected: {filename}", foreground='yellow')
            except Exception as e:
                self.console.insert(tk.END, f"\n❌ Error while stopping: {str(e)}\n")
                self.console.see(tk.END)
        else:
            messagebox.showinfo("Not Running", 
                               f"This script is not currently running.\n{os.path.basename(self.selected_file)}")
    
    def load_theme_preference(self):
        """Load the theme preference from configurtation file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    return config.get('dark_mode', False)
        except Exception:
            pass
        return False
    
    def save_theme_preference(self):
        """Save the theme preference in configurtation file"""
        try:
            config = {}
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
            
            config['dark_mode'] = self.dark_mode
            
            with open(self.config_file, 'w') as f:
                json.dump(config, f)
        except Exception as e:
            print(f"Error while saving preferences: {e}")
    
    def toggle_theme(self):
        """Toggle between light and dark theme"""
        self.dark_mode = self.theme_var.get()
        self.apply_theme()
        self.save_theme_preference()
    
    def save_last_folder(self, folder_path):
        """Save the last opened folder path"""
        try:
            config = {}
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
            
            config['last_folder'] = folder_path
            
            with open(self.config_file, 'w') as f:
                json.dump(config, f)
        except Exception as e:
            print(f"Error while saving last folder: {e}")
    
    def load_last_folder(self):
        """Load the last opened folder path"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    return config.get('last_folder', None)
        except Exception:
            pass
        return None
    
    def apply_theme(self):
        """Apply theme to interface"""
        if self.dark_mode:
            # Dark Mode
            bg_color = '#2b2b2b'
            fg_color = '#ffffff'
            console_bg = '#1e1e1e'
            console_fg = '#00ff00'
            listbox_bg = '#3c3c3c'
            listbox_fg = '#ffffff'
            select_bg = '#404040'
            tree_bg = '#3c3c3c'
            tree_fg = '#ffffff'
            field_bg = '#2b2b2b'
            
            # ttk style configuration for dark mode
            style = ttk.Style()
            style.theme_use('clam')
            
            # Style for Treeview
            style.configure("Treeview",
                          background=tree_bg,
                          foreground=tree_fg,
                          fieldbackground=tree_bg,
                          borderwidth=0)
            style.map('Treeview',
                     background=[('selected', select_bg)],
                     foreground=[('selected', '#ffffff')])
            
            # Style for frames and labels
            style.configure("TFrame", background=bg_color)
            style.configure("TLabel", background=bg_color, foreground=fg_color)
            style.configure("TLabelframe", background=bg_color, foreground=fg_color)
            style.configure("TLabelframe.Label", background=bg_color, foreground=fg_color)
            
            # Style for buttons
            style.configure("TButton", background='#404040', foreground=fg_color)
            style.map('TButton',
                     background=[('active', '#505050')],
                     foreground=[('active', '#ffffff')])
            
            # Style for PanedWindow
            style.configure("TPanedwindow", background=bg_color)
            style.configure("Sash", sashthickness=5, background='#404040')
            
            # Scrollbars
            style.configure("Vertical.TScrollbar", background='#404040', 
                          troughcolor=tree_bg, borderwidth=0, arrowcolor=fg_color)
            style.configure("Horizontal.TScrollbar", background='#404040',
                          troughcolor=tree_bg, borderwidth=0, arrowcolor=fg_color)
            
            self.root.configure(bg=bg_color)
            self.console.configure(bg=console_bg, fg=console_fg, 
                                  insertbackground=console_fg)
            self.files_listbox.configure(bg=listbox_bg, fg=listbox_fg, 
                                        selectbackground=select_bg,
                                        selectforeground='#ffffff')
        else:
            # Light Mode
            bg_color = '#f0f0f0'
            fg_color = '#000000'
            console_bg = '#ffffff'
            console_fg = '#000000'
            listbox_bg = '#ffffff'
            listbox_fg = '#000000'
            select_bg = '#0078d7'
            tree_bg = '#ffffff'
            tree_fg = '#000000'
            
            # ttk style configuration for light mode
            style = ttk.Style()
            style.theme_use('clam')
            
            # Style for Treeview
            style.configure("Treeview",
                          background=tree_bg,
                          foreground=tree_fg,
                          fieldbackground=tree_bg,
                          borderwidth=1)
            style.map('Treeview',
                     background=[('selected', select_bg)],
                     foreground=[('selected', '#ffffff')])
            
            # Style for frames and labels
            style.configure("TFrame", background=bg_color)
            style.configure("TLabel", background=bg_color, foreground=fg_color)
            style.configure("TLabelframe", background=bg_color, foreground=fg_color)
            style.configure("TLabelframe.Label", background=bg_color, foreground=fg_color)
            
            # Style for boutons
            style.configure("TButton", background='#e1e1e1', foreground=fg_color)
            style.map('TButton',
                     background=[('active', '#d0d0d0')],
                     foreground=[('active', '#000000')])
            
            # Style for PanedWindow
            style.configure("TPanedwindow", background=bg_color)
            style.configure("Sash", sashthickness=5, background='#d0d0d0')
            
            # Scrollbars
            style.configure("Vertical.TScrollbar", background='#e1e1e1',
                          troughcolor=tree_bg, borderwidth=1, arrowcolor=fg_color)
            style.configure("Horizontal.TScrollbar", background='#e1e1e1',
                          troughcolor=tree_bg, borderwidth=1, arrowcolor=fg_color)
            
            self.root.configure(bg=bg_color)
            self.console.configure(bg=console_bg, fg=console_fg,
                                  insertbackground=console_fg)
            self.files_listbox.configure(bg=listbox_bg, fg=listbox_fg,
                                        selectbackground=select_bg,
                                        selectforeground='#ffffff')


def main():
    root = tk.Tk()
    app = PythonScriptRunner(root)
    root.mainloop()


if __name__ == "__main__":
    main()