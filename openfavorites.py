# encoding: utf-8
import os
import regex
from bs4 import BeautifulSoup

out_dir = "preferiti"

def execute(file, path, bookmarks, bookmark_index=0):
    while len(file) != 0:
        row = file.pop(0)
        if "<DL><p>" in row:
            pass
        elif "<DT><H3" in row:
            nameUnparsed = row.split("\">")[1].split("<")[0]
            name = regex.sub(r'[^\s\p{L}]+', '', nameUnparsed)
            if not os.path.exists(path + "/" + name):
                os.makedirs(path + "/" + name)
            path = path + "/" + name
        elif "<DT><A" in row:
            nameUnparsed = row.split("\">")[1].split("<")[0]
            name = regex.sub(r'[^\s\p{L}]+', '', nameUnparsed)
            create_url_shortcut(name, bookmarks[bookmark_index].get("href"), row, path)
            bookmark_index += 1
        elif "</DL><p>" in row:
            path = path.split("/")
            path.pop()
            path = "/".join(path)
    return bookmark_index


def create_url_shortcut(name, url, data, save_path="."):
    file_path = f"{save_path}/{name}.url"
    if os.path.exists(file_path):
        return
    with open(file_path, "w+") as file:
        file.write(f"[InternetShortcut]\n")
        file.write(f"URL={url}\n")
        return



if "__main__" == __name__:
    favorites_file = input("Inserisci il nome del file da elaborare: ")
    try:
        with open(favorites_file, "r", encoding="utf-8") as file:
            soup = BeautifulSoup(file, "html.parser")
    except FileNotFoundError:
        print(f"Il file '{favorites_file}' non esiste.")
        exit(1)

    # Trova tutti i link (i tag <A>)
    bookmarks = soup.find_all("a")
    created = 0
    with open(favorites_file, "r", encoding='utf-8') as f:
        favorites = f.read()
        with open("favorites.txt", "w", encoding='utf-8') as w:
            file = favorites.splitlines()
            created = execute(file, out_dir, bookmarks)
    print(f"Ho elaborato {created} preferiti")