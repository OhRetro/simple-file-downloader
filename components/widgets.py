import customtkinter as ctk
from typing import TYPE_CHECKING, TypeVar
from requests import Session
from threading import Thread
from ua_generator import generate as ua_generate
from os import makedirs as os_makedirs
from os.path import (abspath as osp_abspath, 
                     expanduser as osp_expanduser, 
                     isfile as osp_isfile, 
                     splitext as osp_splitext)
from .url import url_get_filename, get_filename_from_content_disposition
from .log import log

if TYPE_CHECKING:
    from .wrapper import Wrapper
else:
    Wrapper = TypeVar("Wrapper")

ua = ua_generate()
session = Session()
session.headers.update(ua.headers.get())

log(f"Generated UA: {ua}")

class FileURLDownloaderWidget(ctk.CTkFrame):
    def __init__(self, parent: ctk.CTkBaseClass, url: str):
        super().__init__(parent, corner_radius=5)
        self.pack(fill="x", padx=5, pady=5)
        self.setup_widgets(url)
        
        self.url = url
        self.progress_value: float = 0
        self.download_thread: Thread = None
        self.downloading = False
        self.download_success = False
        self.true_parent: Wrapper = None
        
    def setup_widgets(self, url: str):
        self.url_textbox = ctk.CTkTextbox(self, 250, height=5, activate_scrollbars=False, wrap="none")
        self.url_textbox.pack(side="left", padx=5, pady=5)
        self.url_textbox.insert("0.0", url)
        self.url_textbox.configure(state="disabled")

        self.control_frame = ctk.CTkFrame(self, height=5, corner_radius=5)
        self.control_frame.pack(side="right", padx=5, pady=5)
        
        self.remove_button = ctk.CTkButton(self.control_frame, 
                                        10, 10, 
                                        text="X", fg_color="red", hover_color="darkred", 
                                        command=self.destroy)
        self.remove_button.pack(side="right", padx=5)
        
        self.download_button = ctk.CTkButton(self.control_frame, 
                                        text="Download", text_color_disabled="white", 
                                        command=self._start_download_thread)
        self.download_button.pack(side="right", padx=5, pady=5)
        
        self.percent_label = ctk.CTkLabel(self.control_frame, text="0%")
        self.percent_label.pack(side="right", padx=5, pady=5)

        self.progress_bar = ctk.CTkProgressBar(self.control_frame, 125, progress_color="#4a4d50")
        self.progress_bar.pack(side="left", padx=5)
        self.progress_bar.set(0)

    def destroy(self):
        log(f"Destroying File Downloader: {self.url}")
        
        if self.true_parent:
            del self.true_parent.downloader_widgets[self.url]
            
        super().destroy()

    def bind_events(self, root: ctk.CTk):
        root.bind(f"<<{self.url} lock>>", self._lock_state)
        root.bind(f"<<{self.url} fail>>", self._fail_state)
        root.bind(f"<<{self.url} success>>", self._success_state)
        root.bind(f"<<{self.url} progress>>", self._progress_update)
    
    def _create_download_thread(self):
        log(f"Creating download thread: {self.url}")
        return Thread(
            target=self._download_file, 
            name=f"FileURLDownload @ {self.url}",
            daemon=True
        )
    
    def _start_download_thread(self):
        self.download_thread = self._create_download_thread()
        log(f"Starting download thread: {self.url}")
        self.download_thread.start()
    
    def _lock_state(self, _):
        self.progress_bar.configure(progress_color="#1f6aa5")
        self.download_button.configure(text="Downloading", fg_color="#4a4d50", state="disabled")
        self.remove_button.configure(fg_color="darkred", state="disabled")
        # self.update()

    def _fail_state(self, _):
        self.progress_bar.configure(progress_color="red")
        self.download_button.configure(text="Failed. Retry?", fg_color="red", hover_color="darkred", state="normal")
        self.remove_button.configure(fg_color="red", state="normal")
        # self.update()
        
    def _success_state(self, _):
        self.progress_bar.configure(progress_color="green")
        self.download_button.configure(text="Completed!", fg_color="green")
        self.remove_button.configure(fg_color="red", state="normal")
        # self.update()
    
    def _progress_update(self, _):
        self.progress_bar.set(self.progress_value)
        self.percent_label.configure(text=f"{round(self.progress_value * 100)}%")
        # self.update()

    def _download_file(self):
        self.downloading = True
        self.event_generate(f"<<{self.url} lock>>")
        log(f"Downloading URL: {self.url}")
        
        success = self._request_file()
        
        if success:
            self.event_generate(f"<<{self.url} success>>")
            log(f"Download successful: {self.url}")
            
        else:
            self.event_generate(f"<<{self.url} fail>>")
            log(f"Download failed: {self.url}")
            
        self.downloading =  False
        
    def _request_file(self) -> bool:
        subfolder = "sfd"
        with session.get(self.url, stream=True, allow_redirects=True) as response:
            content_disposition: str = response.headers.get("content-disposition", None)
            
            filename = get_filename_from_content_disposition(content_disposition) or url_get_filename(response.url)
            destination_dir = osp_abspath(f"{osp_expanduser('~')}/Downloads/{subfolder}")
            
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
                    
                with open(file_destination, "ab") as file:
                    downloaded_size = 0
                    
                    for chunk in response.iter_content(chunk_size=8192): # chunk_size=8192
                        if chunk:
                            file.write(chunk)
                            downloaded_size += len(chunk)
                            progress_percentage = downloaded_size / total_size
                            
                            self.progress_value = progress_percentage
                            self.event_generate(f"<<{self.url} progress>>")
                            
                            log(f"[{round(progress_percentage * 100, 2)}% | {downloaded_size} / {total_size}] {self.url}")
                            
                    self.download_success = True
                    log(f"File saved as \"{file_destination}\"")
            
            return is_ok_to_download
        