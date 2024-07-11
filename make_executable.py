from os import system as os_system
from platform import system as pf_system
from main import __version__

def include_data_dir(dir: str) -> str:
    return f"--include-data-dir={dir}={dir}"

def program_icon(filename: str, win_filename: str = None) -> str:
    match pf_system():
        case "Windows":
            win_filename = win_filename or filename
            return f"--windows-icon-from-ico={win_filename}"
        
        case "Linux":
            return f"--linux-icon={filename}"
        
        # I will never know how it runs there
        case "Darwin":
            return f"--macos-app-icon={filename}"
        
        case _:
            raise SystemError("Unsupported system")


def make_executable(version: str):
    options = (
        # General
        "--standalone",
        "--onefile",
        # "--quiet",
        "--assume-yes-for-downloads",
        "--windows-console-mode=attach",
        
        # Plugins
        "--enable-plugin=tk-inter",
        
        # Files
        include_data_dir("assets"),
        
        # Output
        "--output-dir=build/",
        f"--output-filename=SimpleFileDownloader_v{version}",
        
        # Program File Information
        "--company-name=OhRetro",
        "--product-name=SimpleFileDownloader",
        f"--product-version={version}",
        f"--file-version={version}",
        
        # Program Icon
        program_icon("assets/icon.png", "assets/icon.ico"),
    )

    _options = " ".join(options)
    
    # subprocess.run() raises an exception
    os_system(f"nuitka {_options} main.py")

if __name__ == "__main__":
    make_executable(__version__)
    