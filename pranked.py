import tkinter as tk
import random
import os
import winsound
import ctypes
import time

# --- Configuration ---
FLASH_DURATION_MS = 5000          # total flash time
FLASH_INTERVAL_MS = 300           # how fast images change
IMAGE_FILES = ["EA1.png", "EA2.png", "EA3.png", "EA4.png", "EA5.png"]
AUDIO_FILE = "AU1.wav"
# ----------------------

user32 = ctypes.windll.user32

def block_input(block: bool) -> bool:
    """Block / unblock keyboard & mouse. Requires Administrator privileges."""
    return bool(user32.BlockInput(block))

class FlashShow:
    def __init__(self, root):
        self.root = root
        self.root.title("Flash Show")
        self.root.attributes("-fullscreen", True)
        self.root.configure(bg="black")

        self.canvas = tk.Canvas(root, bg="black", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.prompt_label = tk.Label(
            root, text="Press any key to start",
            font=("Segoe UI", 24), fg="white", bg="black"
        )
        self.canvas.create_window(
            root.winfo_screenwidth() // 2,
            root.winfo_screenheight() // 2,
            window=self.prompt_label
        )

        self.info_label = tk.Label(
            root, text="Press Esc anytime to quit  •  Ctrl+Alt+Del overrides input block",
            font=("Segoe UI", 12), fg="white", bg="black"
        )
        self.canvas.create_window(
            root.winfo_screenwidth() // 2,
            root.winfo_screenheight() // 2 + 60,
            window=self.info_label
        )

        self.running = False
        self.started = False
        self.input_blocked = False

        self.root.bind("<Key>", self._on_key_press)
        self.root.protocol("WM_DELETE_WINDOW", self._cleanup_and_quit)

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
        if not images:
            missing = ", ".join(IMAGE_FILES)
            self.info_label.configure(
                text=f"No images found. Expected: {missing}  (Esc to quit)"
            )
        return images

    def _find_audio(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(script_dir, AUDIO_FILE)
        if os.path.isfile(path) and path.lower().endswith(".wav"):
            return path
        return None

    def _on_key_press(self, event):
        if event.keysym == "Escape":
            self._cleanup_and_quit()
        elif not self.started:
            self.start_flashing()

    def start_flashing(self):
        if not self.images:
            return

        self.started = True
        self.prompt_label.place_forget()
        self.canvas.delete("all")
        self.running = True
        self.elapsed = 0

        # Block keyboard + mouse for the duration of the show
        success = block_input(True)
        self.input_blocked = success
        if not success:
            print("Could not block input – try running as Administrator.")
        else:
            print("Input blocked for 5 seconds. Ctrl+Alt+Del can still override.")

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
        """Always unblock input and stop sound before exiting."""
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
