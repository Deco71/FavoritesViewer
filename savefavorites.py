import datetime
from collections import defaultdict
import os
import regex
from bs4 import BeautifulSoup
import shutil
import subprocess

out_dir = "preferiti"

def parse_name(nameUnparsed):
    name = regex.sub(r'[^\s\p{L}\p{N}-_’\']+', '', nameUnparsed)
    name = name.strip()
    if len(name) > 200:
        #max length 200
        name = name[:200]
    return name


def execute(file, path, bookmarks, bookmark_index=0):
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    while len(file) != 0:
        row = file.pop(0)
        if "<DL><p>" in row:
            pass
        elif "<DT><H3" in row:
            nameUnparsed = row.split("\">")[1].split("<")[0]
            name = parse_name(nameUnparsed)
            if not os.path.exists(path + "/" + name):
                os.makedirs(path + "/" + name)
                print(f"Creata la cartella {path + '/' + name}")
                path = path + "/" + name
        elif "<DT><A" in row:
            nameUnparsed = row.split("\">")[1].split("<")[0]
            name = parse_name(nameUnparsed)
            create_url_shortcut(name, bookmarks[bookmark_index].get("href"), path)
            bookmark_index += 1
        elif "</DL><p>" in row:
            path = path.split("/")
            path.pop()
            path = "/".join(path)
    return bookmark_index


def create_url_shortcut(name, url, save_path="."):
    file_path = f"{save_path}/{name}.url"
    if os.path.exists(file_path):
        return
    try:
        with open(file_path, "w+") as file:
            print(f"Creata la scorciatoia {file_path}")
            file.write(f"[InternetShortcut]\n")
            file.write(f"URL={url}\n")
            return
    except FileNotFoundError:
        print(f"Impossibile creare il file {file_path}. Assicurati che il percorso esista.")
        exit(1)
        return

def estrai_url_da_file(filepath):
    with open(filepath, 'r') as f:
        for line in f:
            if line.startswith("URL="):
                return line.strip().split("=", 1)[1]
    return None

def raccogli_url(cartella_principale):
    dati = []
    for root, dirs, files in os.walk(cartella_principale):
        for file in files:
            if file.endswith(".url"):
                percorso_completo = os.path.join(root, file)
                url = estrai_url_da_file(percorso_completo)
                if url:
                    nome = os.path.splitext(file)[0]
                    path_relativo = os.path.relpath(root, cartella_principale).replace("\\", "/")
                    dati.append({
                        "name": nome,
                        "url": url,
                        "path": path_relativo
                    })
    return dati

# Costruisce un albero annidato di cartelle
def build_tree(bookmarks):
    tree = lambda: defaultdict(tree)
    root = tree()
    for bm in bookmarks:
        parts = bm['path'].split('/') if bm['path'] else []
        curr = root
        for part in parts:
            curr = curr[part]
        if '_links' not in curr:
            curr['_links'] = []
        curr['_links'].append(bm)
    return root

# Genera HTML ricorsivamente
def render_folder(name, content, indent=1):
    lines = []
    indent_str = '    ' * indent
    if name and name != '.':
        lines.append(f'{indent_str}<DT><H3 ADD_DATE="0">{name}</H3>')
        lines.append(f'{indent_str}<DL><p>')
    for key, val in content.items():
        if key == '_links':
            for link in val:
                lines.append(f'{indent_str}    <DT><A HREF="{link["url"]}">{link["name"]}</A>')
        else:
            lines.extend(render_folder(key, val, indent + 1))
    if name and name != '.':
        lines.append(f'{indent_str}</DL><p>')
    return lines

# HTML iniziale
def generate_bookmark_file(bookmarks):
    tree = build_tree(bookmarks)
    lines = [
        '<!DOCTYPE NETSCAPE-Bookmark-file-1>',
        '<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">',
        '<TITLE>Bookmarks</TITLE>',
        '<H1>Bookmarks</H1>',
        '<DL><p>'
    ]
    lines += render_folder(None, tree)
    lines.append('</DL><p>')
    return '\n'.join(lines)

if "__main__" == __name__:
    if not os.path.exists(out_dir):
        found = False
        while not found:
            # Apertura
            favorites_file = input("Inserisci il nome del file dei preferiti: ")
            try:
                with open(favorites_file, "r", encoding="utf-8") as file:
                    soup = BeautifulSoup(file, "html.parser")
                    found = True
            except FileNotFoundError:
                print(f"Il file '{favorites_file}' non esiste.")

        # Creazione struttura
        bookmarks = soup.find_all("a")
        created = 0
        with open(favorites_file, "r", encoding='utf-8') as f:
            favorites = f.read()
            file = favorites.splitlines()
            created = execute(file, out_dir, bookmarks)
        print(f"Ho elaborato {created} preferiti")

        # Apertura Cartella
        subprocess.Popen(f'explorer "{out_dir}"')

        input("Cartella per la modifica aperta, premere invio per completare l'operazione di salvataggio...")
    else:
        print("Cartella per la modifica già esistente, procedo con il salvataggio dei preferiti...")

    #Salvataggio
    cartella = out_dir
    risultato = raccogli_url(cartella)
    print(f"Ho trovato {len(risultato)} bookmarks")
    html_output = generate_bookmark_file(risultato)

    # Creazione del nome del file HTML
    today = datetime.datetime.now()
    today_date = today.strftime("%Y-%m-%d") 
    filename = "preferiti-"+today_date+".html"
    filenameToCheck = filename
    omonomini = 0
    while os.path.exists(filenameToCheck):
        omonomini += 1
        filenameToCheck = filename.split(".")[0] + " (" + str(omonomini) + ")" + "." + filename.split(".")[1]
    filename = filenameToCheck

    # Scrittura del file HTML
    with open(filename, "w", encoding='utf-8') as f:
        f.write(html_output)
    shutil.rmtree(out_dir)
    print("File creato correttamente con il nome " + filename)
