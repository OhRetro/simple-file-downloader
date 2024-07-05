import customtkinter as ctk
from components.wrapper import Wrapper
from components.widgets import session

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Simple File Downloader")
        self.geometry("700x450")
        self.resizable(False, False)
        wrapper = Wrapper(self)
        wrapper.pack(fill="both", expand=True, padx=10, pady=10)

if __name__ == "__main__":
    app = App()
    app.mainloop()
    
    #! Note to self, always remember to close sessions if using requests.Session()
    session.close()
    