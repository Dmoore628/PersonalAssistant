import tkinter as tk
from threading import Thread

class HUDOverlay:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("HUD Overlay")
        self.root.attributes('-topmost', True)
        self.root.attributes('-alpha', 0.8)
        self.root.geometry("300x200")
        self.root.configure(bg='black')
        self.root.overrideredirect(True)

        self.label = tk.Label(self.root, text="Task Status", fg="white", bg="black", font=("Arial", 14))
        self.label.pack(pady=10)

        self.status_text = tk.Text(self.root, height=10, width=40, bg="black", fg="white", wrap=tk.WORD)
        self.status_text.pack()

    def update_status(self, status):
        self.status_text.delete(1.0, tk.END)
        self.status_text.insert(tk.END, status)

    def run(self):
        self.root.mainloop()

def start_hud_overlay():
    hud = HUDOverlay()

    def update_loop():
        import time
        while True:
            # Example: Replace with real-time task updates
            hud.update_status("Task running...\nTask completed.")
            time.sleep(5)

    Thread(target=update_loop, daemon=True).start()
    hud.run()

if __name__ == "__main__":
    start_hud_overlay()