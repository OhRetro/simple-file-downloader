import customtkinter as ctk
from requests import Session
from ua_generator import generate as ua_generate
from argparse import ArgumentParser
from components.wrapper import Wrapper
from components.log import log, log_exception, export_log_text

__version__ = "1.0.0"

class App(ctk.CTk):
    def __init__(self, **kwargs):
        ua = ua_generate()
        log(f"Generated UA: {ua}")
        
        self.session = Session()
        self.session.headers.update(ua.headers.get())

        super().__init__()
        self.title(f"Simple File Downloader v{__version__}")
        self.iconbitmap("./icon.ico")
        self.geometry("700x450")
        self.resizable(False, False)
        self.wrapper = Wrapper(self, self.session, **kwargs)
        self.wrapper.pack(fill="both", expand=True, padx=10, pady=10)
        
    def destroy(self):
        super().destroy()
        
        #! Note to self, always remember to close sessions if using requests.Session() in the future.
        log(f"Closing session")
        self.session.close()

def main():
    parser = ArgumentParser(
        "Simple File Downloader",
        description="A Simple File Downloader made with Python and customtkinter"
        )
    parser.add_argument("-e", "--export-log", action="store_true", help="export logs into a file after closing the program")
    parser.add_argument("--url-example", type=int, default=0, help="add example urls to download", metavar="QUANTITY")
    args = parser.parse_args()
    
    try:
        app = App(url_example=args.url_example)
        app.mainloop()
        
    except Exception as e:
        log_exception(e)
    
    except KeyboardInterrupt:
        pass
    
    if args.export_log:
        export_log_text()

if __name__ == "__main__":
    main()
    