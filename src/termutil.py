import os
import re
import time
import signal
import platform
import datetime
from blessed import Terminal
from src.framebuffer import Framebuffer
from src.translate import LocaleManager
from term_image.image import from_file

cur_locale = LocaleManager().current_locale()

def strip_seqs(text):
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~]|\([0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)

box_styles = [
    "┌─┐││└─┘", #Base box
    ".-.||'-'"  #Minimal box
    #Maybe add more styles later?
]

def prettydate(d, longFormat = False):
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

reset_color = term.normal

def set_reset_color(color):
    global reset_color
    reset_color = color


def prng (beat = 0.0, seed = 0):
    """quick pseudorandomness don't mind me"""
    return int(beat * 210413 + 2531041 * (seed+1.3)/3.4) % 2**32

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
    text = text.replace("\\{", "￼ø").replace("\\}", "ŧ￼").replace("{", "�{").replace("}", "}�")
    #If you are using � or ￼ genuiunely, what the #### is wrong with you /gen
    data = text.split("�")
    rendered_text = ""
    glitchify_next = False
    for i in data:
        if i.startswith("{") and i.endswith("}"):
            command = i.strip("{}")
            if command.startswith("cf"):
                col = color_code_from_hex(command.replace("cf ", "", 1))
                rendered_text += term.color_rgb(col[0], col[1], col[2])
                continue
            if command.startswith("cb"):
                col = color_code_from_hex(command.replace("cb ", "", 1))
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

previous_width = 0
previous_height = 0
just_resized = False
minimum_width = 125
minimum_height = 32

def on_resize(_, _2):
    framebuffer.UpdateRes()
    global previous_width, previous_height, just_resized
    previous_width = framebuffer.width
    previous_height = framebuffer.height
    just_resized = True
    print(term.clear)

if platform.system() != "Windows":
    signal.signal(signal.SIGWINCH, on_resize)

def framerate():
    """Returns the current framerate."""
    return framebuffer.FPS()

def check_term_size():
    if previous_width != framebuffer.width or previous_height != framebuffer.height:
        on_resize(None, None)

def print_at(x, y, text:str):
    x = int(x)
    y = int(y)
    framebuffer.PrintText(term.move_xy(x, y) + text)

def refresh():
    """
Pro tip: only call this at the end of a frame! Or else, this may reduce the framerate greatly!
    """
    # global toDraw
    # print(toDraw)
    # toDraw = ""
    framebuffer.Draw(term.move_xy(0,0) + reset_color)

def debug_val(val):
    if not val:
        pass
    elif val.is_sequence:
        print_at(0,term.height-2,f"got sequence: {(str(val), val.name, val.code)}.")
    elif val:
        print_at(0,term.height-2,f"got {val}.")

def print_lines_at(x:int, y:int, text:str, center = False, color = None):
    if color is None:
        color = reset_color
    lines = text.split("\n")
    for i,line in enumerate(lines):
        if center:
            print_at(x, y + i, color + term.center(line) + reset_color)
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

def print_cropped(x, y, maxsize, text, offset, color, is_wrap_around = True):
    if is_wrap_around:
        print_at(x, y, color + (text*(3+int(maxsize/len(text))))[(offset%len(text))+len(text):maxsize+(offset%len(text))+len(text)] + reset_color)
    else:
        actual_text = text[offset%len(text):maxsize+(offset%len(text))]
        print_at(x, y, color + actual_text + reset_color + (" "*(maxsize - len(actual_text))))

def print_box(x,y,width, height, color = reset_color, style = 0, caption = ""):
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
    print_column(x,y+1,height-2,color + current_box_style[3])
    print_column(x+width-1,y+1,height-2,color + current_box_style[4])

def too_small(bypass = False):
    """Checks if the screen size is smaller than what the game requires.
    Side note: having the bypass variable set to True will completely bypass this check"""
    return (framebuffer.width < minimum_width or framebuffer.height < minimum_height) and not bypass
