from config import Config

def load_blacklist():
    """
    Carrega a blacklist do arquivo.
    """
    try:
        with open(Config.BLACKLIST_FILE, 'r') as f:
            return set(line.strip() for line in f)
    except FileNotFoundError:
        return set()

def load_whitelist():
    """
    Carrega a whitelist do arquivo.
    """
    try:
        with open(Config.WHITELIST_FILE, 'r') as f:
            return set(line.strip() for line in f)
    except FileNotFoundError:
        return set()

def save_to_file(file_path, data):
    """
    Salva uma lista no arquivo.
    """
    with open(file_path, 'w') as f:
        f.writelines(f"{item}\n" for item in data)

def update_blacklist(ip, action):
    """
    Adiciona ou remove um IP da blacklist.
    """
    blacklist = load_blacklist()
    if action == "add":
        blacklist.add(ip)
    elif action == "remove":
        blacklist.discard(ip)
    save_to_file(Config.BLACKLIST_FILE, blacklist)

def update_whitelist(ip, action):
    """
    Adiciona ou remove um IP da whitelist.
    """
    whitelist = load_whitelist()
    if action == "add":
        whitelist.add(ip)
    elif action == "remove":
        whitelist.discard(ip)
    save_to_file(Config.WHITELIST_FILE, whitelist)
