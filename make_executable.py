from os import system
from main import __version__

def make_executable(version: str):
    options = [
        "--standalone",
        "--onefile",
        "--follow-imports",
        "--windows-console-mode=attach",
        # "--quiet",
        "--assume-yes-for-downloads",
        "--lto=no",
        # "--show-memory",
        
        "--output-dir=build/",
        f"--output-filename=SimpleFileDownloader_v{version}",
        "--enable-plugin=tk-inter",
        
        "--product-name=SimpleFileDownloader",
        f"--product-version={version}",
        f"--file-version={version}",
        
        "--windows-icon-from-ico=icon.ico",
        #"--include-data-files=./icon.ico=icon.ico",
    ]

    _options = " ".join(options)
    system(f"nuitka {_options} main.py")

if __name__ == "__main__":
    make_executable(__version__)
    