import requests
import customtkinter as ctk
import threading as th
from ua_generator import generate as ua_generate
from tkinter import messagebox as tk_messagebox
from os import makedirs as os_makedirs
from os.path import (abspath as osp_abspath, 
                     expanduser as osp_expanduser, 
                     isfile as osp_isfile, 
                     splitext as osp_splitext)
from random import randint
from .url import url_is_valid, url_get_filename
from .gui import FileURLDownloader

ua = ua_generate()
seasson = requests.Session()
seasson.headers.update(ua.headers.get())

print(f"Generated UA: {ua}")

class FileDownloader(ctk.CTkFrame):
    def __init__(self, root: ctk.CTk):
        super().__init__(root)
        self.urls_item_widget: dict[str, FileURLDownloader] = {}

        self.setup_gui()
        self.add_url_examples(10)
        
    def add_url_examples(self, quantity: int = 3):
        for _ in range(quantity):
            x = randint(100, 300)
            y = randint(100, 300)
            self.link_entry.insert(0, f"https://picsum.photos/{x}/{y}")
            self.add_item()

    def setup_gui(self):
        entry_frame = ctk.CTkFrame(self)
        entry_frame.pack(fill="x", padx=10, pady=10)

        self.link_entry = ctk.CTkEntry(entry_frame, placeholder_text="Enter file URL link")
        self.link_entry.pack(side="left", fill="x", expand=True, padx=5)

        self.add_button = ctk.CTkButton(entry_frame, text="Add", command=self.add_item)
        self.add_button.pack(side="left", padx=5, pady=5)

        # Frame for List of urls
        self.listbox = ctk.CTkScrollableFrame(self, label_text="URLs list")
        self.listbox.pack(fill="both", expand=True, padx=10, pady=10)
        
        print("GUI Created!")
    
    def remove_item(self, name: str):
        if name in self.urls_item_widget:
            self.urls_item_widget[name]["main_frame"].destroy()
            del self.urls_item_widget[name]
            print(f"Deleted URL: {name}")
        
    def add_item(self):
        link = self.link_entry.get()

        if link and not url_is_valid(link):
            error_message = f"The provided link is not a valid URL:\n\"{link}\"\nPlease enter a valid URL."
            tk_messagebox.showerror("Invalid URL", error_message)
            print(error_message)

        elif link and url_is_valid(link) and link in self.urls_item_widget:
            error_message = f"The provided link is already in the list:\n\"{link}\""
            tk_messagebox.showerror("Already on List", error_message)
            print(error_message)
                     
        elif link and url_is_valid(link) and link not in self.urls_item_widget:
            url_item_widget = FileURLDownloader(
                self.listbox, 
                link,
                lambda: self.on_download_button_clicked(link))
            
            self.urls_item_widget[link] = url_item_widget
            
            url_item_widget.bind_events(self.master)
            
            print(f"Added URL: \"{link}\"")

        self.link_entry.delete(0, "end")
        self.listbox.update_idletasks()
    
    def on_download_button_clicked(self, url: str):
        download_thread = th.Thread(
            target=self.download_file, 
            args=(url, ), 
            name=f"download_file '{url}'",
            daemon=True
            )
        
        download_thread.start()
    
    def download_file(self, url: str):
        self.event_generate(f"<<{url} lock>>")
        print(f"Downloading URL: {url}")
        
        success = self._request_file(url)
        
        if success:
            self.event_generate(f"<<{url} success>>")
            print(f"Download successful: {url}")
            
        else:
            self.event_generate(f"<<{url} fail>>")
            print(f"Download failed: {url}")
        
    def _request_file(self, url: str) -> bool:
        subfolder = "sfd"
        with seasson.get(url, stream=True, allow_redirects=True) as response:
            filename = url_get_filename(response.url)
            destination_dir = osp_abspath(f"{osp_expanduser("~")}/Downloads/{subfolder}")
            
            is_response_ok = response.ok
            total_size = int(response.headers.get("content-length", 0))
            
            is_ok_to_download = is_response_ok and total_size > 0
            
            if is_ok_to_download:
                os_makedirs(destination_dir, exist_ok=True)
                file_destination = f"{destination_dir}/{filename}"
                
                i = 1
                base_filename, extension = osp_splitext(filename)
                while osp_isfile(file_destination):
                    file_destination = f"{destination_dir}/{base_filename} ({i}){extension}"
                    i += 1
                    
                with open(file_destination, "wb") as file:
                    downloaded_size = 0
                    
                    for chunk in response.iter_content(chunk_size=1000): # 8192
                        file.write(chunk)
                        downloaded_size += len(chunk)
                        progress_percentage = downloaded_size / total_size
                        
                        self.urls_item_widget.get(url).progress_value = progress_percentage
                        self.event_generate(f"<<{url} progress>>")
                        
                        print(f"[{round(progress_percentage*100, 2)}% | {downloaded_size} / {total_size}] {url}")
            
            return is_ok_to_download
        