from pathlib import Path

CONFIG_FILE_PATH = Path("./config/config.yaml")
PARAMS_FILE_PATH = Path("params.yaml")
SOS = '\t'  # Début de séquence.
EOS = '*'   # Fin de séquence.# Liste des caractères utilisés dans le traitement des données texte.
CHARS = list('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ ')# Expression régulière pour supprimer certains caractères indésirables des données.
REMOVE_CHARS = '[#$%"\+@<=>!&,-.?:;()*\[\]^_`{|}~/\d\t\n\r\x0b\x0c]'
