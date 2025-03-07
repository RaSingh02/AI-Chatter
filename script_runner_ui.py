import subprocess
import tkinter as tk
from tkinter import ttk, scrolledtext
import sys
import os
from pathlib import Path
import threading
import queue
import asyncio
from styles import configure_styles
from utils import get_timestamp, get_log_colors
from auto_fine_tuner import AutoFineTuner


class ScriptRunnerUI:
    def __init__(self, master):
        self.master = master
        self.auto_tuner = None
        master.title('AI Chatter Script Runner')
        master.configure(bg='#f0f0f0')

        self.style = configure_styles()

        self.project_dir = Path(__file__).parent
        self.output_queue = queue.Queue()
        self.current_process = None

        self._setup_ui()
        self.monitor_output()

    def _setup_ui(self):
        # Create main container
        self.main_frame = ttk.Frame(self.master, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self._setup_header()
        self._setup_script_selection()
        self._setup_controls()
        self._setup_status()
        self._setup_log()

    def _setup_header(self):
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(header_frame, text='AI Chatter Control Panel',
                  font=('Segoe UI', 14, 'bold')).pack()

    def _setup_script_selection(self):
        script_frame = ttk.LabelFrame(
            self.main_frame, text='Available Scripts', padding=10)
        script_frame.pack(fill=tk.X, pady=(0, 10))

        self.script_mapping = {
            'chat_reader': ('Chat Reader', 'chat_reader.py'),
            'fine_tuner': ('Model Fine Tuner', 'model_fine_tuner.py'),
            'twitch_bot': ('Twitch Bot', 'twitch_bot.py'),
            'auto_tuner': ('Auto Fine Tuner', None),  # Special handling
        }

        self.script_var = tk.StringVar(value='chat_reader')
        for key, (display_name, _) in self.script_mapping.items():
            ttk.Radiobutton(script_frame, text=display_name,
                            variable=self.script_var, value=key).pack(anchor=tk.W)

    def _setup_controls(self):
        control_frame = ttk.Frame(self.main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))

        self.run_button = ttk.Button(control_frame, text='▶ Run Script',
                                     command=self.run_script, style='TButton')
        self.run_button.pack(side=tk.LEFT, padx=5)

        self.stop_button = ttk.Button(control_frame, text='⬛ Stop Script',
                                      command=self.stop_script, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)

        ttk.Button(control_frame, text='🗑 Clear Log',
                   command=self.clear_log).pack(side=tk.RIGHT, padx=5)

    def _setup_status(self):
        self.status_frame = ttk.Frame(self.main_frame)
        self.status_frame.pack(fill=tk.X, pady=(0, 5))
        self.status_label = ttk.Label(self.status_frame, text='Ready')
        self.status_label.pack(side=tk.LEFT)

    def _setup_log(self):
        log_frame = ttk.LabelFrame(
            self.main_frame, text='Log Output', padding=5)
        log_frame.pack(fill=tk.BOTH, expand=True)

        self.log_area = scrolledtext.ScrolledText(
            log_frame,
            width=70,
            height=20,
            font=('Consolas', 9),
            bg='#1e1e1e',
            fg='#d4d4d4',
            insertbackground='white'
        )
        self.log_area.pack(fill=tk.BOTH, expand=True)

    def log_message(self, message, level='INFO'):
        timestamp = get_timestamp()
        color_map = get_log_colors()
        self.log_area.tag_config(
            level, foreground=color_map.get(level, '#d4d4d4'))
        self.log_area.insert(tk.END, f'[{timestamp}] {message}\n', level)
        self.log_area.see(tk.END)

    def monitor_output(self):
        try:
            while True:
                message = self.output_queue.get_nowait()
                level = 'ERROR' if 'Error' in message else 'INFO'
                self.log_message(message, level)
        except queue.Empty:
            pass
        finally:
            self.master.after(100, self.monitor_output)

    def run_script(self):
        script_key = self.script_var.get()
        if script_key == 'auto_tuner':
            self.run_auto_tuner()
            return

        if script_key not in self.script_mapping:
            self.log_message(
                f'Invalid script selection: {script_key}', 'ERROR')
            return

        script_name = self.script_mapping[script_key][1]
        script_path = self.project_dir / script_name

        self.run_button.configure(state=tk.DISABLED)
        self.stop_button.configure(state=tk.NORMAL)
        self.status_label.configure(text=f'Running: {script_name}')

        def run_process():
            try:
                env = os.environ.copy()
                env['PYTHONPATH'] = str(self.project_dir)

                self.current_process = subprocess.Popen(
                    [sys.executable, str(script_path)],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    env=env,
                    cwd=str(self.project_dir),
                    bufsize=1,
                    universal_newlines=True
                )

                while self.current_process and self.current_process.poll() is None:
                    stdout = self.current_process.stdout.readline()
                    if stdout:
                        self.output_queue.put(stdout.strip())
                    stderr = self.current_process.stderr.readline()
                    if stderr:
                        self.output_queue.put(f"Error: {stderr.strip()}")

                if self.current_process:
                    return_code = self.current_process.wait()
                    if return_code == 0:
                        self.output_queue.put("Script completed successfully")
                    else:
                        self.output_queue.put(
                            f"Script failed with return code {return_code}")

            finally:
                self.master.after(0, self.reset_ui)

        threading.Thread(target=run_process, daemon=True).start()

    def run_auto_tuner(self):
        self.run_button.configure(state=tk.DISABLED)
        self.stop_button.configure(state=tk.NORMAL)
        self.status_label.configure(text='Running: Auto Fine Tuner')

        def run_async():
            async def start():
                self.auto_tuner = AutoFineTuner()
                try:
                    await self.auto_tuner.start()
                except Exception as e:
                    self.output_queue.put(f"Error in auto tuner: {e}")
                finally:
                    self.master.after(0, self.reset_ui)

            asyncio.run(start())

        threading.Thread(target=run_async, daemon=True).start()

    def stop_script(self):
        if self.auto_tuner:
            async def stop():
                await self.auto_tuner.stop()
            asyncio.run(stop())
            self.auto_tuner = None
            self.log_message("Auto tuner stopped by user", 'WARNING')
        elif self.current_process:
            self.current_process.terminate()
            self.log_message("Script stopped by user", 'WARNING')

        self.reset_ui()

    def reset_ui(self):
        self.current_process = None
        self.auto_tuner = None
        self.run_button.configure(state=tk.NORMAL)
        self.stop_button.configure(state=tk.DISABLED)
        self.status_label.configure(text='Ready')

    def clear_log(self):
        self.log_area.delete(1.0, tk.END)


if __name__ == '__main__':
    root = tk.Tk()
    root.geometry('800x600')
    app = ScriptRunnerUI(root)
    root.mainloop()
