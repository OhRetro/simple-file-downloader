from os import system
from main import __version__
#from subprocess import run as sp_run

def make_executable(version: str):
    options = [
        "--standalone",
        "--onefile",
        "--follow-imports",
        "--windows-console-mode=disable",
        #"--quiet",
        "--assume-yes-for-downloads",
        "--output-dir=build/",
        f"--output-filename=SimpleFileDownloader_v{version}",
        "--enable-plugin=tk-inter",
        "--product-name=SimpleFileDownloader",
        f"--product-version={version}",
        f"--file-version={version}",
        "--windows-icon-from-ico=icon.ico",
    ]

    _options = " ".join(options)
    system(f"nuitka {_options} main.py")
    #sp_run(f"nuitka {_options} main.py", check=True)

if __name__ == "__main__":
    make_executable(__version__)
    