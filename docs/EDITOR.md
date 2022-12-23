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
|A/D|Previous/Next bar|
|Z|New note at position|
|H/J/K/L|Move selected note left/down/up/right|
|:|Command mode|
|E|Set key of note|

## Command mode

"Huh? Command mode? What's that?" <br>
So, first up, remember vim? *...wait where did everybody go-*<br>
Jokes aside, this editor has inspirations from vim, as in you can type different commands to achieve different things. Here are some basic examples:

```
:q              -> Quits the editor, if you're way too scared to try this out.
:w              -> Saves the file (will prompt you to select where you want to save it if it's a new file)
:w <filename>   -> Same deal, except it saves it in this specific file
:wq             -> Combinaison of :w and :q
:p              -> Places a tile at current position (will prompt you for a key)
:p <KeyNum>     -> Places a tile at current position (with a defined key)
:o <foldername> -> Opens a chart
```