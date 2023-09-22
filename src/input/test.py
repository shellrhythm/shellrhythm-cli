from pynput.keyboard import Key, Listener

keys_pressed = []

def on_press(key):
    if key not in keys_pressed:
        keys_pressed.append(key)
        print('{0} pressed'.format(key))
    else:
        print('{0} held'.format(key))

def on_release(key):
    print('{0} released'.format(key))
    if key in keys_pressed:
        keys_pressed.remove(key)
    if key == Key.esc:
        # Stop listener
        return False

# Collect events until released
with Listener(
        on_press=on_press,
        on_release=on_release) as listener:
    listener.join()
