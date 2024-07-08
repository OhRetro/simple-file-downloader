import customtkinter as ctk
from traceback import print_exception
from requests import Session
from ua_generator import generate as ua_generate
from components.wrapper import Wrapper
from components.log import log

ua = ua_generate()
session = Session()
session.headers.update(ua.headers.get())

log(f"Generated UA: {ua}")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Simple File Downloader")
        self.geometry("700x450")
        self.resizable(False, False)
        self.wrapper = Wrapper(self, session)
        self.wrapper.pack(fill="both", expand=True, padx=10, pady=10)

if __name__ == "__main__":
    try:
        app = App()
        app.mainloop()
        
    except Exception as e:
        bar = "=" * 100
        print(f"\n{bar}")
        print_exception(e)
        print(f"{bar}\n")
    
    #! Note to self, always remember to close sessions if using requests.Session() in the future.
    log(f"Closing session")
    session.close()
    