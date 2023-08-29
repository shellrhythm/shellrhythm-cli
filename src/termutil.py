import os
import re
import time
import signal
import platform
import datetime
import logging
from blessed import Terminal
from term_image.image import from_file
from src.framebuffer import Framebuffer
from src.translate import LocaleManager

MINIMUM_WIDTH = 100
MINIMUM_HEIGHT = 32


if not os.path.exists("./logs/"):
    os.mkdir("./logs")

logging.basicConfig(
    filename="logs/app.log",
    filemode="w",
    format="%(asctime)s | [%(levelname)s]: %(message)s",
    level=logging.INFO
)

def log(message, level = 0):
    logging.log(level, message)

def strip_seqs(text):
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~]|\([0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)

box_styles = [
    "┌─┐││└─┘", #Base box
    ".-.||'-'", #Minimal box
    "*-*||*-*", #Pause box
    #Maybe add more styles later?
]

def prettydate(d, longFormat = False):
    cur_locale = LocaleManager().current_locale()
    diff = datetime.datetime.fromtimestamp(time.time()) - d
    if longFormat:
        output = d.strftime('%d %b %y, %H:%M:%S')
        if diff.days < 1:
            if diff.seconds <= 1:
                output = cur_locale("datetime.long.now")
            elif diff.seconds < 60:
                output = cur_locale("datetime.long.secs").format(int(diff.seconds))
            elif diff.seconds < 120:
                output = cur_locale("datetime.long.min1")
            elif diff.seconds < 3600:
                output = cur_locale("datetime.long.min").format(int(diff.seconds/60))
            elif diff.seconds < 7200:
                output = cur_locale("datetime.long.hour1")
            else:
                output = cur_locale("datetime.long.hour").format(int(diff.seconds/3600))
        elif diff.days < 2:
            output = cur_locale("datetime.long.ystd")
        elif diff.days < 30:
            output = cur_locale("datetime.long.day").format(int(diff.days))
    else:
        output = d.strftime('%d %b %y')
        if diff.days < 1:
            if diff.seconds <= 10:
                output = cur_locale("datetime.short.now")
            elif diff.seconds < 60:
                output = cur_locale("datetime.short.secs").format(int(diff.seconds))
            elif diff.seconds < 3600:
                output = cur_locale("datetime.short.mins").format(int(diff.seconds/60))
            else:
                output = cur_locale("datetime.short.hours").format(int(diff.seconds/3600))
        elif diff.days < 30:
            output = cur_locale("datetime.short.days").format(int(diff.days))
    return output


term = Terminal()
framebuffer = Framebuffer()


def prng (beat = 0.0, seed = 0, upperlimit = 2**32) -> int:
    """quick pseudorandomness don't mind me"""
    return int(beat * 216113 + 2531041 * (seed+1.3)/3.4) % upperlimit

def color_text(text = "", beat = 0.0):
    """Here, replace something like {cf XXXXXX} with the corresponding terminal color
    Combinaisons to support:
     - cf RRGGBB		Foreground color
     - cb RRGGBB		Background color
     - b				Bold text
     - i				Italic text
     - u				Underline text
     - n				Reverts text back to normal state
     - r				Flips foreground and background
     - k				Glitchifies text
    """
    text = text\
        .replace("\\\\","￼[")\
        .replace("\\{", "￼ø")\
        .replace("\\}", "ŧ￼")\
        .replace("{", "�{")\
        .replace("}", "}�")\
        .replace("￼[", "\\")
    #If you are using � or ￼ genuiunely, what the #### is wrong with you /gen
    data = text.split("�")
    rendered_text = ""
    glitchify_next = False
    for i in data:
        if i.startswith("{") and i.endswith("}"):
            command = i.strip("{}")
            if command.startswith("cf"):
                col = color_code_from_hex(command.replace("cf", "", 1).replace(" ", ""))
                rendered_text += term.color_rgb(col[0], col[1], col[2])
                continue
            if command.startswith("cb"):
                col = color_code_from_hex(command.replace("cb", "", 1).replace(" ", ""))
                rendered_text += term.on_color_rgb(col[0], col[1], col[2])
                continue
            if command == "b":
                rendered_text += term.bold
                continue
            if command == "i":
                rendered_text += term.italic
                continue
            if command == "u":
                rendered_text += term.underline
                continue
            if command == "n":
                rendered_text += term.normal
                glitchify_next = False
                continue
            if command == "r":
                rendered_text += term.reverse
                continue
            if command == "k":
                glitchify_next = True
                continue
            if glitchify_next:
                #this big chunk will generate a random string with characters from 0x20 to 0x7e
                rendered_text += "".join([chr(int(prng(beat, k))%(0x7e-0x20) + 0x20) \
                                          for k in range(len(i.replace("￼ø", "{")\
                                                             .replace("ŧ￼", "}")))])
            else:
                rendered_text += i.replace("￼ø", "{").replace("ŧ￼", "}")
        else:
            if glitchify_next:
                rendered_text += "".join([chr(int(prng(beat, k))%(0x7e-0x20) + 0x20) \
                                          for k in range(len(i.replace("￼ø", "{")\
                                                             .replace("ŧ￼", "}")))])
            else:
                rendered_text += i.replace("￼ø", "{").replace("ŧ￼", "}")
    return rendered_text

def color_code_from_hex(hexcode:str) -> list:
    # hexcode is string built like "RRGGBB"
    output = [0,0,0]
    if len(hexcode) == 6: #No more, no less
        try:
            output = [int(hexcode[i:i+2], 16) for i in range(0, len(hexcode), 2)]
        except ValueError:
            pass
    return output

def hexcode_from_color_code(code:list) -> str:
    output = "000000"
    if len(code) == 3:
        output = hex((code[0] * 256**2) + (code[1] * 256) + code[2]).replace("0x", "")
    if len(output) < 6:
        output = "0"*(6-len(output)) + output
    return output
# toDraw = ""

previous = [0, 0]

def on_resize(_, _2):
    framebuffer.UpdateRes()
    previous[0] = framebuffer.width
    previous[1] = framebuffer.height
    print(term.clear)

if platform.system() != "Windows":
    signal.signal(signal.SIGWINCH, on_resize)

def framerate():
    """Returns the current framerate."""
    return framebuffer.FPS()

def check_term_size():
    if previous[0] != framebuffer.width or previous[1] != framebuffer.height:
        on_resize(None, None)

def print_at(x, y, text:str):
    x = int(x)
    y = int(y)
    framebuffer.PrintText(term.move_xy(x, y) + text)

def refresh(reset_color:str = ""):
    """
Pro tip: only call this at the end of a frame! Or else, this may reduce the framerate greatly!
    """
    # global toDraw
    # print(toDraw)
    # toDraw = ""
    framebuffer.Draw(term.move_xy(0,0)\
                     + reset_color\
                     + " "*(term.width*term.height)\
                     + term.move_xy(0,0))

def debug_val(val):
    """Logs a detailed version of val, a keypress from blessed."""
    if not val:
        pass
    elif val.is_sequence:
        log(f"got sequence: {(str(val), val.name, val.code)}.", logging.INFO)
    elif val:
        log(f"got {val}.", logging.INFO)

def print_lines_at(x:int, y:int, text:str, center = False, color = None, reset_color = term.normal):
    if color is None:
        color = reset_color
    lines = text.split("\n")
    for i,line in enumerate(lines):
        if center:
            print_at(x, y + i, color + term.center(line).replace(" ", term.move_right) + reset_color)
        else:
            print_at(x, y + i, color + line + reset_color)

def print_image(x,y,image_path,scale):
    if os.path.exists(image_path):
        image = from_file(image_path, width=scale)
        stringified_image = str(image)
        print_lines_at(x, y, stringified_image)
        return True
    else:
        return False

def print_column(x, y, size, char):
    for i in range(size):
        print_at(x, y + i, char)

def print_cropped(x, y, maxsize, text, offset, color, is_wrap_around = True, reset_color = term.normal):
    if is_wrap_around:
        print_at(x, y, color + (text*(3+int(maxsize/len(text))))[
            (offset%len(text))+len(text):maxsize+(offset%len(text))+len(text)
        ] + reset_color)
    else:
        actual_text = text[offset%len(text):maxsize+(offset%len(text))]
        print_at(x, y, color + actual_text + reset_color + (" "*(maxsize - len(actual_text))))

def print_box(x,y,width, height, color = term.normal, style = 0, caption = "", reset_color = term.normal, inside_full = True):
    current_box_style = "????????"
    if isinstance(style, int):
        current_box_style = box_styles[style]
    elif isinstance(style, str):
        current_box_style = box_styles
    if caption != "":
        print_at(x,y,
            color + current_box_style[0] + term.reverse + caption +
            reset_color + color + (current_box_style[1]*(width-(2+len(caption))))
            + current_box_style[2] + reset_color)
    else:
        print_at(x,y,
            color + current_box_style[0] + (current_box_style[1]*(width-2))
            + current_box_style[2] + reset_color)
    print_at(x,y+height-1,
            color + current_box_style[5] + (current_box_style[6]*(width-2))
            + current_box_style[7] + reset_color)
    fill = " "*(width-2)
    if not inside_full:
        fill = term.move_right*(width-2)
    print_column(x,y+1,height-2,color + current_box_style[3] + fill + current_box_style[4])
    # print_column(x+width-1,y+1,height-2,color + current_box_style[4])

def too_small(bypass = False):
    """Checks if the screen size is smaller than what the game requires.
    Side note: having the bypass variable set to True will completely bypass this check"""
    return (framebuffer.width < MINIMUM_WIDTH or framebuffer.height < MINIMUM_HEIGHT) and not bypass
