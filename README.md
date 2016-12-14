Anastasis
=========
Archimandrite Ephrem (Lash) was well known for his translations of Orthodox liturgical and patristic texts. 
With his passing (may his memory be eternal!), easy access to his translations was lost. I have attempted to begin
a correspondence with the appropriate people in order to make sure this repository is permitted, but am making 
these texts available here in the interim.

Please begin with [Archimandrite Ephrem's Index](files/index.md).

Converting
==========
I have written a simple Python script to convert Archimandrite Ephrem's
original HTML (which seems to have been generated by Microsoft Frontpage) into
Markdown. On a Mac, you must have Python 3, Virtualenv, and
[Pandoc](http://pandoc.org/) installed to run the script. Most of these things
can be installed with [Homebrew](http://brew.sh/).:

    virtualenv -p python3 ve
    . ve/bin/activate
    pip install -r requirements.txt

Once you have this done, you should be able to run the script as follows:

    python cleanup.py

The script will convert the files in the 'original' directory to new markdown
files in the 'files' directory.
