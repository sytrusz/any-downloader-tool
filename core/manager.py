import subprocess
import threading
import queue
import os
import sys
import shutil

class DownloadManager:
    def __init__(self):
        self.output_queue = queue.Queue()
        self.process = None
        self.base_path = self._get_base_path()

    def _get_base_path(self):
        """Returns the base path for the application, handling PyInstaller bundling."""
        if getattr(sys, 'frozen', False):
            # If running as a bundled executable
            return sys._MEIPASS
        # If running as a raw script
        return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    def _resolve_engine_path(self, engine_name):
        """
        Locates the full path for a given engine (yt-dlp, spotdl, etc.)
        Order of priority:
        1. Bundled 'bin' folder (for portable builds)
        2. Local '.venv/bin' folder (for development)
        3. System PATH
        """
        # 1. Check bundled bin folder
        bundled_path = os.path.join(self.base_path, "bin", engine_name)
        if os.name == 'nt': bundled_path += ".exe"
        if os.path.exists(bundled_path):
            return bundled_path

        # 2. Check virtual environment
        venv_path = os.path.join(self.base_path, ".venv", "bin", engine_name)
        if os.name == 'nt': venv_path = os.path.join(self.base_path, ".venv", "Scripts", engine_name + ".exe")
        if os.path.exists(venv_path):
            return venv_path

        # 3. Fallback to system PATH
        system_path = shutil.which(engine_name)
        if system_path:
            return system_path

        return engine_name # Return as is, hope for the best

    def start_download(self, command, cwd=None):
        """Starts the download process in a separate thread."""
        # Resolve the engine path (first element of command)
        engine = command[0]
        resolved_engine = self._resolve_engine_path(engine)
        
        # Reconstruct command with resolved engine
        full_command = [resolved_engine] + command[1:]
        
        self.output_queue.put(("STATUS", f"Starting: {' '.join(full_command)}"))
        if cwd:
            self.output_queue.put(("STATUS", f"Output directory: {cwd}"))
            
        thread = threading.Thread(target=self._run_process, args=(full_command, cwd), daemon=True)
        thread.start()

    def _run_process(self, command, cwd):
        """Runs the subprocess and captures stdout and stderr."""
        try:
            # Ensure FFmpeg is available in the path if bundled
            env = os.environ.copy()
            bundled_bin = os.path.join(self.base_path, "bin")
            if os.path.exists(bundled_bin):
                env["PATH"] = bundled_bin + os.pathsep + env.get("PATH", "")

            self.process = subprocess.Popen(
                command,
                cwd=cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                env=env # Inject bundled bin into path for ffmpeg access
            )

            # Start threads to read stdout and stderr continuously
            stdout_thread = threading.Thread(target=self._read_stream, args=(self.process.stdout, "STDOUT"), daemon=True)
            stderr_thread = threading.Thread(target=self._read_stream, args=(self.process.stderr, "STDERR"), daemon=True)
            
            stdout_thread.start()
            stderr_thread.start()
            
            self.process.wait()
            
            stdout_thread.join()
            stderr_thread.join()
            
            self.output_queue.put(("STATUS", f"Process finished with exit code {self.process.returncode}"))
            
        except Exception as e:
            self.output_queue.put(("ERROR", str(e)))

    def _read_stream(self, stream, stream_type):
        """Reads from a stream and puts lines into the queue, handling carriage returns."""
        buffer = ""
        while True:
            char = stream.read(1)
            if not char:
                if buffer:
                    self.output_queue.put((stream_type, buffer.strip()))
                break
            if char in ['\r', '\n']:
                if buffer:
                    self.output_queue.put((stream_type, buffer.strip()))
                    buffer = ""
            else:
                buffer += char
        stream.close()

    def get_messages(self):
        """Returns all available messages from the queue without blocking."""
        messages = []
        while not self.output_queue.empty():
            try:
                messages.append(self.output_queue.get_nowait())
            except queue.Empty:
                break
        return messages
