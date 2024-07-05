import customtkinter as ctk
from tkinter import messagebox as tk_messagebox
from random import randint
from .url import url_is_valid
from .widgets import FileURLDownloaderWidget
from .log import log

class Wrapper(ctk.CTkFrame):
    def __init__(self, root: ctk.CTk):
        super().__init__(root)
        self.downloader_widgets: dict[str, FileURLDownloaderWidget] = {}

        self.setup_widgets()
        
        # self.add_url("https://github.com/szalony9szymek/large/releases/download/free/large")
        # self.add_url_examples(3)
    
    def setup_widgets(self):
        entry_frame = ctk.CTkFrame(self)
        entry_frame.pack(fill="x", padx=10, pady=10)

        self.url_entry = ctk.CTkEntry(entry_frame, placeholder_text="Type/Paste a file URL")
        self.url_entry.pack(side="left", fill="x", expand=True, padx=5)

        add_button = ctk.CTkButton(entry_frame, text="Add", command=self.add_downloader_widget)
        add_button.pack(side="left", padx=5, pady=5)
        
        control_frame = ctk.CTkFrame(self)
        control_frame.pack(fill="x", padx=10, pady=10)

        w_size = 320

        download_all_button = ctk.CTkButton(control_frame, w_size, text="Download All", command=self.on_download_all_button_clicked)
        download_all_button.pack(side="left", padx=5, pady=5)

        remove_all_button = ctk.CTkButton(control_frame, w_size, text="Remove All", fg_color="red", hover_color="darkred", command=self.on_remove_all_button_clicked)
        remove_all_button.pack(side="right", padx=5, pady=5)
        
        self.list_of_download_task = ctk.CTkScrollableFrame(self, label_text="URLs list")
        self.list_of_download_task.pack(fill="both", expand=True, padx=10, pady=10)
        
        log(f"{self.__class__.__name__} Widgets Setup!")
    
    def on_download_all_button_clicked(self):
        if len(self.downloader_widgets) > 0:
            log(f"Downloading all!")
        else:
            log("No URLs to download!")
            
        for url, widget in self.downloader_widgets.items():
            widget: FileURLDownloaderWidget
            if not widget.downloading and not widget.download_success:
                widget.download_button.invoke()
            else:
                log(f"Is already downloading or is completed: {url}")

    def on_remove_all_button_clicked(self):
        if len(self.downloader_widgets) > 0:
            log(f"Removing all!")
        else:
            log("No URLs to remove!")
        
        to_delete: list[str] = []
        
        for url, widget in self.downloader_widgets.items():
            widget: FileURLDownloaderWidget
            if not widget.downloading:
                widget.remove_button.invoke()
                to_delete.append(url)
            else:
                log(f"Can't remove as it's downloading: {url}")
                
        for url in to_delete:
            del self.downloader_widgets[url]
      
    def add_downloader_widget(self):
        url = self.url_entry.get()
        
        if url and not url_is_valid(url):
            error_message = f"The provided link is not a valid URL:\n\"{url}\"\nPlease enter a valid URL."
            tk_messagebox.showerror("Invalid URL", error_message)
            log(error_message)

        elif url and url_is_valid(url) and url in self.downloader_widgets:
            error_message = f"The provided link is already in the list:\n\"{url}\""
            tk_messagebox.showerror("Already on List", error_message)
            log(error_message)
                     
        elif url and url_is_valid(url) and url not in self.downloader_widgets:
            downloader_widget = FileURLDownloaderWidget(
                self.list_of_download_task, url
                )
            
            self.downloader_widgets[url] = downloader_widget
            downloader_widget.true_parent = self
            
            downloader_widget.bind_events(self.master)
            
            log(f"Added URL: \"{url}\"")

        self.url_entry.delete(0, "end")
        # self.list_of_download_task.update_idletasks()

    def add_url(self, url: str):
        self.url_entry.insert(0, url)
        self.add_downloader_widget()
    
    def add_url_examples(self, quantity: int):
        for _ in range(quantity):
            x = randint(100, 300)
            y = randint(100, 300)
            self.add_url(f"https://picsum.photos/{x}/{y}")
