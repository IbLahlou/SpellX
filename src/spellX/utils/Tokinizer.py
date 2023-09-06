import re
import unidecode
import numpy as np
import os
from spellX.constants import REMOVE_CHARS 
import random
import string


def read_text(data_path, list_of_books):
    text = ''
    for book in list_of_books:
        file_path = os.path.join(data_path, book)
        strings = unidecode.unidecode(open(file_path).read())
        text += strings + ' '
    return text

def tokenize(text):
    tokens = [re.sub(REMOVE_CHARS, '', token)
              for token in re.split("[-\n ]", text)]
    return tokens


def add_spelling_errors(token, error_rate):
    # Validate the error rate
    if error_rate < 0 or error_rate > 1:
        raise ValueError("Error rate should be a value between 0 and 1")

    # Calculate the number of errors to introduce
    num_errors = int(len(token) * error_rate)

    # Create a set of characters to choose from for introducing errors
    characters = string.ascii_lowercase  # You can customize this as needed

    # Randomly select positions in the token to introduce errors
    error_positions = random.sample(range(len(token)), num_errors)

    # Convert the token to a list of characters to modify it
    token_list = list(token)

    # Introduce errors at the selected positions
    for pos in error_positions:
        random_char = random.choice(characters)
        token_list[pos] = random_char

    # Convert the modified list of characters back to a string
    modified_token = ''.join(token_list)

    return modified_token


def tokenize_data(data_path, list_of_books, error_rate):
    text = read_text(data_path, list_of_books)
    tokens = tokenize(text)
    tokens = list(filter(None, tokens))  # Remove empty tokens
    tokenized_data = [add_spelling_errors(token, error_rate) for token in tokens]
    return tokenized_data
