# How to make charts

Right now, there is no editor (even though I could very much add one) so everything has to be done by hand, so let's dissect a chart folder, shall we?

------

First up, you need to create a folder (*named literally whatever you want*), then create a file called `data.json` in that folder.<br/>
You can then add the sound file in that folder! (Can be any sound file format, mp3, ogg, etc...)

And then, here's what your `data.json` file should look like:
```json
{
    "sound": "sound.ogg",
    "bpm": 112,
    "offset": -0.0110,
    "metadata": {
        "title": "Title",
        "author": "Author",
        "charter": "You",
        "description": "A very interesting description!"
    },
    "notes": [
        { 
            "type": "hit_object", 
            "beatpos": [0, 1],       
            "key": 0, 
            "screenpos": [0,0],     
            "color": 1 
        },
    ]
}
```

Quite a lot, isn't it? Let's look at each part individually.

## JSON Surface Content:

### - `"sound"`

Type: `String`
- Should be the entire path of the file relative to data.json (So, if it's in the same folder, just the file name.)


### - `"bpm"`

Type: `Float`/`Int`
- The BPM of the song.
- ⚠ Currently, BPM Changing mid-song is not supported, but will in a future update. (Or you can just implement it yourself by making a PR!... Sorry if that sounded rude...)

### - `"offset"`

Type: `Float`/`Int`
- The offset of the song, in seconds.
- Press 4 during gameplay to turn on the metronome.

### - `"metadata"`

Type: `Dict`
- In order to describe each entry individually, I will open a new section:

## JSON Chart Metadata:

### - `"title"`

Type: `String`
- The actual title of the song.

### - `"author"`

Type: `String` 
- The song author's pseudonym.

### - `"charter"`

Type: `String` (obviously)
- That's you! Use your preferred pseudonym.

## JSON Notes Data:

Each note needs to be put in `"notes"` (Type: `Array`), inside of another `Dict`. Here's what you can change:

### - Note type
- The type of object this note is. There are two different note types with different values to type in.<br/>
Here's a sheet displaying all currently available types:

|Note's `"type"`|Version|Description|
|--|--|--|
|`"hit_object"`|0.1|The average note. Displays a key, and all the junk around it.|
|`"end"`|0.1|Allows you to end the level at the defined position.|

### Hit objects
Hit objects are very cool! Here's what they look like in-game:
```
╔═╗ <- Can have different colors
║H║ <- Can be any of the usable keyboard keys
╚3╝ <- When this reaches 0, tap the key!
```

And here's each of their propreties:

#### - `"beatpos"`

Type: `Array` of two items: an `Int` (`0`) and a `Float` (`1`)
- Basically, when you have to hit the note in the song.
- It's in the format `[Measure (Int), Beat (Float)]`
- The song starts at `[0, 1]`, and each measure is `4` beats long (this will be changed in a future update, but 4 will stay the default)

#### - `"key"`

Type: `Int` (between `0` and `29`)
- The key you need to hit. It's not a character, because there's multiple different layouts existing.
- Here's a quick tip on how to find what key to use:
    - Look at your keyboard
    - Look at the key you wanna use
    - Check how far it is from the top left used key. (Q for QWERTY, A for AZERTY, etc...)
    - Then write the Int as YX, Y being how much you have to go down, and X how much you have to go to the right
    - So it looks something like this for every key:<br/>
    ```
    ┌──┬──┬──┬──┬──┬──┬──┬──┬──┬──┐
    |00|01|02|03|04|05|06|07|08|09|
    ├──┼──┼──┼──┼──┼──┼──┼──┼──┼──┤
    |10|11|12|13|14|15|16|17|18|19|
    ├──┼──┼──┼──┼──┼──┼──┼──┼──┼──┤
    |20|21|22|23|24|25|26|27|28|29|
    └──┴──┴──┴──┴──┴──┴──┴──┴──┴──┘
    ```

#### - `"screenpos"`

Type: `Array` containing two `Float`s (between `0` and `1`)
- The position of the note on the playfield. Varies depending on terminal size.
- Putting something out of the 0-1 range has a high chance of crashing the game on play. **Don't**.
- It's in format `[X, Y]` this time.

#### - `"color"`

Type `Int` (between `0` and... I think `6`)

- This will only change the color of the outline, the number and key will stay the same.
- Current known colors:

|`"color"`|Outputted color|
|:-------:|---------------|
|    0    |White                                        |
|    1    |<span style="color:red">Red</span>           |
|    2    |<span style="color:green">Green</span>       |
|    3    |<span style="color:yellow">Yellow</span>     |
|    4    |<span style="color:blue">Blue</span>         |
|    5    |<span style="color:magenta">Magenta</span>   |
|    6    |<span style="color:cyan">Cyan</span>         |

### - End level object

An end level object allows you to tell the game "Hey, here's the end of my chart, there's nothing past that point" and the game will say "alright sure", without actually knowing if you're telling the truth or no.
#### - `"beatpos"`
Type: `Array` of two items: an `Int` (`0`) and a `Float` (`1`)
- The position at which the chart will stop.
- It's in the format `[Measure (Int), Beat (Float)]`
- The song starts at `[0, 1]`, and each measure is `4` beats long (this will be changed in a future update, but 4 will stay the default)

## Ascii Icon

Once your chart is over, you can add a little Ascii art of your choice (don't make it too big!) in a file named `icon.txt`.<br/>
Here's an example:
```
PLACEHOLDER
ERPLACEHOLD
LDERPLACEHO
HOLDERPLACE
CEHOLDERPLA
```
That is quite literally the placeholder icon. :D<br/>
~~colors coming soon~~