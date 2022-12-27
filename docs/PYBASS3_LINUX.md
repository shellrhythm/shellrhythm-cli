# PyBASS3 on Linux compatibility

If you're a Linux user, you may have noticed that you cannot actually start the game. This is due to pybass3 not fully supporting Linux yet. 
However, I have found a workaround to get it to work anyways, so let's get into it!

## What you'll need

- An internet connection
- The [BASS library](https://www.un4seen.com/download.php?bass24-linux) (note, this is a direct download link. This is their official website, if you need.)
- Its [tags](https://www.un4seen.com/download.php?z/3/tags18-linux)

## Step 1: In shellrhythm

In the libbass zip file, get to the `/libs/x86-64/` (or maybe `/libs/x86/`, depending on what you're running) folder, and grab the `libbass.so file`, then put it in the root of the shellrhythm files.

## Step 2: In the module's folder

The module's folder is most of the time `~/.local/lib/[whatever your python version is]/site-packages/pybass3/`.
Once in here, go to `/vendor/` and put in it from the library zip `./libs/x86(-64)/libbass.so` and from the tags zip `./libs/x86(-64)/libtags.so`, and rename that last file to `tags.so`.

--------

If you did everything as mentioned, you should be good. If you still can't launch the game/there are imprecisions in that tutorial, open an issue!