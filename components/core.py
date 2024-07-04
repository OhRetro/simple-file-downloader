import requests
import customtkinter as ctk
from asyncio import run as asyncio_run
from tkinter import messagebox as tk_messagebox
from os import makedirs as os_makedirs
from os.path import abspath as osp_abspath, expanduser as osp_expanduser
from .url import url_is_valid, url_get_filename

widgets_dict = dict[str, ctk.CTkBaseClass]

class FileDownloader(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.create_widgets()

    def create_widgets(self):
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
        self.listbox = ctk.CTkFrame(self)
        self.listbox.pack(fill="both", expand=True, padx=10, pady=10)
        
    def add_item(self):
        link = self.link_entry.get()
        
        if link and url_is_valid(link):
            widgets: widgets_dict = {}
            
            # Limit text so items don't go out of the window
            max_chars = 30
            display_link = link[:max_chars] + "..." if len(link) > max_chars else link
            
            # Frame
            item_frame = ctk.CTkFrame(self.listbox, corner_radius=5)
            item_frame.pack(fill="x", padx=5, pady=5)
            
            # URL Label
            link_label = ctk.CTkLabel(item_frame, text=display_link)
            link_label.pack(side="left", padx=5, pady=5)
            
            # Delete button
            delete_button = ctk.CTkButton(item_frame, 
                                          10, 10, 
                                          text="X", fg_color="red", hover_color="#8B0000", 
                                          command=lambda frame=item_frame: frame.destroy())
            delete_button.pack(side="right", padx=5)
            
            # Download button
            download_button = ctk.CTkButton(item_frame, 
                                            height=17, text="Download", text_color_disabled="white", 
                                            command=lambda: self.download_file(link, widgets))
            download_button.pack(side="right", padx=5, pady=5)

            # Status label
            status_label = ctk.CTkLabel(item_frame, text="Status: READY")
            status_label.pack(side="right", padx=5)
            
            # Progress bar
            progress_bar = ctk.CTkProgressBar(item_frame, 125, progress_color="#4a4d50")
            progress_bar.pack(side="right", padx=5)
            progress_bar.set(0)
            
            widgets["status_label"] = status_label
            widgets["progress_bar"] = progress_bar
            widgets["download_button"] = download_button
            widgets["delete_button"] = delete_button
            
        elif link and not url_is_valid(link):
            error_message = f"The provided link is not a valid URL:\n\"{link}\"\nPlease enter a valid URL."
            tk_messagebox.showerror("Invalid URL", error_message)

        self.link_entry.delete(0, "end")
        self.listbox.update_idletasks()
            
    def download_file(self, url: str, widgets: widgets_dict):
        progress_bar: ctk.CTkProgressBar = widgets.get("progress_bar")
        download_button: ctk.CTkButton = widgets.get("download_button")
        delete_button: ctk.CTkButton = widgets.get("delete_button")

        progress_bar.configure(progress_color="#1f6aa5")
        download_button.configure(state="disabled")
        delete_button.configure(state="disabled")
        
        success = asyncio_run(self._request_file(url, widgets))
        
        if success:
            progress_bar.configure(progress_color="green")
            download_button.configure(text="Completed!")
            delete_button.configure(state="normal")
        else:
            progress_bar.configure(progress_color="red")
            download_button.configure(text="Failed", state="normal")
            delete_button.configure(state="normal")
        
    async def _request_file(self, url: str, widgets: widgets_dict) -> bool:
        status_label: ctk.CTkLabel = widgets.get("status_label")
        progress_bar: ctk.CTkProgressBar = widgets.get("progress_bar")
        
        headers = {"User-Agent": "Mozilla/5.0"}
        
        with requests.get(url, stream=True, headers=headers, allow_redirects=True) as response:
            filename = url_get_filename(response.url)
            destination_dir = osp_abspath(f"{osp_expanduser("~")}/Downloads") # /SimpleFileDownloader
            
            is_response_ok = response.ok
            status_label.configure(text=f"Status: {'OK' if is_response_ok else 'FAIL'}")
            
            if is_response_ok:
                os_makedirs(destination_dir, exist_ok=True)
                with open(f"{destination_dir}/{filename}", "wb") as file:
                    total_size = int(response.headers.get("content-length", 0))
                    downloaded_size = 0
                    
                    for chunk in response.iter_content(chunk_size=8192):
                        file.write(chunk)
                        downloaded_size += len(chunk)
                        progress_percentage = downloaded_size / total_size
                        progress_bar.set(progress_percentage)
                        self.update()
            
            return is_response_ok
        