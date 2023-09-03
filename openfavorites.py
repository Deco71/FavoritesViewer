# encoding: utf-8
import os

favorites_file = ""
out_dir = "out"

def execute(file, path):
    if len(file) == 0:
        return
    print(file[0])
    row = file.pop(0).replace(" ", "")
    if "<DL><p>" in row:
        pass
    elif "<DT><H3" in row:
        name = row.split("\">")[1].split("<")[0]
        os.makedirs(path + "/" + name)
        path = path + "/" + name
        with open(path + "/.NONRIMUOVEREOSPOSTARE" + name, "w", encoding='utf-8') as w:
            w.write(row)
    elif "<DT><A" in row:
        name = row.split("\">")[1].split("<")[0]
        with open(path + "/" + name, "w", encoding='utf-8') as w:
            w.write(row)
    elif "</DL><p>" in row:
        path = path.split("/")
        path.pop()
        path = "/".join(path)
    execute(file, path)



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
                exit(1)
            favorites_file = file_name
    with open(favorites_file, "r", encoding='utf-8') as f:
        favorites = f.read()
        with open("favorites.txt", "w", encoding='utf-8') as w:
            file = favorites.splitlines()
            execute(file, out_dir)