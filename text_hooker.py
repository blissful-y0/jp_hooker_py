import ctypes
import ctypes.wintypes
import win32api
import win32con
import win32gui
import win32process
import psutil
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import queue
import time
import pyperclip
from datetime import datetime


class TextHooker:
    def __init__(self):
        self.hooked_processes = {}
        self.text_queue = queue.Queue()
        self.running = False
        self.hook = None

    def find_game_windows(self):
        """Find all running game windows"""
        game_windows = []

        def enum_windows_callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                window_text = win32gui.GetWindowText(hwnd)
                if window_text:
                    try:
                        _, pid = win32process.GetWindowThreadProcessId(hwnd)
                        process = psutil.Process(pid)
                        windows.append({
                            'hwnd': hwnd,
                            'title': window_text,
                            'pid': pid,
                            'process_name': process.name()
                        })
                    except:
                        pass
            return True

        win32gui.EnumWindows(enum_windows_callback, game_windows)
        return game_windows

    def hook_process(self, pid):
        """Hook into a specific process to capture text"""
        if pid in self.hooked_processes:
            return False

        try:
            # Open process with necessary permissions
            process_handle = win32api.OpenProcess(
                win32con.PROCESS_ALL_ACCESS,
                False,
                pid
            )

            self.hooked_processes[pid] = {
                'handle': process_handle,
                'hooks': []
            }

            return True
        except Exception as e:
            print(f"Failed to hook process {pid}: {e}")
            return False

    def unhook_process(self, pid):
        """Unhook from a process"""
        if pid in self.hooked_processes:
            try:
                win32api.CloseHandle(self.hooked_processes[pid]['handle'])
                del self.hooked_processes[pid]
                return True
            except:
                pass
        return False

    def capture_text(self, hwnd):
        """Capture text from a window using various methods"""
        captured_texts = []

        # Method 1: GetWindowText
        try:
            window_text = win32gui.GetWindowText(hwnd)
            if window_text:
                captured_texts.append(('Window Title', window_text))
        except:
            pass

        # Method 2: SendMessage with WM_GETTEXT
        try:
            length = win32gui.SendMessage(hwnd, win32con.WM_GETTEXTLENGTH, 0, 0)
            if length > 0:
                buffer = ctypes.create_unicode_buffer(length + 1)
                win32gui.SendMessage(hwnd, win32con.WM_GETTEXT, length + 1, buffer)
                if buffer.value:
                    captured_texts.append(('WM_GETTEXT', buffer.value))
        except:
            pass

        # Method 3: Enumerate child windows
        def enum_child_callback(child_hwnd, texts):
            try:
                child_text = win32gui.GetWindowText(child_hwnd)
                if child_text and self._is_japanese(child_text):
                    texts.append(('Child Window', child_text))

                # Try WM_GETTEXT on child windows
                length = win32gui.SendMessage(child_hwnd, win32con.WM_GETTEXTLENGTH, 0, 0)
                if length > 0:
                    buffer = ctypes.create_unicode_buffer(length + 1)
                    win32gui.SendMessage(child_hwnd, win32con.WM_GETTEXT, length + 1, buffer)
                    if buffer.value and self._is_japanese(buffer.value):
                        texts.append(('Child Text', buffer.value))
            except:
                pass
            return True

        try:
            win32gui.EnumChildWindows(hwnd, enum_child_callback, captured_texts)
        except:
            pass

        return captured_texts

    def _is_japanese(self, text):
        """Check if text contains Japanese characters"""
        if not text:
            return False

        # Check for Hiragana (3040-309F), Katakana (30A0-30FF), or Kanji (4E00-9FAF)
        for char in text:
            code = ord(char)
            if (0x3040 <= code <= 0x309F) or \
               (0x30A0 <= code <= 0x30FF) or \
               (0x4E00 <= code <= 0x9FAF):
                return True
        return False

    def monitor_window(self, hwnd, callback):
        """Monitor a window for text changes"""
        self.running = True
        last_texts = set()

        while self.running:
            try:
                texts = self.capture_text(hwnd)
                for source, text in texts:
                    if text and text not in last_texts:
                        if self._is_japanese(text):
                            callback(f"[{source}] {text}")
                            last_texts.add(text)
                            # Keep only recent texts to avoid memory issues
                            if len(last_texts) > 100:
                                last_texts = set(list(last_texts)[-50:])
            except:
                pass

            time.sleep(0.1)  # Check every 100ms

    def stop_monitoring(self):
        """Stop monitoring"""
        self.running = False


class TextHookerGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Japanese Text Hooker")
        self.root.geometry("900x600")

        self.hooker = TextHooker()
        self.monitor_thread = None
        self.selected_window = None

        self.setup_ui()

    def setup_ui(self):
        # Top frame for controls
        control_frame = ttk.Frame(self.root, padding="10")
        control_frame.pack(fill=tk.X)

        # Process selection
        ttk.Label(control_frame, text="Select Window:").pack(side=tk.LEFT, padx=(0, 5))

        self.window_combo = ttk.Combobox(control_frame, width=50, state="readonly")
        self.window_combo.pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(control_frame, text="Refresh", command=self.refresh_windows).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(control_frame, text="Start Capture", command=self.start_capture).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(control_frame, text="Stop Capture", command=self.stop_capture).pack(side=tk.LEFT, padx=(0, 5))

        # Text display area
        text_frame = ttk.Frame(self.root, padding="10")
        text_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(text_frame, text="Captured Text:").pack(anchor=tk.W)

        self.text_display = scrolledtext.ScrolledText(
            text_frame,
            wrap=tk.WORD,
            width=80,
            height=20,
            font=("Yu Gothic", 11)  # Font that supports Japanese
        )
        self.text_display.pack(fill=tk.BOTH, expand=True, pady=(5, 0))

        # Bottom frame for actions
        action_frame = ttk.Frame(self.root, padding="10")
        action_frame.pack(fill=tk.X)

        ttk.Button(action_frame, text="Copy Selected", command=self.copy_selected).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(action_frame, text="Copy All", command=self.copy_all).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(action_frame, text="Clear", command=self.clear_text).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(action_frame, text="Save to File", command=self.save_to_file).pack(side=tk.LEFT, padx=(0, 5))

        # Status bar
        self.status_label = ttk.Label(self.root, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(fill=tk.X, side=tk.BOTTOM)

        # Initial window refresh
        self.refresh_windows()

    def refresh_windows(self):
        """Refresh the list of available windows"""
        windows = self.hooker.find_game_windows()
        window_list = [f"{w['title']} (PID: {w['pid']})" for w in windows]
        self.window_combo['values'] = window_list

        if window_list:
            self.window_combo.current(0)

        self.windows_data = windows
        self.update_status(f"Found {len(windows)} windows")

    def start_capture(self):
        """Start capturing text from selected window"""
        if not self.window_combo.get():
            messagebox.showwarning("No Selection", "Please select a window first")
            return

        if self.monitor_thread and self.monitor_thread.is_alive():
            messagebox.showinfo("Already Running", "Capture is already running")
            return

        # Get selected window
        index = self.window_combo.current()
        self.selected_window = self.windows_data[index]

        # Hook the process
        if self.hooker.hook_process(self.selected_window['pid']):
            self.update_status(f"Hooked to: {self.selected_window['title']}")

        # Start monitoring in a separate thread
        self.monitor_thread = threading.Thread(
            target=self.hooker.monitor_window,
            args=(self.selected_window['hwnd'], self.add_captured_text),
            daemon=True
        )
        self.monitor_thread.start()

        self.update_status(f"Capturing from: {self.selected_window['title']}")

    def stop_capture(self):
        """Stop capturing text"""
        self.hooker.stop_monitoring()

        if self.selected_window:
            self.hooker.unhook_process(self.selected_window['pid'])

        self.update_status("Capture stopped")

    def add_captured_text(self, text):
        """Add captured text to the display"""
        self.root.after(0, self._add_text_to_display, text)

    def _add_text_to_display(self, text):
        """Add text to display (must be called from main thread)"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.text_display.insert(tk.END, f"[{timestamp}] {text}\n")
        self.text_display.see(tk.END)

    def copy_selected(self):
        """Copy selected text to clipboard"""
        try:
            selected = self.text_display.get(tk.SEL_FIRST, tk.SEL_LAST)
            pyperclip.copy(selected)
            self.update_status("Selected text copied to clipboard")
        except tk.TclError:
            messagebox.showwarning("No Selection", "Please select text first")

    def copy_all(self):
        """Copy all text to clipboard"""
        all_text = self.text_display.get(1.0, tk.END)
        pyperclip.copy(all_text)
        self.update_status("All text copied to clipboard")

    def clear_text(self):
        """Clear the text display"""
        self.text_display.delete(1.0, tk.END)
        self.update_status("Text cleared")

    def save_to_file(self):
        """Save captured text to file"""
        from tkinter import filedialog

        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialfile=f"captured_text_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        )

        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.text_display.get(1.0, tk.END))
                self.update_status(f"Saved to: {filename}")
            except Exception as e:
                messagebox.showerror("Save Error", f"Failed to save file: {e}")

    def update_status(self, message):
        """Update status bar"""
        self.status_label.config(text=message)

    def run(self):
        """Run the GUI"""
        self.root.mainloop()


if __name__ == "__main__":
    app = TextHookerGUI()
    app.run()