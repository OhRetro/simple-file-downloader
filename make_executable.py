from os import system
#from subprocess import run as sp_run

def make_executable(version: str):
    options = [
        "--standalone",
        "--onefile",
        "--follow-imports",
        "--disable-console",
        #"--quiet",
        "--assume-yes-for-downloads",
        "--output-dir=build/",
        f"--output-filename=SimpleFileDownloader",
        # #"--windows-icon-from-ico=logo.ico",
        "--enable-plugin=tk-inter"
    ]

    _options = " ".join(options)
    system(f"nuitka {_options} main.py")
    #sp_run(f"nuitka {_options} main.py", check=True)

if __name__ == "__main__":
    make_executable("1.0.0")
    