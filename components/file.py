from os.path import (join as osp_join, 
                     dirname as osp_dirname,
                     abspath as osp_abspath)

# Function to get the absolute file path.
# This is particularly useful for getting files with Nuitka 
# when using the --onefile and the --include-* options.
# More information here: https://nuitka.net/user-documentation/common-issue-solutions.html#onefile-finding-files
def get_filepath(filename: str):
    directory = osp_dirname(osp_dirname(osp_abspath(__file__)))
    return osp_join(directory, filename)
