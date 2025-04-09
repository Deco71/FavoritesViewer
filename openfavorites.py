# encoding: utf-8
import os
import re
from bs4 import BeautifulSoup

favorites_file = ""
out_dir = "out"

def execute(file, path, bookmarks, bookmark_index=0):
    if len(file) == 0:
        return
    row = file.pop(0)
    if "<DL><p>" in row:
        pass
    elif "<DT><H3" in row:
        nameUnparsed = row.split("\">")[1].split("<")[0]
        name = re.sub(r'[^a-zA-Z\s]+', '', nameUnparsed)
        if not os.path.exists(path + "/" + name):
            os.makedirs(path + "/" + name)
        path = path + "/" + name
        with open(path + "/.NONRIMUOVEREOSPOSTARE" + name, "w", encoding='utf-8') as w:
            w.write(row)
    elif "<DT><A" in row:
        nameUnparsed = row.split("\">")[1].split("<")[0]
        name = re.sub(r'[^a-zA-Z\s]+', '', nameUnparsed)
        create_url_shortcut(name, bookmarks[bookmark_index].get("href"), row, path)
        bookmark_index += 1
    elif "</DL><p>" in row:
        path = path.split("/")
        path.pop()
        path = "/".join(path)
    execute(file, path, bookmarks, bookmark_index)



def create_url_shortcut(name, url, data, save_path="."):
    file_path = f"{save_path}/{name}.url"
    with open(file_path, "w+") as file:
        file.write(f"[InternetShortcut]\n")
        file.write(f"URL={url}\n")
        file.write(f"Data={data}\n")



if "__main__" == __name__:  
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    else:
        print("Per favore apri prima il file ./savefavorites.py e poi prova a lanciare questo script")
        exit(1)
    for file_name in os.listdir("."):
        if file_name.endswith(".html"):
            if favorites_file != "":
                print("Non avere più di un file html nella cartella")
                os.rmdir(out_dir, ignore_errors=True)
                exit(1)
            favorites_file = file_name
    with open(favorites_file, "r", encoding="utf-8") as file:
        soup = BeautifulSoup(file, "html.parser")

    # Trova tutti i link (i tag <A>)
    bookmarks = soup.find_all("a")
    with open(favorites_file, "r", encoding='utf-8') as f:
        favorites = f.read()
        with open("favorites.txt", "w", encoding='utf-8') as w:
            file = favorites.splitlines()
            execute(file, out_dir, bookmarks)