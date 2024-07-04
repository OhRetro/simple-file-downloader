from typing import Callable
import customtkinter as ctk

class FileURLDownloader(ctk.CTkFrame):
    def __init__(self, parent: ctk.CTkBaseClass, url: str, download_func: Callable):
        super().__init__(parent, corner_radius=5)
        self.pack(fill="x", padx=5, pady=5)
        
        # Limit text so items don't go out of the window
        max_chars = 30
        url_display = url[:max_chars] + "..." if len(url) > max_chars else url
        
        self.url = url
        self.progress_value: float = 0
        
        self.url_label = ctk.CTkLabel(self, text=url_display)
        self.url_label.pack(side="left", padx=5, pady=5)

        self.control_frame = ctk.CTkFrame(self, corner_radius=5)
        self.control_frame.pack(side="right", padx=5, pady=5)
        
        self.delete_button = ctk.CTkButton(self.control_frame, 
                                        10, 10, 
                                        text="X", fg_color="red", hover_color="darkred", 
                                        command=self.destroy)
        self.delete_button.pack(side="right", padx=5)
        
        self.download_button = ctk.CTkButton(self.control_frame, 
                                        height=17, text="Download", text_color_disabled="white", 
                                        command=download_func)
        self.download_button.pack(side="right", padx=5, pady=5)

        self.progress_bar = ctk.CTkProgressBar(self.control_frame, 125, progress_color="#4a4d50")
        self.progress_bar.pack(side="right", padx=5)
        self.progress_bar.set(0)
    
    def bind_events(self, root: ctk.CTk):
        root.bind(f"<<{self.url} lock>>", self._lock_state)
        root.bind(f"<<{self.url} fail>>", self._fail_state)
        root.bind(f"<<{self.url} success>>", self._success_state)
        root.bind(f"<<{self.url} progress>>", self._progress_update)
    
    def _lock_state(self, _):
        self.progress_bar.configure(progress_color="#1f6aa5")
        self.download_button.configure(state="disabled")
        self.delete_button.configure(state="disabled")

    def _fail_state(self, _):
        self.progress_bar.configure(progress_color="red")
        self.download_button.configure(text="Retry?", state="normal")
        self.delete_button.configure(state="normal")
        
    def _success_state(self, _):
        self.progress_bar.configure(progress_color="green")
        self.download_button.configure(text="Completed!")
        self.delete_button.configure(state="normal")
    
    def _progress_update(self, _):
        self.update_progress(self.progress_value)
    
    def update_progress(self, progress: float):
        self.progress_bar.set(progress)

        