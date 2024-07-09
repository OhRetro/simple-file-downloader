import customtkinter as ctk
from requests import Session
from ua_generator import generate as ua_generate
from argparse import ArgumentParser
from components.wrapper import Wrapper
from components.log import log, log_exception, export_log_text

__version__ = "1.0.0"

ua = ua_generate()
session = Session()
session.headers.update(ua.headers.get())

log(f"Generated UA: {ua}")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(f"Simple File Downloader v{__version__}")
        self.iconbitmap("./icon.ico")
        self.geometry("700x450")
        self.resizable(False, False)
        self.wrapper = Wrapper(self, session)
        self.wrapper.pack(fill="both", expand=True, padx=10, pady=10)

def main():
    parser = ArgumentParser(
        "Simple File Downloader",
        description="A Simple File Downloader made with Python and customtkinter"
        )

    parser.add_argument("-e", "--export-log", action="store_true", help="Export logs into a file after closing the program")

    args = parser.parse_args()
    
    try:
        app = App()
        app.mainloop()
        
    except Exception as e:
        log_exception(e)
    
    except KeyboardInterrupt:
        pass
    
    #! Note to self, always remember to close sessions if using requests.Session() in the future.
    log(f"Closing session")
    session.close()
    
    if args.export_log:
        export_log_text()

if __name__ == "__main__":
    main()
    