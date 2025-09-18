import ctypes
import ctypes.wintypes
from ctypes import windll, POINTER, Structure, c_char_p, c_void_p, c_int, c_uint, c_ulong
import win32api
import win32con
import win32gui
import win32process
import win32clipboard
import psutil
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import queue
import time
import struct
from datetime import datetime
import json
import re


# Windows API structures
class MEMORY_BASIC_INFORMATION(Structure):
    _fields_ = [
        ("BaseAddress", c_void_p),
        ("AllocationBase", c_void_p),
        ("AllocationProtect", ctypes.wintypes.DWORD),
        ("RegionSize", ctypes.c_size_t),
        ("State", ctypes.wintypes.DWORD),
        ("Protect", ctypes.wintypes.DWORD),
        ("Type", ctypes.wintypes.DWORD)
    ]


class AdvancedTextHooker:
    def __init__(self):
        self.hooked_processes = {}
        self.text_patterns = []
        self.captured_texts = []
        self.running = False
        self.load_patterns()

    def load_patterns(self):
        """Load common text patterns for Japanese visual novels"""
        self.text_patterns = [
            # Common dialogue patterns
            rb'[\x81-\x9F\xE0-\xFC][\x40-\x7E\x80-\xFC]+',  # Shift-JIS
            rb'[\xA1-\xFE][\xA1-\xFE]+',  # EUC-JP
            rb'(?:\xE3[\x80-\xBF][\x80-\xBF])+',  # UTF-8 Japanese
        ]

    def hook_process_advanced(self, pid):
        """Advanced process hooking with memory reading"""
        try:
            # Open process with read permissions
            process_handle = windll.kernel32.OpenProcess(
                win32con.PROCESS_VM_READ | win32con.PROCESS_QUERY_INFORMATION,
                False,
                pid
            )

            if not process_handle:
                return False

            self.hooked_processes[pid] = {
                'handle': process_handle,
                'text_addresses': set(),
                'last_texts': set()
            }

            return True
        except Exception as e:
            print(f"Failed to hook process {pid}: {e}")
            return False

    def read_process_memory(self, pid, address, size):
        """Read memory from a process"""
        if pid not in self.hooked_processes:
            return None

        handle = self.hooked_processes[pid]['handle']
        buffer = ctypes.create_string_buffer(size)
        bytes_read = ctypes.c_size_t()

        result = windll.kernel32.ReadProcessMemory(
            handle,
            ctypes.c_void_p(address),
            buffer,
            size,
            ctypes.byref(bytes_read)
        )

        if result:
            return buffer.raw[:bytes_read.value]
        return None

    def scan_memory_for_text(self, pid):
        """Scan process memory for Japanese text"""
        if pid not in self.hooked_processes:
            return []

        handle = self.hooked_processes[pid]['handle']
        found_texts = []

        # Get system info for memory scanning
        system_info = ctypes.wintypes.SYSTEM_INFO()
        windll.kernel32.GetSystemInfo(ctypes.byref(system_info))

        min_address = system_info.lpMinimumApplicationAddress
        max_address = system_info.lpMaximumApplicationAddress

        current_address = min_address
        memory_info = MEMORY_BASIC_INFORMATION()

        while current_address < max_address:
            # Query memory region
            result = windll.kernel32.VirtualQueryEx(
                handle,
                ctypes.c_void_p(current_address),
                ctypes.byref(memory_info),
                ctypes.sizeof(memory_info)
            )

            if result == 0:
                break

            # Check if memory is readable
            if (memory_info.State == win32con.MEM_COMMIT and
                memory_info.Protect & win32con.PAGE_READWRITE):

                # Read memory region
                data = self.read_process_memory(pid, current_address, memory_info.RegionSize)

                if data:
                    # Search for text patterns
                    texts = self.extract_japanese_text(data)
                    for text in texts:
                        if text not in self.hooked_processes[pid]['last_texts']:
                            found_texts.append(text)
                            self.hooked_processes[pid]['last_texts'].add(text)

                            # Keep cache size manageable
                            if len(self.hooked_processes[pid]['last_texts']) > 500:
                                old_texts = list(self.hooked_processes[pid]['last_texts'])[:250]
                                for old in old_texts:
                                    self.hooked_processes[pid]['last_texts'].discard(old)

            current_address += memory_info.RegionSize

        return found_texts

    def extract_japanese_text(self, data):
        """Extract Japanese text from binary data"""
        texts = []

        # Try different encodings
        encodings = ['shift_jis', 'utf-8', 'euc-jp', 'utf-16-le']

        for encoding in encodings:
            try:
                decoded = data.decode(encoding, errors='ignore')

                # Find sequences of Japanese characters
                japanese_pattern = re.compile(
                    r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF\u3000-\u303F]{2,}'
                )

                matches = japanese_pattern.findall(decoded)

                for match in matches:
                    # Filter out noise
                    if len(match) >= 2 and len(match) <= 500:
                        # Check if it's meaningful text (not just repeated characters)
                        if len(set(match)) > 1:
                            texts.append(match)
            except:
                pass

        return texts

    def hook_window_messages(self, hwnd):
        """Hook window messages to capture text"""
        def window_proc(hwnd, msg, wparam, lparam):
            if msg == win32con.WM_SETTEXT:
                # Text is being set to a window
                try:
                    text = ctypes.string_at(lparam).decode('utf-8', errors='ignore')
                    if self._is_japanese(text):
                        self.captured_texts.append(('WM_SETTEXT', text))
                except:
                    pass

            return windll.user32.CallWindowProcW(
                self.old_window_proc,
                hwnd,
                msg,
                wparam,
                lparam
            )

        # Store old window procedure
        self.old_window_proc = win32gui.GetWindowLong(hwnd, win32con.GWL_WNDPROC)

        # Set new window procedure
        WNDPROC = ctypes.WINFUNCTYPE(
            ctypes.c_long,
            ctypes.wintypes.HWND,
            ctypes.c_uint,
            ctypes.wintypes.WPARAM,
            ctypes.wintypes.LPARAM
        )

        self.window_proc_hook = WNDPROC(window_proc)
        win32gui.SetWindowLong(hwnd, win32con.GWL_WNDPROC, self.window_proc_hook)

    def _is_japanese(self, text):
        """Check if text contains Japanese characters"""
        if not text:
            return False

        for char in text:
            code = ord(char)
            if (0x3040 <= code <= 0x309F) or \
               (0x30A0 <= code <= 0x30FF) or \
               (0x4E00 <= code <= 0x9FAF) or \
               (0x3000 <= code <= 0x303F):
                return True
        return False

    def monitor_clipboard(self):
        """Monitor clipboard for Japanese text"""
        last_clipboard = ""

        while self.running:
            try:
                win32clipboard.OpenClipboard()
                if win32clipboard.IsClipboardFormatAvailable(win32con.CF_UNICODETEXT):
                    data = win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
                    if data != last_clipboard and self._is_japanese(data):
                        self.captured_texts.append(('Clipboard', data))
                        last_clipboard = data
                win32clipboard.CloseClipboard()
            except:
                pass

            time.sleep(0.5)


class AdvancedHookerGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Advanced Japanese Text Hooker")
        self.root.geometry("1000x700")

        self.hooker = AdvancedTextHooker()
        self.monitor_threads = []
        self.selected_process = None

        self.setup_ui()

    def setup_ui(self):
        # Create notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Main capture tab
        capture_tab = ttk.Frame(notebook)
        notebook.add(capture_tab, text="Capture")
        self.setup_capture_tab(capture_tab)

        # Settings tab
        settings_tab = ttk.Frame(notebook)
        notebook.add(settings_tab, text="Settings")
        self.setup_settings_tab(settings_tab)

        # History tab
        history_tab = ttk.Frame(notebook)
        notebook.add(history_tab, text="History")
        self.setup_history_tab(history_tab)

        # Status bar
        self.status_label = ttk.Label(self.root, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(fill=tk.X, side=tk.BOTTOM)

    def setup_capture_tab(self, parent):
        # Process selection frame
        select_frame = ttk.LabelFrame(parent, text="Process Selection", padding="10")
        select_frame.pack(fill=tk.X, padx=5, pady=5)

        # Process list
        columns = ('Process', 'PID', 'Window Title')
        self.process_tree = ttk.Treeview(select_frame, columns=columns, height=5)

        for col in columns:
            self.process_tree.heading(col, text=col)
            self.process_tree.column(col, width=200)

        self.process_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Control buttons
        button_frame = ttk.Frame(select_frame)
        button_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))

        ttk.Button(button_frame, text="Refresh", command=self.refresh_processes).pack(pady=2, fill=tk.X)
        ttk.Button(button_frame, text="Hook Selected", command=self.hook_selected).pack(pady=2, fill=tk.X)
        ttk.Button(button_frame, text="Start Capture", command=self.start_capture).pack(pady=2, fill=tk.X)
        ttk.Button(button_frame, text="Stop Capture", command=self.stop_capture).pack(pady=2, fill=tk.X)

        # Text display frame
        text_frame = ttk.LabelFrame(parent, text="Captured Text", padding="10")
        text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.text_display = scrolledtext.ScrolledText(
            text_frame,
            wrap=tk.WORD,
            width=80,
            height=20,
            font=("Yu Gothic UI", 11)
        )
        self.text_display.pack(fill=tk.BOTH, expand=True)

        # Action buttons
        action_frame = ttk.Frame(text_frame)
        action_frame.pack(fill=tk.X, pady=(5, 0))

        ttk.Button(action_frame, text="Copy", command=self.copy_text).pack(side=tk.LEFT, padx=2)
        ttk.Button(action_frame, text="Save", command=self.save_text).pack(side=tk.LEFT, padx=2)
        ttk.Button(action_frame, text="Clear", command=self.clear_text).pack(side=tk.LEFT, padx=2)
        ttk.Button(action_frame, text="Auto-scroll", command=self.toggle_autoscroll).pack(side=tk.LEFT, padx=2)

        self.autoscroll = True

    def setup_settings_tab(self, parent):
        # Capture methods
        method_frame = ttk.LabelFrame(parent, text="Capture Methods", padding="10")
        method_frame.pack(fill=tk.X, padx=5, pady=5)

        self.capture_methods = {
            'window_text': tk.BooleanVar(value=True),
            'memory_scan': tk.BooleanVar(value=False),
            'clipboard': tk.BooleanVar(value=True),
            'window_messages': tk.BooleanVar(value=False)
        }

        ttk.Checkbutton(method_frame, text="Window Text (GetWindowText)",
                       variable=self.capture_methods['window_text']).pack(anchor=tk.W)
        ttk.Checkbutton(method_frame, text="Memory Scanning (Advanced)",
                       variable=self.capture_methods['memory_scan']).pack(anchor=tk.W)
        ttk.Checkbutton(method_frame, text="Clipboard Monitoring",
                       variable=self.capture_methods['clipboard']).pack(anchor=tk.W)
        ttk.Checkbutton(method_frame, text="Window Messages (WM_SETTEXT)",
                       variable=self.capture_methods['window_messages']).pack(anchor=tk.W)

        # Filter settings
        filter_frame = ttk.LabelFrame(parent, text="Text Filters", padding="10")
        filter_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(filter_frame, text="Minimum Length:").grid(row=0, column=0, sticky=tk.W)
        self.min_length = tk.IntVar(value=2)
        ttk.Spinbox(filter_frame, from_=1, to=100, textvariable=self.min_length, width=10).grid(row=0, column=1)

        ttk.Label(filter_frame, text="Maximum Length:").grid(row=1, column=0, sticky=tk.W)
        self.max_length = tk.IntVar(value=500)
        ttk.Spinbox(filter_frame, from_=10, to=1000, textvariable=self.max_length, width=10).grid(row=1, column=1)

        # Duplicate filter
        self.filter_duplicates = tk.BooleanVar(value=True)
        ttk.Checkbutton(filter_frame, text="Filter Duplicates",
                       variable=self.filter_duplicates).grid(row=2, column=0, columnspan=2, sticky=tk.W)

    def setup_history_tab(self, parent):
        # History list
        history_frame = ttk.Frame(parent, padding="10")
        history_frame.pack(fill=tk.BOTH, expand=True)

        self.history_list = scrolledtext.ScrolledText(
            history_frame,
            wrap=tk.WORD,
            width=80,
            height=25,
            font=("Yu Gothic UI", 10)
        )
        self.history_list.pack(fill=tk.BOTH, expand=True)

        # History controls
        control_frame = ttk.Frame(history_frame)
        control_frame.pack(fill=tk.X, pady=(5, 0))

        ttk.Button(control_frame, text="Export History", command=self.export_history).pack(side=tk.LEFT, padx=2)
        ttk.Button(control_frame, text="Clear History", command=self.clear_history).pack(side=tk.LEFT, padx=2)

    def refresh_processes(self):
        """Refresh the list of processes"""
        self.process_tree.delete(*self.process_tree.get_children())

        for proc in psutil.process_iter(['pid', 'name']):
            try:
                pid = proc.info['pid']
                name = proc.info['name']

                # Try to get window title
                windows = []
                def enum_callback(hwnd, windows):
                    _, window_pid = win32process.GetWindowThreadProcessId(hwnd)
                    if window_pid == pid and win32gui.IsWindowVisible(hwnd):
                        title = win32gui.GetWindowText(hwnd)
                        if title:
                            windows.append(title)
                    return True

                win32gui.EnumWindows(enum_callback, windows)

                if windows:
                    for title in windows[:1]:  # Show first window only
                        self.process_tree.insert('', tk.END, values=(name, pid, title))
            except:
                pass

        self.update_status("Process list refreshed")

    def hook_selected(self):
        """Hook the selected process"""
        selection = self.process_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a process first")
            return

        item = self.process_tree.item(selection[0])
        values = item['values']
        pid = values[1]

        if self.hooker.hook_process_advanced(pid):
            self.selected_process = pid
            self.update_status(f"Hooked to process {pid}")
        else:
            messagebox.showerror("Hook Failed", f"Failed to hook process {pid}")

    def start_capture(self):
        """Start capturing text"""
        if not self.selected_process:
            messagebox.showwarning("No Process", "Please hook a process first")
            return

        self.hooker.running = True

        # Start memory scanning if enabled
        if self.capture_methods['memory_scan'].get():
            thread = threading.Thread(target=self.memory_scan_loop, daemon=True)
            thread.start()
            self.monitor_threads.append(thread)

        # Start clipboard monitoring if enabled
        if self.capture_methods['clipboard'].get():
            thread = threading.Thread(target=self.hooker.monitor_clipboard, daemon=True)
            thread.start()
            self.monitor_threads.append(thread)

        # Start text update loop
        self.root.after(100, self.update_captured_text)

        self.update_status("Capture started")

    def memory_scan_loop(self):
        """Continuously scan memory for text"""
        while self.hooker.running:
            if self.selected_process:
                texts = self.hooker.scan_memory_for_text(self.selected_process)
                for text in texts:
                    self.hooker.captured_texts.append(('Memory', text))
            time.sleep(0.5)

    def update_captured_text(self):
        """Update the display with captured text"""
        if not self.hooker.running:
            return

        while self.hooker.captured_texts:
            source, text = self.hooker.captured_texts.pop(0)

            # Apply filters
            if len(text) < self.min_length.get() or len(text) > self.max_length.get():
                continue

            timestamp = datetime.now().strftime("%H:%M:%S")
            formatted = f"[{timestamp}][{source}] {text}\n"

            self.text_display.insert(tk.END, formatted)
            self.history_list.insert(tk.END, formatted)

            if self.autoscroll:
                self.text_display.see(tk.END)
                self.history_list.see(tk.END)

        # Continue updating
        self.root.after(100, self.update_captured_text)

    def stop_capture(self):
        """Stop capturing text"""
        self.hooker.running = False
        self.update_status("Capture stopped")

    def copy_text(self):
        """Copy selected text"""
        try:
            selected = self.text_display.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.root.clipboard_clear()
            self.root.clipboard_append(selected)
            self.update_status("Text copied")
        except:
            all_text = self.text_display.get(1.0, tk.END)
            self.root.clipboard_clear()
            self.root.clipboard_append(all_text)
            self.update_status("All text copied")

    def save_text(self):
        """Save captured text to file"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialfile=f"captured_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        )

        if filename:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(self.text_display.get(1.0, tk.END))
            self.update_status(f"Saved to {filename}")

    def clear_text(self):
        """Clear the text display"""
        self.text_display.delete(1.0, tk.END)

    def toggle_autoscroll(self):
        """Toggle auto-scrolling"""
        self.autoscroll = not self.autoscroll
        self.update_status(f"Auto-scroll: {'ON' if self.autoscroll else 'OFF'}")

    def export_history(self):
        """Export history to JSON"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialfile=f"history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )

        if filename:
            history_text = self.history_list.get(1.0, tk.END)
            lines = history_text.strip().split('\n')

            history_data = []
            for line in lines:
                if line:
                    match = re.match(r'\[(\d{2}:\d{2}:\d{2})\]\[([^\]]+)\] (.+)', line)
                    if match:
                        history_data.append({
                            'timestamp': match.group(1),
                            'source': match.group(2),
                            'text': match.group(3)
                        })

            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(history_data, f, ensure_ascii=False, indent=2)

            self.update_status(f"History exported to {filename}")

    def clear_history(self):
        """Clear history"""
        self.history_list.delete(1.0, tk.END)
        self.update_status("History cleared")

    def update_status(self, message):
        """Update status bar"""
        self.status_label.config(text=message)

    def run(self):
        """Run the GUI"""
        self.root.mainloop()


if __name__ == "__main__":
    app = AdvancedHookerGUI()
    app.run()