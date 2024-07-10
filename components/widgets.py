import customtkinter as ctk
from requests import Session
from typing import TYPE_CHECKING, TypeVar
from threading import Thread
from os import makedirs as os_makedirs
from os.path import (abspath as osp_abspath, 
                     expanduser as osp_expanduser, 
                     isfile as osp_isfile, 
                     splitext as osp_splitext)
from math import floor
from .url import url_get_filename, get_filename_from_content_disposition
from .log import log, log_exception
from .env import get_env_var

if TYPE_CHECKING:
    from .wrapper import Wrapper
else:
    Wrapper = TypeVar("Wrapper")

class FileURLDownloaderWidget(ctk.CTkFrame):
    def __init__(self, parent: ctk.CTkBaseClass, url: str, session: Session, **kwargs):
        super().__init__(parent, corner_radius=5)
        self.pack(fill="x", padx=5, pady=5)
        self.setup_widgets(url)
        
        self.url = url
        self.progress_value: float = 0
        self.download_thread: Thread = None
        self.download_success = False
        self.download_size_reported = False
        self.downloading = False
        self.session = session
        self.true_parent: Wrapper = kwargs.get("true_parent", None)
        
    def setup_widgets(self, url: str):
        self.url_textbox = ctk.CTkTextbox(self, 250, height=5, activate_scrollbars=False, wrap="none")
        self.url_textbox.pack(side="left", padx=5, pady=5, fill="x")
        self.url_textbox.insert("0.0", url)
        self.url_textbox.configure(state="disabled")

        self.control_frame = ctk.CTkFrame(self, height=5, corner_radius=5)
        self.control_frame.pack(side="right", padx=5, pady=5, fill="x", expand=True)

        self.progress_bar = ctk.CTkProgressBar(self.control_frame, 125, progress_color="#4a4d50")
        self.progress_bar.pack(side="left", padx=5)
        self.progress_bar.set(0)
             
        self.remove_button = ctk.CTkButton(self.control_frame, 
                                        10, 10, 
                                        text="X", fg_color="red", hover_color="darkred", 
                                        command=self.remove)
        self.remove_button.pack(side="right", padx=5)
        
        self.download_button = ctk.CTkButton(self.control_frame,
                                        text="Download", text_color_disabled="white", 
                                        command=self._start_download_thread)
        self.download_button.pack(side="right", padx=5, pady=5)
        
        self.percent_label = ctk.CTkLabel(self.control_frame, text="0%")
        self.percent_label.pack(side="right", padx=5, pady=5)

    def remove(self):
        log(f"Removing download task: {self.url}")
        self.destroy()
        
        if self.true_parent:
            del self.true_parent.downloader_widgets[self.url]
            self.true_parent.update()
            
    # def event_generate(self, *args, **kwargs):
    #     if self.test_env: return
    #     super().event_generate(*args, **kwargs)

    def bind_events(self, root: ctk.CTk):
        root.bind(f"<<{self.url} lock>>", self._lock_state)
        root.bind(f"<<{self.url} fail>>", self._fail_state)
        root.bind(f"<<{self.url} success>>", self._success_state)
        root.bind(f"<<{self.url} progress>>", self._progress_update)
    
    def _create_download_thread(self):
        log(f"Creating download thread: {self.url}")
        return Thread(
            target=self._download_file, 
            name=f"FileURLDownload @ \"{self.url}\"",
            daemon=True
        )
    
    def _start_download_thread(self):
        self.download_thread = self._create_download_thread()
        log(f"Starting download thread: {self.url}")
        self.download_thread.start()
    
    # I don't know if this is the right way to save resources
    def _clear_download_thread(self):
        self.download_thread = None
    
    def _lock_state(self, _):
        self.progress_bar.configure(progress_color="#1f6aa5")
        self.download_button.configure(text="Downloading", fg_color="#4a4d50", state="disabled")
        self.remove_button.configure(fg_color="darkred", state="disabled")
        self.update()

    def _fail_state(self, _):
        self.progress_bar.configure(progress_color="red")
        self.download_button.configure(text="Failed. Retry?", fg_color="red", hover_color="darkred", state="normal")
        self.remove_button.configure(fg_color="red", state="normal")
        self.update()
        
    def _success_state(self, _):
        self.progress_bar.configure(progress_color="green")
        self.download_button.configure(text="Completed!", fg_color="green")
        self.remove_button.configure(fg_color="red", state="normal")
        self.update()
    
    def _progress_update(self, _):
        if self.download_size_reported:
            self.progress_bar.set(self.progress_value)
            self.percent_label.configure(text=f"{floor(self.progress_value * 100)}%")
        else:
            self.percent_label.configure(text="???%")
            
        self.update()

    def _progress_indeterminate_start(self):
        self.progress_bar.configure(mode="indeterminate")
        self.progress_bar.start()
        self.update()

    def _progress_indeterminate_stop(self, success: bool):
        self.progress_bar.stop()
        self.progress_bar.configure(mode="determinate")
        if success:
            self.progress_bar.set(1)
            self.percent_label.configure(text="100%")
        else:
            self.progress_bar.set(0)
            self.percent_label.configure(text="???%")
        
        self.update()
                
    def _download_file(self):
        self.downloading = True
        self.event_generate(f"<<{self.url} lock>>")
        log(f"Downloading URL: {self.url}")
        
        try:
            self._request_file()
        except Exception as e:
            log_exception(e)
            
        if not self.download_size_reported:
            self._progress_indeterminate_stop(self.download_success)
        
        if self.download_success:
            self.event_generate(f"<<{self.url} success>>")
            log(f"Download successful: {self.url}")
            
        else:
            self.event_generate(f"<<{self.url} fail>>")
            log(f"Download failed: {self.url}")
        
        self.downloading =  False
        self._clear_download_thread()
        
    def _request_file(self):
        subfolder = "SimpleFileDownloader"
        destination_dir = osp_abspath(f"{osp_expanduser('~')}/Downloads/{subfolder}")
        LOG_PRINT_DOWNLOAD_PROGRESS = get_env_var("LOG_PRINT_DOWNLOAD_PROGRESS") == "true"
        
        with self.session.get(self.url, stream=True, allow_redirects=True) as response:
            content_disposition: str = response.headers.get("content-disposition", None)
            
            filename = get_filename_from_content_disposition(content_disposition) or url_get_filename(response.url)
            
            is_response_ok = response.ok
            total_size = int(response.headers.get("content-length", 0))
            self.download_size_reported = total_size > 0
            
            log(f"Response Status: {response.status_code}: {self.url}")
            
            if self.download_size_reported:
                log(f"Total size: {total_size}: {self.url}")
            else:
                log(f"Total size: UNKNOWN: {self.url}")
            
            if not is_response_ok: return
                
            os_makedirs(destination_dir, exist_ok=True)
            file_destination = f"{destination_dir}/{filename}"
            
            i = 1
            base_filename, extension = osp_splitext(filename)
            while osp_isfile(file_destination):
                file_destination = f"{destination_dir}/{base_filename} ({i}){extension}"
                i += 1
                
            with open(file_destination, "wb") as file:
                downloaded_size = 0
                
                if not self.download_size_reported:
                    self._progress_indeterminate_start()
                
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        file.write(chunk)
                        downloaded_size += len(chunk)
                        
                        if self.download_size_reported:
                            progress_percentage = downloaded_size / total_size
                            self.progress_value = progress_percentage
                            
                            if LOG_PRINT_DOWNLOAD_PROGRESS:
                                log(f"[{round(progress_percentage * 100, 2)}% | {downloaded_size} / {total_size}] {self.url}")
                        
                        elif not self.download_size_reported and LOG_PRINT_DOWNLOAD_PROGRESS:
                            log(f"[???% | {downloaded_size} / ???] {self.url}")
                        
                        self.event_generate(f"<<{self.url} progress>>")
                        
                self.download_success = True
                log(f"File saved as \"{file_destination}\"")
        