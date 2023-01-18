# shellrhythm's editor

## Introduction

You know this editor's gonna be crazy when I have to write full documentation on it :notlikethis:

Jokes aside, let me introduce you to the basic controls of the editor.
|Key|Action|
|←/→|Move on the timeline|
|↑/↓|Goto previous/next note|
|Space|Preview from position|
|Ctrl+Space|Preview from beginning|
|T|Metronome On/Off|
|Z|New note at position|
|Shift+Z|Set end note position|
|H/J/K/L|Move selected note left/down/up/right|
|U/I|Move selected note earlier/later|
|:|Command mode|
|E|Note options|
|Escape|Change metadata settings|

## Command mode

"Huh? Command mode? What's that?" <br>
So, first up, remember vim? *...wait where did everybody go-*<br>
Jokes aside, this editor has inspirations from vim, as in you can type different commands to achieve different things. Here are some basic examples:

```
:q                  -> Quits the editor, if you're way too scared to try this out.
:w                  -> Saves the file (will prompt you to select where you want to save it if it's a new file)
:w <filename>       -> Same deal, except it saves it in this specific file
:wq                 -> Combinaison of :w and :q
:p                  -> Places a tile at current position (will prompt you for a key)
:p <KeyNum>         -> Places a tile at current position (with a defined key)
:o <foldername>     -> Opens a chart
:m <Beats>          -> Moves cursor by specified amount of beats
:song               -> Opens the window dialog to search for a song
:off                -> Sets offset (will open the song calibration menu)
:mt <param> <value> -> Changes metadata
:bpm <bpm>          -> Changes the song's BPM
:s <snap>           -> Changes snapping to a specific value
:cp <range> <by>    -> Copies note range (min-max) by defined number of beats
```

Something cool about this command mode is that you can chain multiple commands at once using `;;`<br>
So, for example, `:o test_chart;;m 5.5;;p 4;;w test_chart_2;;q` will open a chart in the folder `./charts/test_chart/`, move by 5.5 beats (so by default 1 bar and 1.5 beats), places a 4 (which, with QWERTY layout, corresponds to a `R`) at this position, and then saves it to a new folder, `./charts/test_chart_2/`, before closing everything. Yeah, that's a lot to take in...