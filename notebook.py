from libnote.note import Note
from libnote.reader import Reader
from os import path, system
from pynput import keyboard
from sys import stdout, exit
from typing import Tuple

data_filename = ".data/data"
location_filename = ".cache/location"
saved_filename = ".cache/saved"

clear_screen_cmd = "cls"
quit_cmd = "'q'"
save_cmd = "'s'"
show_next_cmd1 = "'n'"
show_next_cmd2 = "Key.down"
show_next_cmd3 = "Key.right"
show_next_cmd4 = "Key.page_down"
show_previous_cmd1 = "'p'"
show_previous_cmd2 = "Key.left"
show_previous_cmd3 = "Key.up"
show_previous_cmd4 = "Key.page_up"
toggle_more_cmd = "Key.space"
toogle_note_cmd = "'x'"
toggle_saved_cmd = "'t'"

pause_ctrlcmd = "'p'"

is_ctrl_pressed = False
is_exit = False
is_pausing = False

notebook: Note = None

vocabulary: Note = None
sentences: Note = None
saved_vocabulary: Note = None
saved_sentences: Note = None

previous_note: Note = None
previous_saved: Note = None

last_notebook_viewed = ""


def clear():
    system(clear_screen_cmd)


def clprint(*objects, sep=" ", end="\n", file=stdout, flush=False):
    clear()
    print(*objects, sep=sep, end=end, file=file, flush=flush)


def refresh():
    string = ""
    if notebook is vocabulary:
        string += "Vocabulary:\n"
    elif notebook is sentences:
        string += "Sentences:\n"
    elif notebook is saved_vocabulary:
        string += "Saved Vocabulary:\n"
    else:
        string += "Saved Sentences:\n"
    string += "# " + str(notebook.cursor + 1) + "\n"
    clprint(string + notebook.get_the_refreshed(), end="")


def show_more():
    notebook.is_show_more = True
    refresh()


def show_simple():
    notebook.is_show_more = False
    refresh()


def show_next():
    notebook.cursor_forward()
    if notebook.name == "Vocabulary":
        show_simple()
    else:
        refresh()


def show_previous():
    notebook.cursor_backward()
    if notebook.name == "Vocabulary":
        show_simple()
    else:
        refresh()


def save():
    def write():
        with open(saved_filename, "a", encoding="utf-8") as saved_file:
            saved_file.write(str(notebook.get_current_item()))

    if notebook is vocabulary and not saved_vocabulary.has_item_key(
            notebook.get_current_item().key):
        saved_vocabulary.add(notebook.get_current_item())
        write()
    elif notebook is sentences and not saved_sentences.has_item_key(
            notebook.get_current_item().key):
        saved_sentences.add(notebook.get_current_item())
        write()


def toggle_note():
    global notebook

    if notebook is vocabulary:
        notebook = sentences
    elif notebook is sentences:
        notebook = vocabulary
    elif notebook is saved_vocabulary:
        notebook = saved_sentences
    else:
        notebook = saved_vocabulary

    exit()


def toggle_saved():
    global notebook
    global previous_note
    global previous_saved

    if notebook is vocabulary or notebook is sentences:
        previous_note = notebook
        notebook = previous_saved
    else:
        previous_saved = notebook
        notebook = previous_note

    exit()


def init_notebook() -> Tuple[Note, Note, Note, Note]:
    global last_notebook_viewed

    vocabulary = Note("Vocabulary")
    vocabulary.is_show_more = False
    sentences = Note("Sentences")
    saved_vocabulary = Note("Saved Vocabulary")
    saved_vocabulary.is_show_more = False
    saved_sentences = Note("Saved Sentences")

    with Reader(data_filename) as reader:
        flag_item = reader.next_item()
        while flag_item is not None:
            if flag_item[0]:
                vocabulary.add(flag_item[1])
            else:
                sentences.add(flag_item[1])
            flag_item = reader.next_item()

    if path.exists(saved_filename) and path.getsize(saved_filename):
        with Reader(saved_filename) as reader:
            flag_item = reader.next_item()
            while flag_item is not None:
                if flag_item[0]:
                    saved_vocabulary.add(flag_item[1])
                else:
                    saved_sentences.add(flag_item[1])
                flag_item = reader.next_item()

    if path.exists(location_filename) and path.getsize(location_filename):
        with open(location_filename, "r", encoding="utf-8") as location_file:
            vocabulary.cursor = int(location_file.readline())
            sentences.cursor = int(location_file.readline())
            saved_vocabulary.cursor = int(location_file.readline())
            saved_sentences.cursor = int(location_file.readline())
            last_notebook_viewed = location_file.readline().strip()

    return vocabulary, sentences, saved_vocabulary, saved_sentences


def on_press_key(key):
    global is_ctrl_pressed
    global is_exit
    global is_pausing

    if key == keyboard.Key.ctrl_l:
        is_ctrl_pressed = True
        return
    if is_ctrl_pressed:
        if str(key) == f"{pause_ctrlcmd}":
            if is_pausing:
                is_pausing = False
                refresh()
            else:
                is_pausing = True
                clprint("Pausing...\n", end="")
        return
    if is_pausing:
        return

    if str(key) == f"{quit_cmd}":
        is_exit = True
        clear()
        exit()
    elif str(key) == f"{save_cmd}":
        save()
    elif str(key) == f"{toggle_more_cmd}":
        if notebook is vocabulary or notebook is saved_vocabulary:
            if notebook.is_show_more:
                show_simple()
            else:
                show_more()
    elif str(key) == f"{show_next_cmd1}" or str(
            key) == f"{show_next_cmd2}" or str(
                key) == f"{show_next_cmd3}" or str(key) == f"{show_next_cmd4}":
        show_next()
    elif str(key) == f"{show_previous_cmd1}" or str(
            key) == f"{show_previous_cmd2}" or str(
                key) == f"{show_previous_cmd3}" or str(
                    key) == f"{show_previous_cmd4}":
        show_previous()
    elif str(key) == f"{toogle_note_cmd}":
        toggle_note()
    elif str(key) == f"{toggle_saved_cmd}":
        toggle_saved()


def on_release_key(key):
    global is_ctrl_pressed

    if key == keyboard.Key.ctrl_l:
        is_ctrl_pressed = False


def main():
    global last_notebook_viewed
    global notebook
    global vocabulary
    global sentences
    global saved_vocabulary
    global saved_sentences
    global previous_note
    global previous_saved

    vocabulary, sentences, saved_vocabulary, saved_sentences = init_notebook()

    previous_note = vocabulary
    previous_saved = saved_vocabulary

    def run():
        refresh()
        with keyboard.Listener(
                on_press=on_press_key, on_release=on_release_key) as listener:
            listener.join()

    if last_notebook_viewed == "Vocabulary":
        notebook = vocabulary
    elif last_notebook_viewed == "Sentences":
        notebook = sentences
    elif last_notebook_viewed == "Saved Vocabulary":
        notebook = saved_vocabulary
    else:
        notebook = saved_sentences

    while True:
        if is_exit:
            with open(
                    location_filename, "w", encoding="utf-8") as location_file:
                location_file.write(str(vocabulary.cursor) + "\n")
                location_file.write(str(sentences.cursor) + "\n")
                location_file.write(str(saved_vocabulary.cursor) + "\n")
                location_file.write(str(saved_sentences.cursor) + "\n")
                location_file.write(notebook.name + "\n")
            exit()

        run()


if __name__ == "__main__":
    main()
