import requests
import customtkinter as ctk
from ua_generator import generate as ua_generate
from tkinter import messagebox as tk_messagebox
from os import makedirs as os_makedirs
from os.path import (abspath as osp_abspath, 
                     expanduser as osp_expanduser, 
                     isfile as osp_isfile, 
                     splitext as osp_splitext)
from .url import url_is_valid, url_get_filename

from random import randint

widgets_dict = dict[str, ctk.CTkBaseClass]

ua = ua_generate()
seasson = requests.Session()
seasson.headers.update(ua.headers.get())

print(f"Generated UA: {ua}")

class FileDownloader(ctk.CTkFrame):
    def __init__(self, parent: ctk.CTk):
        super().__init__(parent)
        self.urls_item_frame: dict[str, widgets_dict] = {}
        self.urls_success: list[str] = []
        self.setup_gui()
        
        self.add_url_examples()
        
    def add_url_examples(self, quantity: int = 3):
        for _ in range(quantity):
            x = randint(100, 300)
            y = randint(100, 300)
            self.link_entry.insert(0, f"https://picsum.photos/{x}/{y}")
            self.add_item()
            
        self.link_entry.insert(0, "https://www.youtube.com/watch?v=8wX1uEp2Jhs")
        self.add_item()

    def setup_gui(self):
        # Main frame
        entry_frame = ctk.CTkFrame(self)
        entry_frame.pack(fill="x", padx=10, pady=10)

        # Link input box
        self.link_entry = ctk.CTkEntry(entry_frame, placeholder_text="Enter file URL link")
        self.link_entry.pack(side="left", fill="x", expand=True, padx=5)

        # Add button
        self.add_button = ctk.CTkButton(entry_frame, text="Add", command=self.add_item)
        self.add_button.pack(side="left", padx=5, pady=5)

        # Listbox for urls
        self.listbox = ctk.CTkScrollableFrame(self, label_text="URLs list")
        self.listbox.pack(fill="both", expand=True, padx=10, pady=10)
        
        print("GUI Created!")
    
    def delete_item(self, name: str):
        if name in self.urls_item_frame:
            self.urls_item_frame[name]["main_frame"].destroy()
            del self.urls_item_frame[name]
            print(f"Deleted URL: {name}")
        
        if name in self.urls_success:
            self.urls_success.remove(name)
    
    def add_item(self):
        link = self.link_entry.get()

        if link and not url_is_valid(link):
            error_message = f"The provided link is not a valid URL:\n\"{link}\"\nPlease enter a valid URL."
            tk_messagebox.showerror("Invalid URL", error_message)
            print(error_message)

        elif link and url_is_valid(link) and link in self.urls_item_frame:
            error_message = f"The provided link is already in the list:\n\"{link}\""
            tk_messagebox.showerror("Already on List", error_message)
            print(error_message)
                     
        elif link and url_is_valid(link) and link not in self.urls_item_frame:
            widgets: widgets_dict = {}
            
            # Limit text so items don't go out of the window
            max_chars = 30
            display_link = link[:max_chars] + "..." if len(link) > max_chars else link
            
            item_frame = ctk.CTkFrame(self.listbox, corner_radius=5)
            item_frame.pack(fill="x", padx=5, pady=5)
            
            link_label = ctk.CTkLabel(item_frame, text=display_link)
            link_label.pack(side="left", padx=5, pady=5)

            item_subframe = ctk.CTkFrame(item_frame, corner_radius=5)
            item_subframe.pack(side="right", padx=5, pady=5)
            
            delete_button = ctk.CTkButton(item_subframe, 
                                          10, 10, 
                                          text="X", fg_color="red", hover_color="darkred", 
                                          command=lambda: self.delete_item(link))
            delete_button.pack(side="right", padx=5)
            
            download_button = ctk.CTkButton(item_subframe, 
                                            height=17, text="Download", text_color_disabled="white", 
                                            command=lambda: self.download_file(link))
            download_button.pack(side="right", padx=5, pady=5)

            progress_bar = ctk.CTkProgressBar(item_subframe, 125, progress_color="#4a4d50")
            progress_bar.pack(side="right", padx=5)
            progress_bar.set(0)
            
            widgets["main_frame"] = item_frame
            widgets["progress_bar"] = progress_bar
            widgets["download_button"] = download_button
            widgets["delete_button"] = delete_button
            
            self.urls_item_frame[link] = widgets
            
            print(f"Added URL: \"{link}\"")

        self.link_entry.delete(0, "end")
        self.listbox.update_idletasks()
    
    def get_gui_element(self, url: str, name: str):
        return self.urls_item_frame.get(url).get(name)
    
    def download_file(self, url: str):
        progress_bar: ctk.CTkProgressBar = self.get_gui_element(url, "progress_bar")
        download_button: ctk.CTkButton = self.get_gui_element(url, "download_button")
        delete_button: ctk.CTkButton = self.get_gui_element(url, "delete_button")

        progress_bar.configure(progress_color="#1f6aa5")
        download_button.configure(state="disabled")
        delete_button.configure(state="disabled")
        
        print(f"Downloading URL: {url}")
        success = self._request_file(url)
        
        if success:
            progress_bar.configure(progress_color="green")
            download_button.configure(text="Completed!")
            delete_button.configure(state="normal")
            
            print(f"Download successful: {url}")
            
        else:
            progress_bar.configure(progress_color="red")
            download_button.configure(text="Retry?", state="normal")
            delete_button.configure(state="normal")
            
            print(f"Download failed: {url}")
        
    def _request_file(self, url: str) -> bool:
        progress_bar: ctk.CTkProgressBar = self.get_gui_element(url, "progress_bar")
        
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
                    
                    for chunk in response.iter_content(chunk_size=8192):
                        file.write(chunk)
                        downloaded_size += len(chunk)
                        progress_percentage = downloaded_size / total_size
                        progress_bar.set(progress_percentage)
                        
                        print(f"[{round(progress_percentage*100, 2)}% | {downloaded_size} / {total_size}] {url}")
                        
                    self.urls_success.append(url)
            
            return is_ok_to_download
        