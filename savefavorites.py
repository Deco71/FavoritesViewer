import json
from collections import defaultdict
from pathlib import Path
import os

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
        lines.append(f'{indent_str}<DT><H3>{name}</H3>')
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

# Salva su file
if "__main__" == __name__:  
    # Imposta qui il percorso della tua cartella principale
    cartella = "out"
    risultato = raccogli_url(cartella)

    print(f"Ho trovato {len(risultato)} bookmarks")
    
    html_output = generate_bookmark_file(risultato)
    with open("bookmarks_to_save.html", "w", encoding='utf-8') as f:
        f.write(html_output)
    print("File 'bookmarks.html' creato correttamente.")
