from _libnote import NotePage
from os import mkdir, path, system
from pynput import keyboard
from sys import stdout, exit
from typing import List

save_point_filename = ".critical_data/save_point"
sentences_file_path = "notepages/sentences"
vocabulary_file_path = "notepages/vocabulary"

clear_screen_cmd = "cls"

go_to_first_cmd = ["Key.home"]
go_to_last_cmd = ["Key.end"]
quit_cmd = ["'q'"]
show_previous_cmd = ["Key.left", "Key.up", "Key.page_up"]
show_next_cmd = ["Key.right", "Key.down", "Key.page_down"]
toggle_more_cmd = ["Key.space"]
toggle_note_page_cmd = ["'x'"]

go_to_first_sub_page_ctrlcmd = ["Key.home"]
go_to_last_sub_page_ctrlcmd = ["Key.end"]
previous_sub_page_ctrlcmd = ["Key.left", "Key.up", "Key.page_up"]
next_sub_page_ctrlcmd = ["Key.right", "Key.down", "Key.page_down"]
pause_ctrlcmd = ["'p'"]

note_pages: List[NotePage] = []
note_page_index = 0

is_ctrl_pressed = False
is_pausing = False


def clear():
    system(clear_screen_cmd)


def clprint(*objects, sep=" ", end="\n", file=stdout, flush=False):
    clear()
    print(*objects, sep=sep, end=end, file=file, flush=flush)


def refresh():
    string = ""

    string += f"{note_pages[note_page_index].name}\n\n"
    string += f"=== Sub-page # {note_pages[note_page_index].index + 1} ({note_pages[note_page_index].sub_page_num - note_pages[note_page_index].index - 1} Left)\n"
    string += f"=== {note_pages[note_page_index].sub_page_name}\n\n"
    string += f"# {note_pages[note_page_index].cursor + 1} ({note_pages[note_page_index].sub_page_len - note_pages[note_page_index].cursor - 1} Left)\n"
    clprint(string + note_pages[note_page_index].item_str(), end="")


# Operating functions on sub-pages


def show_more():
    note_pages[note_page_index].show_more = True
    refresh()


def show_simple():
    note_pages[note_page_index].show_more = False
    refresh()


def refresh_for_toggle():
    if note_pages[note_page_index].name == "Vocabulary":
        show_simple()
    else:
        refresh()


def show_previous():
    note_pages[note_page_index].cursor -= 1

    refresh_for_toggle()


def show_next():
    note_pages[note_page_index].cursor += 1

    refresh_for_toggle()


def go_to_first():
    note_pages[note_page_index].cursor = 0

    refresh_for_toggle()


def go_to_last():
    note_pages[
        note_page_index].cursor = note_pages[note_page_index].sub_page_len - 1

    refresh_for_toggle()


def toggle_more():
    if note_pages[note_page_index].name == "Vocabulary":
        if note_pages[note_page_index].show_more:
            show_simple()
        else:
            show_more()


# Operating functions on note pages


def previous_sub_page():
    note_pages[note_page_index].index -= 1

    refresh_for_toggle()


def next_sub_page():
    note_pages[note_page_index].index += 1

    refresh_for_toggle()


def go_to_first_sub_page():
    note_pages[note_page_index].index = 0

    refresh_for_toggle()


def go_to_last_sub_page():
    note_pages[
        note_page_index].index = note_pages[note_page_index].sub_page_num - 1

    refresh_for_toggle()


# Operating functions on note page list


def toggle_note_page():
    global note_page_index

    note_page_index = (note_page_index + 1) % len(note_pages)

    refresh_for_toggle()


def on_press_key(key):
    global is_ctrl_pressed
    global is_pausing

    if key == keyboard.Key.ctrl_l:
        is_ctrl_pressed = True

        return

    if is_ctrl_pressed:
        if str(key) in pause_ctrlcmd:
            if is_pausing:
                is_pausing = False
                refresh()
            else:
                is_pausing = True
                clprint("Pausing...\n", end="")

    if is_pausing:
        return

    if is_ctrl_pressed:
        if str(key) in go_to_first_sub_page_ctrlcmd:
            go_to_first_sub_page()
        elif str(key) in go_to_last_sub_page_ctrlcmd:
            go_to_last_sub_page()
        elif str(key) in previous_sub_page_ctrlcmd:
            previous_sub_page()
        elif str(key) in next_sub_page_ctrlcmd:
            next_sub_page()

        return

    if str(key) in go_to_first_cmd:
        go_to_first()
    elif str(key) in go_to_last_cmd:
        go_to_last()
    elif str(key) in quit_cmd:
        clear()
        exit()
    elif str(key) in show_previous_cmd:
        show_previous()
    elif str(key) in show_next_cmd:
        show_next()
    elif str(key) in toggle_more_cmd:
        toggle_more()
    elif str(key) in toggle_note_page_cmd:
        toggle_note_page()


def on_release_key(key):
    global is_ctrl_pressed

    if key == keyboard.Key.ctrl_l:
        is_ctrl_pressed = False


def main():
    global note_page_index

    note_pages.append(NotePage(vocabulary_file_path, "Vocabulary"))
    note_pages.append(NotePage(sentences_file_path, "Sentences"))

    if path.exists(save_point_filename) and path.getsize(save_point_filename):
        with open(save_point_filename, "r", encoding="utf-8") as file:
            note_page_index = int(file.readline())
            line = file.readline()

            for index in range(len(note_pages)):
                if line == "":
                    break

                note_pages[index].index = int(line)
                note_pages[index].cursors = list(
                    map(int,
                        file.readline().split()))
                line = file.readline()

    with keyboard.Listener(
            on_press=on_press_key, on_release=on_release_key) as listener:
        refresh_for_toggle()
        listener.join()

    if not path.exists(".critical_data"):
        mkdir(".critical_data")

    with open(save_point_filename, "w", encoding="utf-8") as file:
        string = str(note_page_index) + "\n"

        for index in range(len(note_pages)):
            string += str(note_pages[index].index) + "\n"
            string += " ".join(map(str, note_pages[index].cursors)) + "\n"

        file.write(string)


if __name__ == "__main__":
    main()
