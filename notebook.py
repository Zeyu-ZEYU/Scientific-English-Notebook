from _libnote import NotePage
from os import makedirs, system
from os.path import dirname, exists, getsize, isfile
from pynput import keyboard
from sys import stdout, exit
from typing import List

save_point_filename = ".critical_data/save_point"
sentences_data_path = ".critical_data/sentences_data"
sentences_file_path = "notepages/sentences"
vocabulary_data_path = ".critical_data/vocabulary_data"
vocabulary_file_path = "notepages/vocabulary"

clear_screen_cmd = "cls"

go_to_first_cmd = ["Key.home"]
go_to_last_cmd = ["Key.end"]
show_previous_cmd = ["Key.left", "Key.up", "Key.page_up"]
show_next_cmd = ["Key.right", "Key.down", "Key.page_down"]

go_to_first_sub_page_ctrlcmd = ["Key.home"]
go_to_last_sub_page_ctrlcmd = ["Key.end"]
previous_sub_page_ctrlcmd = ["Key.left", "Key.up", "Key.page_up"]
next_sub_page_ctrlcmd = ["Key.right", "Key.down", "Key.page_down"]
reset_review_ctrlcmd = ["'i'"]
toggle_more_ctrlcmd = ["Key.space"]
toggle_note_page_ctrlcmd = ["'t'"]
toggle_reviewer_ctrlcmd = ["'r'"]
pause_ctrlcmd = ["'p'"]
quit_ctrlcmd = ["'q'"]

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
    remaining_item_num = note_pages[note_page_index].sub_page_len - note_pages[
        note_page_index].cursor - 1
    remaining_sub_page_num = note_pages[
        note_page_index].sub_page_num - note_pages[note_page_index].index - 1
    key_presented = note_pages[note_page_index].key_presented

    if remaining_item_num < 0:
        remaining_item_num = 0

    if remaining_sub_page_num < 0:
        remaining_sub_page_num = 0

    string += f"{note_pages[note_page_index].name}\n\n"

    if not note_pages[note_page_index].in_reviewer:
        string += f"=== Sub-page # {note_pages[note_page_index].index + 1} ({remaining_sub_page_num} Left)\n"

    string += f"=== {note_pages[note_page_index].sub_page_name}\n\n"

    if note_pages[note_page_index].in_reviewer:
        string += f"=== √ {note_pages[note_page_index].reviewed_num} Reviewed || × {note_pages[note_page_index].unreviewed_num} Unreviewed\n"
        string += f"=== {'' if note_pages[note_page_index].reviewed_today(key_presented) else 'Not '}Reviewed Today "
        string += f"(Already Reviewed {note_pages[note_page_index].review_times(key_presented)} Times)\n\n"

    string += f"# {note_pages[note_page_index].cursor + 1} ({remaining_item_num} Left)\n"
    clprint(string + note_pages[note_page_index].item_str(), end="")


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


# Operating functions on sub-pages


def go_to_first():
    note_pages[note_page_index].cursor = 0

    refresh_for_toggle()


def go_to_last():
    note_pages[
        note_page_index].cursor = note_pages[note_page_index].sub_page_len - 1

    refresh_for_toggle()


def show_previous():
    note_pages[note_page_index].cursor -= 1

    refresh_for_toggle()


def show_next():
    note_pages[note_page_index].cursor += 1

    refresh_for_toggle()


def toggle_more():
    if note_pages[note_page_index].name == "Vocabulary":
        if note_pages[note_page_index].show_more:
            show_simple()
        else:
            show_more()


# Operating functions on note pages


def go_to_first_sub_page():
    note_pages[note_page_index].index = 0

    refresh_for_toggle()


def go_to_last_sub_page():
    note_pages[
        note_page_index].index = note_pages[note_page_index].sub_page_num - 1

    refresh_for_toggle()


def previous_sub_page():
    note_pages[note_page_index].index -= 1

    refresh_for_toggle()


def next_sub_page():
    note_pages[note_page_index].index += 1

    refresh_for_toggle()


def reset_review():
    note_pages[note_page_index].reset_review(
        note_pages[note_page_index].key_presented)

    refresh_for_toggle()


def toggle_reviewer():
    if note_pages[note_page_index].in_reviewer:
        note_pages[note_page_index].in_reviewer = False
    else:
        note_pages[note_page_index].in_reviewer = True

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
        elif str(key) in reset_review_ctrlcmd:
            reset_review()
        elif str(key) in toggle_more_ctrlcmd:
            toggle_more()
        elif str(key) in toggle_note_page_ctrlcmd:
            toggle_note_page()
        elif str(key) in toggle_reviewer_ctrlcmd:
            toggle_reviewer()
        elif str(key) in quit_ctrlcmd:
            clear()
            exit()

        return

    if str(key) in go_to_first_cmd:
        go_to_first()
    elif str(key) in go_to_last_cmd:
        go_to_last()
    elif str(key) in show_previous_cmd:
        show_previous()
    elif str(key) in show_next_cmd:
        show_next()


def on_release_key(key):
    global is_ctrl_pressed

    if key == keyboard.Key.ctrl_l:
        is_ctrl_pressed = False


def main():
    global note_page_index

    note_pages.append(
        NotePage(vocabulary_file_path, vocabulary_data_path, "Vocabulary"))
    note_pages.append(
        NotePage(sentences_file_path, sentences_data_path, "Sentences"))

    if exists(save_point_filename) and isfile(save_point_filename) and getsize(
            save_point_filename):
        with open(save_point_filename, "r", encoding="utf-8") as file:
            note_page_index = int(file.readline())

    with keyboard.Listener(
            on_press=on_press_key, on_release=on_release_key) as listener:
        refresh_for_toggle()
        listener.join()

    if not exists(save_point_filename) or not isfile(save_point_filename):
        dir_name = dirname(save_point_filename)

        if not exists(dir_name):
            makedirs(dir_name)

    with open(save_point_filename, "w", encoding="utf-8") as file:
        file.write(str(note_page_index) + "\n")

    for note_page in note_pages:
        note_page.close()


if __name__ == "__main__":
    main()
