# dupechecker

Check for and delete duplicate files from the command line.

## Installation

Install with:

<pre>
pip install dupechecker
</pre>



## Usage

<pre>
>dupechecker -h
usage: dupechecker [-h] [-r] [-d] [-ad] [-ns] [path]

positional arguments:
  path                The path to compare files in.

options:
  -h, --help          show this help message and exit
  -r, --recursive     Glob files to compare recursively.
  -d, --delete_dupes  After finding duplicates, delete all but one copy. For each set of duplicates, the tool will ask you to enter the number corresponding to the copy you want to keep.
                      Pressing 'enter' without entering a number will skip that set without deleting anything.
  -ad, --autodelete   Automatically decide which file to keep and which to delete from each set of duplicate files instead of asking which to keep.
  -ns, --no_show      Don't show printout of matching files.
</pre>
