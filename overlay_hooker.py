import ctypes
import ctypes.wintypes
import win32api
import win32con
import win32gui
import win32process
import psutil
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import queue
import time
import json
import os
from datetime import datetime
import google.generativeai as genai
import asyncio
import aiohttp


class OverlayWindow:
    """Transparent overlay window for displaying text"""

    def __init__(self, parent_callback=None):
        self.root = tk.Toplevel()
        self.root.title("Text Overlay")
        self.parent_callback = parent_callback
        self.setup_overlay()

    def setup_overlay(self):
        # Window configuration for overlay
        self.root.overrideredirect(True)  # Remove window decorations
        self.root.attributes('-alpha', 0.9)  # Semi-transparent
        self.root.attributes('-topmost', True)  # Always on top
        self.root.configure(bg='black')

        # Default position (top-right corner)
        screen_width = self.root.winfo_screenwidth()
        self.root.geometry(f"400x200+{screen_width-420}+20")

        # Create main frame
        main_frame = tk.Frame(self.root, bg='#1a1a1a', highlightbackground='#444', highlightthickness=2)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        # Title bar for dragging
        title_bar = tk.Frame(main_frame, bg='#2a2a2a', height=25)
        title_bar.pack(fill=tk.X)
        title_bar.pack_propagate(False)

        # Title label
        title_label = tk.Label(title_bar, text="📝 Text Capture", bg='#2a2a2a', fg='white', font=("Arial", 9))
        title_label.pack(side=tk.LEFT, padx=5)

        # Control buttons
        button_frame = tk.Frame(title_bar, bg='#2a2a2a')
        button_frame.pack(side=tk.RIGHT)

        # Minimize button
        tk.Button(button_frame, text="─", command=self.minimize, bg='#3a3a3a', fg='white',
                 bd=0, padx=8, pady=1, font=("Arial", 8)).pack(side=tk.LEFT, padx=1)

        # Settings button
        tk.Button(button_frame, text="⚙", command=self.open_settings, bg='#3a3a3a', fg='white',
                 bd=0, padx=8, pady=1, font=("Arial", 10)).pack(side=tk.LEFT, padx=1)

        # Close button
        tk.Button(button_frame, text="✕", command=self.hide, bg='#3a3a3a', fg='white',
                 bd=0, padx=8, pady=1, font=("Arial", 8)).pack(side=tk.LEFT, padx=1)

        # Text display area - Original text
        text_frame = tk.Frame(main_frame, bg='#1a1a1a')
        text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Original text label
        tk.Label(text_frame, text="Original:", bg='#1a1a1a', fg='#888', font=("Arial", 8)).pack(anchor=tk.W)

        self.text_display = tk.Text(text_frame, wrap=tk.WORD, height=3,
                                   bg='#2a2a2a', fg='white',
                                   font=("Yu Gothic UI", 11),
                                   insertbackground='white',
                                   bd=1, relief=tk.FLAT)
        self.text_display.pack(fill=tk.BOTH, expand=True, pady=(2, 5))

        # Translation label
        tk.Label(text_frame, text="Translation:", bg='#1a1a1a', fg='#888', font=("Arial", 8)).pack(anchor=tk.W)

        # Translation display
        self.translation_display = tk.Text(text_frame, wrap=tk.WORD, height=3,
                                          bg='#2a2a2a', fg='#4fc3f7',
                                          font=("Arial", 10),
                                          insertbackground='white',
                                          bd=1, relief=tk.FLAT)
        self.translation_display.pack(fill=tk.BOTH, expand=True, pady=(2, 0))

        # Action buttons
        action_frame = tk.Frame(main_frame, bg='#1a1a1a')
        action_frame.pack(fill=tk.X, padx=5, pady=5)

        tk.Button(action_frame, text="Translate", command=self.translate_text,
                 bg='#4CAF50', fg='white', bd=0, padx=15, pady=3).pack(side=tk.LEFT, padx=2)

        tk.Button(action_frame, text="Copy", command=self.copy_text,
                 bg='#2196F3', fg='white', bd=0, padx=15, pady=3).pack(side=tk.LEFT, padx=2)

        tk.Button(action_frame, text="Clear", command=self.clear_text,
                 bg='#666', fg='white', bd=0, padx=15, pady=3).pack(side=tk.LEFT, padx=2)

        # Opacity slider
        self.opacity = tk.DoubleVar(value=0.9)
        opacity_scale = tk.Scale(action_frame, from_=0.3, to=1.0, resolution=0.1,
                                 orient=tk.HORIZONTAL, variable=self.opacity,
                                 command=self.change_opacity, bg='#1a1a1a', fg='white',
                                 highlightthickness=0, troughcolor='#3a3a3a',
                                 width=10, length=80)
        opacity_scale.pack(side=tk.RIGHT, padx=5)

        tk.Label(action_frame, text="Opacity:", bg='#1a1a1a', fg='#888',
                font=("Arial", 8)).pack(side=tk.RIGHT)

        # Make window draggable
        self.make_draggable(title_bar)

        # Window state
        self.minimized = False
        self.original_geometry = None

    def make_draggable(self, widget):
        """Make the window draggable"""
        def start_drag(event):
            self.x = event.x
            self.y = event.y

        def drag(event):
            deltax = event.x - self.x
            deltay = event.y - self.y
            x = self.root.winfo_x() + deltax
            y = self.root.winfo_y() + deltay
            self.root.geometry(f"+{x}+{y}")

        widget.bind("<Button-1>", start_drag)
        widget.bind("<B1-Motion>", drag)

    def update_text(self, text):
        """Update displayed text"""
        self.text_display.delete(1.0, tk.END)
        self.text_display.insert(1.0, text)

        # Auto-translate if enabled
        if hasattr(self, 'auto_translate') and self.auto_translate.get():
            self.translate_text()

    def translate_text(self):
        """Translate text using Gemini API"""
        text = self.text_display.get(1.0, tk.END).strip()
        if not text:
            return

        if self.parent_callback:
            translation = self.parent_callback('translate', text)
            if translation:
                self.translation_display.delete(1.0, tk.END)
                self.translation_display.insert(1.0, translation)

    def copy_text(self):
        """Copy both original and translation to clipboard"""
        original = self.text_display.get(1.0, tk.END).strip()
        translation = self.translation_display.get(1.0, tk.END).strip()

        if original or translation:
            clipboard_text = f"Original: {original}\nTranslation: {translation}"
            self.root.clipboard_clear()
            self.root.clipboard_append(clipboard_text)

    def clear_text(self):
        """Clear all text"""
        self.text_display.delete(1.0, tk.END)
        self.translation_display.delete(1.0, tk.END)

    def change_opacity(self, value):
        """Change window opacity"""
        self.root.attributes('-alpha', float(value))

    def minimize(self):
        """Minimize/restore window"""
        if not self.minimized:
            self.original_geometry = self.root.geometry()
            # Get current position
            x = self.root.winfo_x()
            y = self.root.winfo_y()
            self.root.geometry(f"400x30+{x}+{y}")
            self.minimized = True
        else:
            if self.original_geometry:
                self.root.geometry(self.original_geometry)
            self.minimized = False

    def open_settings(self):
        """Open settings dialog"""
        if self.parent_callback:
            self.parent_callback('settings', None)

    def hide(self):
        """Hide overlay"""
        self.root.withdraw()

    def show(self):
        """Show overlay"""
        self.root.deiconify()

    def destroy(self):
        """Destroy overlay window"""
        self.root.destroy()


class GeminiTranslator:
    """Gemini API translator"""

    def __init__(self, api_key=None):
        self.api_key = api_key
        self.model = None
        self.initialized = False

    def initialize(self, api_key):
        """Initialize Gemini API"""
        try:
            self.api_key = api_key
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-pro')
            self.initialized = True
            return True
        except Exception as e:
            print(f"Failed to initialize Gemini: {e}")
            return False

    def translate(self, text, target_language="English"):
        """Translate text using Gemini"""
        if not self.initialized or not self.model:
            return None

        try:
            prompt = f"""Translate the following Japanese text to {target_language}.
            Provide only the translation without any additional explanation or notes.
            If the text contains character names or dialogue, preserve the format.

            Text: {text}"""

            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"Translation error: {e}")
            return f"Translation error: {str(e)}"


class OverlayTextHooker:
    """Main application with overlay support"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Japanese Text Hooker with Overlay")
        self.root.geometry("1000x650")

        # Components
        self.hooker = TextHookerCore()
        self.translator = GeminiTranslator()
        self.overlay = None
        self.monitor_thread = None
        self.selected_window = None

        # Settings
        self.load_settings()

        # Setup UI
        self.setup_ui()

        # Create overlay
        self.create_overlay()

    def load_settings(self):
        """Load settings from file"""
        self.settings_file = "settings.json"
        self.settings = {
            'gemini_api_key': '',
            'auto_translate': False,
            'overlay_enabled': True,
            'target_language': 'English',
            'overlay_position': None
        }

        # Create default settings file if it doesn't exist
        if not os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'w') as f:
                    json.dump(self.settings, f, indent=2)
            except:
                pass
        else:
            try:
                with open(self.settings_file, 'r') as f:
                    saved = json.load(f)
                    self.settings.update(saved)

                # Initialize translator if API key exists
                if self.settings['gemini_api_key']:
                    self.translator.initialize(self.settings['gemini_api_key'])
            except:
                pass

    def save_settings(self):
        """Save settings to file"""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except:
            pass

    def setup_ui(self):
        # Create notebook
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Main tab
        main_tab = ttk.Frame(notebook)
        notebook.add(main_tab, text="Capture")
        self.setup_main_tab(main_tab)

        # Settings tab
        settings_tab = ttk.Frame(notebook)
        notebook.add(settings_tab, text="Settings")
        self.setup_settings_tab(settings_tab)

        # Status bar
        self.status_label = ttk.Label(self.root, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(fill=tk.X, side=tk.BOTTOM)

    def setup_main_tab(self, parent):
        # Window selection
        select_frame = ttk.LabelFrame(parent, text="Window Selection", padding="10")
        select_frame.pack(fill=tk.X, padx=5, pady=5)

        # Window combo
        ttk.Label(select_frame, text="Select Window:").pack(side=tk.LEFT, padx=(0, 5))
        self.window_combo = ttk.Combobox(select_frame, width=50, state="readonly")
        self.window_combo.pack(side=tk.LEFT, padx=(0, 10))

        # Control buttons
        ttk.Button(select_frame, text="Refresh", command=self.refresh_windows).pack(side=tk.LEFT, padx=2)
        ttk.Button(select_frame, text="Start", command=self.start_capture).pack(side=tk.LEFT, padx=2)
        ttk.Button(select_frame, text="Stop", command=self.stop_capture).pack(side=tk.LEFT, padx=2)

        # Overlay toggle
        self.overlay_enabled = tk.BooleanVar(value=self.settings['overlay_enabled'])
        ttk.Checkbutton(select_frame, text="Show Overlay",
                       variable=self.overlay_enabled,
                       command=self.toggle_overlay).pack(side=tk.LEFT, padx=10)

        # Text display
        text_frame = ttk.LabelFrame(parent, text="Captured Text", padding="10")
        text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Split pane for original and translation
        paned = ttk.PanedWindow(text_frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)

        # Original text
        orig_frame = ttk.Frame(paned)
        paned.add(orig_frame, weight=1)

        ttk.Label(orig_frame, text="Original:").pack(anchor=tk.W)
        self.text_display = scrolledtext.ScrolledText(
            orig_frame, wrap=tk.WORD, width=40, height=20,
            font=("Yu Gothic UI", 11)
        )
        self.text_display.pack(fill=tk.BOTH, expand=True)

        # Translation
        trans_frame = ttk.Frame(paned)
        paned.add(trans_frame, weight=1)

        ttk.Label(trans_frame, text="Translation:").pack(anchor=tk.W)
        self.translation_display = scrolledtext.ScrolledText(
            trans_frame, wrap=tk.WORD, width=40, height=20,
            font=("Arial", 10)
        )
        self.translation_display.pack(fill=tk.BOTH, expand=True)

        # Action buttons
        action_frame = ttk.Frame(text_frame)
        action_frame.pack(fill=tk.X, pady=(5, 0))

        ttk.Button(action_frame, text="Translate Selected",
                  command=self.translate_selected).pack(side=tk.LEFT, padx=2)
        ttk.Button(action_frame, text="Copy All",
                  command=self.copy_all).pack(side=tk.LEFT, padx=2)
        ttk.Button(action_frame, text="Clear",
                  command=self.clear_all).pack(side=tk.LEFT, padx=2)
        ttk.Button(action_frame, text="Save",
                  command=self.save_to_file).pack(side=tk.LEFT, padx=2)

        # Auto-translate checkbox
        self.auto_translate = tk.BooleanVar(value=self.settings['auto_translate'])
        ttk.Checkbutton(action_frame, text="Auto-translate",
                       variable=self.auto_translate).pack(side=tk.RIGHT, padx=5)

        # Initial refresh
        self.refresh_windows()

    def setup_settings_tab(self, parent):
        # API Settings
        api_frame = ttk.LabelFrame(parent, text="Gemini API Settings", padding="10")
        api_frame.pack(fill=tk.X, padx=5, pady=5)

        # API Key
        ttk.Label(api_frame, text="API Key:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.api_key_var = tk.StringVar(value=self.settings['gemini_api_key'])
        api_entry = ttk.Entry(api_frame, textvariable=self.api_key_var, width=50, show="*")
        api_entry.grid(row=0, column=1, padx=5, pady=5)

        # Show/Hide API key button
        def toggle_api_visibility():
            if api_entry['show'] == '*':
                api_entry['show'] = ''
                show_btn['text'] = 'Hide'
            else:
                api_entry['show'] = '*'
                show_btn['text'] = 'Show'

        show_btn = ttk.Button(api_frame, text="Show", command=toggle_api_visibility, width=8)
        show_btn.grid(row=0, column=2, padx=5)

        # Test API button
        ttk.Button(api_frame, text="Test API", command=self.test_api, width=10).grid(row=0, column=3, padx=5)

        # Target language
        ttk.Label(api_frame, text="Target Language:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.target_lang_var = tk.StringVar(value=self.settings['target_language'])
        lang_combo = ttk.Combobox(api_frame, textvariable=self.target_lang_var, width=20, state="readonly")
        lang_combo['values'] = ('English', 'Korean', 'Chinese', 'Spanish', 'French', 'German', 'Russian')
        lang_combo.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)

        # Translation Settings
        trans_frame = ttk.LabelFrame(parent, text="Translation Settings", padding="10")
        trans_frame.pack(fill=tk.X, padx=5, pady=5)

        # Translation options
        ttk.Checkbutton(trans_frame, text="Enable auto-translation",
                       variable=self.auto_translate).pack(anchor=tk.W, pady=2)

        self.preserve_format = tk.BooleanVar(value=True)
        ttk.Checkbutton(trans_frame, text="Preserve text format (keep line breaks, spacing)",
                       variable=self.preserve_format).pack(anchor=tk.W, pady=2)

        self.translate_names = tk.BooleanVar(value=False)
        ttk.Checkbutton(trans_frame, text="Translate character names",
                       variable=self.translate_names).pack(anchor=tk.W, pady=2)

        # Overlay Settings
        overlay_frame = ttk.LabelFrame(parent, text="Overlay Settings", padding="10")
        overlay_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Checkbutton(overlay_frame, text="Enable overlay window",
                       variable=self.overlay_enabled).pack(anchor=tk.W, pady=2)

        # Save button
        save_frame = ttk.Frame(parent)
        save_frame.pack(fill=tk.X, padx=5, pady=20)

        ttk.Button(save_frame, text="Save Settings", command=self.save_all_settings,
                  style="Accent.TButton").pack(side=tk.LEFT, padx=5)

        ttk.Button(save_frame, text="Reset to Default", command=self.reset_settings).pack(side=tk.LEFT, padx=5)

        # API info
        info_frame = ttk.LabelFrame(parent, text="Information", padding="10")
        info_frame.pack(fill=tk.X, padx=5, pady=5)

        info_text = """• Get your Gemini API key from: https://makersuite.google.com/app/apikey
• The API key is stored locally and never shared
• Free tier includes 60 queries per minute
• Overlay window can be dragged and resized
• Press Alt+T to quickly translate selected text"""

        info_label = ttk.Label(info_frame, text=info_text, justify=tk.LEFT)
        info_label.pack(anchor=tk.W)

    def create_overlay(self):
        """Create overlay window"""
        self.overlay = OverlayWindow(parent_callback=self.overlay_callback)
        if not self.settings['overlay_enabled']:
            self.overlay.hide()

    def overlay_callback(self, action, data):
        """Handle overlay callbacks"""
        if action == 'translate':
            if self.translator.initialized:
                return self.translator.translate(data, self.target_lang_var.get())
            else:
                messagebox.showwarning("API Not Configured",
                                      "Please configure Gemini API key in Settings")
                return None
        elif action == 'settings':
            # Switch to settings tab
            for tab in self.root.winfo_children():
                if isinstance(tab, ttk.Notebook):
                    tab.select(1)  # Select settings tab
                    break

    def toggle_overlay(self):
        """Toggle overlay visibility"""
        if self.overlay:
            if self.overlay_enabled.get():
                self.overlay.show()
            else:
                self.overlay.hide()
        self.settings['overlay_enabled'] = self.overlay_enabled.get()

    def refresh_windows(self):
        """Refresh window list"""
        windows = self.hooker.find_game_windows()
        window_list = [f"{w['title'][:50]} (PID: {w['pid']})" for w in windows]
        self.window_combo['values'] = window_list

        if window_list:
            self.window_combo.current(0)

        self.windows_data = windows
        self.update_status(f"Found {len(windows)} windows")

    def start_capture(self):
        """Start capturing text"""
        if not self.window_combo.get():
            messagebox.showwarning("No Selection", "Please select a window first")
            return

        index = self.window_combo.current()
        self.selected_window = self.windows_data[index]

        # Hook process
        if self.hooker.hook_process(self.selected_window['pid']):
            self.update_status(f"Hooked to: {self.selected_window['title']}")

        # Start monitoring
        self.monitor_thread = threading.Thread(
            target=self.monitor_loop,
            daemon=True
        )
        self.monitor_thread.start()

        self.update_status(f"Capturing from: {self.selected_window['title']}")

    def monitor_loop(self):
        """Monitor loop for capturing text"""
        while self.hooker.running:
            if self.selected_window:
                texts = self.hooker.capture_text(self.selected_window['hwnd'])
                for source, text in texts:
                    if self.hooker._is_japanese(text):
                        self.add_captured_text(text)
            time.sleep(0.1)

    def add_captured_text(self, text):
        """Add captured text to displays"""
        # Add to main display
        self.root.after(0, lambda: self._add_text_to_display(text))

        # Update overlay
        if self.overlay and self.overlay_enabled.get():
            self.root.after(0, lambda: self.overlay.update_text(text))

    def _add_text_to_display(self, text):
        """Add text to main display"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.text_display.insert(tk.END, f"[{timestamp}] {text}\n")
        self.text_display.see(tk.END)

        # Auto-translate if enabled
        if self.auto_translate.get() and self.translator.initialized:
            translation = self.translator.translate(text, self.target_lang_var.get())
            if translation:
                self.translation_display.insert(tk.END, f"[{timestamp}] {translation}\n")
                self.translation_display.see(tk.END)

    def translate_selected(self):
        """Translate selected text"""
        try:
            selected = self.text_display.get(tk.SEL_FIRST, tk.SEL_LAST)
        except:
            selected = self.text_display.get(1.0, tk.END)

        if selected.strip() and self.translator.initialized:
            translation = self.translator.translate(selected, self.target_lang_var.get())
            if translation:
                self.translation_display.insert(tk.END, f"\n{translation}\n")
                self.translation_display.see(tk.END)

    def stop_capture(self):
        """Stop capturing"""
        self.hooker.stop_monitoring()
        if self.selected_window:
            self.hooker.unhook_process(self.selected_window['pid'])
        self.update_status("Capture stopped")

    def test_api(self):
        """Test Gemini API"""
        api_key = self.api_key_var.get()
        if not api_key:
            messagebox.showwarning("No API Key", "Please enter an API key")
            return

        if self.translator.initialize(api_key):
            test_result = self.translator.translate("こんにちは", "English")
            if test_result and "error" not in test_result.lower():
                messagebox.showinfo("Success", f"API test successful!\nTest translation: こんにちは → {test_result}")
            else:
                messagebox.showerror("Failed", "API test failed. Please check your API key.")
        else:
            messagebox.showerror("Failed", "Failed to initialize API. Please check your API key.")

    def save_all_settings(self):
        """Save all settings"""
        self.settings['gemini_api_key'] = self.api_key_var.get()
        self.settings['auto_translate'] = self.auto_translate.get()
        self.settings['overlay_enabled'] = self.overlay_enabled.get()
        self.settings['target_language'] = self.target_lang_var.get()

        # Initialize translator with new API key
        if self.settings['gemini_api_key']:
            self.translator.initialize(self.settings['gemini_api_key'])

        self.save_settings()
        messagebox.showinfo("Saved", "Settings saved successfully")

    def reset_settings(self):
        """Reset to default settings"""
        if messagebox.askyesno("Reset", "Reset all settings to default?"):
            self.settings = {
                'gemini_api_key': '',
                'auto_translate': False,
                'overlay_enabled': True,
                'target_language': 'English',
                'overlay_position': None
            }
            self.api_key_var.set('')
            self.auto_translate.set(False)
            self.overlay_enabled.set(True)
            self.target_lang_var.set('English')
            self.save_settings()

    def copy_all(self):
        """Copy all text"""
        original = self.text_display.get(1.0, tk.END)
        translation = self.translation_display.get(1.0, tk.END)

        combined = f"=== Original ===\n{original}\n\n=== Translation ===\n{translation}"
        self.root.clipboard_clear()
        self.root.clipboard_append(combined)
        self.update_status("Copied to clipboard")

    def clear_all(self):
        """Clear all text"""
        self.text_display.delete(1.0, tk.END)
        self.translation_display.delete(1.0, tk.END)
        if self.overlay:
            self.overlay.clear_text()

    def save_to_file(self):
        """Save to file"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialfile=f"capture_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        )

        if filename:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("=== Original ===\n")
                f.write(self.text_display.get(1.0, tk.END))
                f.write("\n\n=== Translation ===\n")
                f.write(self.translation_display.get(1.0, tk.END))
            self.update_status(f"Saved to {filename}")

    def update_status(self, message):
        """Update status bar"""
        self.status_label.config(text=message)

    def run(self):
        """Run the application"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

    def on_closing(self):
        """Handle window closing"""
        if self.overlay:
            self.overlay.destroy()
        self.root.destroy()


class TextHookerCore:
    """Core text hooking functionality"""

    def __init__(self):
        self.hooked_processes = {}
        self.running = False

    def find_game_windows(self):
        """Find all visible windows"""
        windows = []

        def enum_callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if title:
                    try:
                        _, pid = win32process.GetWindowThreadProcessId(hwnd)
                        process = psutil.Process(pid)
                        windows.append({
                            'hwnd': hwnd,
                            'title': title,
                            'pid': pid,
                            'process_name': process.name()
                        })
                    except:
                        pass
            return True

        win32gui.EnumWindows(enum_callback, windows)
        return windows

    def hook_process(self, pid):
        """Hook a process"""
        if pid in self.hooked_processes:
            return False

        try:
            handle = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, False, pid)
            self.hooked_processes[pid] = {
                'handle': handle,
                'last_texts': set()
            }
            self.running = True
            return True
        except Exception as e:
            print(f"Hook failed: {e}")
            return False

    def unhook_process(self, pid):
        """Unhook a process"""
        if pid in self.hooked_processes:
            try:
                win32api.CloseHandle(self.hooked_processes[pid]['handle'])
                del self.hooked_processes[pid]
            except:
                pass

    def capture_text(self, hwnd):
        """Capture text from window"""
        texts = []

        # Get window text
        try:
            text = win32gui.GetWindowText(hwnd)
            if text:
                texts.append(('Window', text))
        except:
            pass

        # Get text using WM_GETTEXT
        try:
            length = win32gui.SendMessage(hwnd, win32con.WM_GETTEXTLENGTH, 0, 0)
            if length > 0:
                buffer = ctypes.create_unicode_buffer(length + 1)
                win32gui.SendMessage(hwnd, win32con.WM_GETTEXT, length + 1, buffer)
                if buffer.value:
                    texts.append(('WM_GETTEXT', buffer.value))
        except:
            pass

        # Enumerate child windows
        def enum_child(child_hwnd, texts):
            try:
                child_text = win32gui.GetWindowText(child_hwnd)
                if child_text and self._is_japanese(child_text):
                    texts.append(('Child', child_text))
            except:
                pass
            return True

        try:
            win32gui.EnumChildWindows(hwnd, enum_child, texts)
        except:
            pass

        return texts

    def _is_japanese(self, text):
        """Check if text contains Japanese"""
        if not text:
            return False

        for char in text:
            code = ord(char)
            if (0x3040 <= code <= 0x309F) or \
               (0x30A0 <= code <= 0x30FF) or \
               (0x4E00 <= code <= 0x9FAF):
                return True
        return False

    def stop_monitoring(self):
        """Stop monitoring"""
        self.running = False


if __name__ == "__main__":
    app = OverlayTextHooker()
    app.run()