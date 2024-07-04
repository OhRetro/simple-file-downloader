import customtkinter as ctk
from components.core import FileDownloader

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Simple File Downloader")
        self.geometry("700x450")
        self.resizable(False, False)
        
        core = FileDownloader(self)
        core.pack(fill="both", expand=True, padx=10, pady=10)

if __name__ == "__main__":
    app = App()
    app.mainloop()
    