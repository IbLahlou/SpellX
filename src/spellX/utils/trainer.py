# model_training.py

from keras.models import Model, load_model
from keras.layers import Input, LSTM, Dense, Dropout
from keras import optimizers, metrics, backend as K
from tensorflow.keras.optimizers import Adam
import re
import os
import unidecode
import numpy as np
from collections import Counter
import string
import nltk
from nltk.corpus import stopwords
import seaborn as sns
import matplotlib.pyplot as plt

VAL_MAXLEN = 16
# Définition des constantes pour le début et la fin d'une séquence.
SOS = '\t'  # Début de séquence.
EOS = '*'   # Fin de séquence.

# Liste des caractères utilisés dans le traitement des données texte.
CHARS = list('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ ')

# Expression régulière pour supprimer certains caractères indésirables des données.
REMOVE_CHARS = '[#$%"\+@<=>!&,-.?:;()*\[\]^_`{|}~/\d\t\n\r\x0b\x0c]'


def truncated_acc(y_true, y_pred):
    # Truncated accuracy for sequences of variable lengths
    y_true = y_true[:, :VAL_MAXLEN, :]
    y_pred = y_pred[:, :VAL_MAXLEN, :]
    
    acc = metrics.categorical_accuracy(y_true, y_pred)
    
    return K.mean(acc, axis=-1)

def truncated_loss(y_true, y_pred):
    # Truncated loss for sequences of variable lengths
    y_true = y_true[:, :VAL_MAXLEN, :]
    y_pred = y_pred[:, :VAL_MAXLEN, :]
    
    loss = K.categorical_crossentropy(
        target=y_true, output=y_pred, from_logits=False)
    
    return K.mean(loss, axis=-1)

def seq2seq(hidden_size, nb_input_chars, nb_target_chars):
    
    # Définir le modèle principal composé de l'encodeur et du décodeur.
    encoder_inputs = Input(shape=(None, nb_input_chars),
                           name='encoder_data')
    encoder_lstm = LSTM(hidden_size, recurrent_dropout=0.2,
                        return_sequences=True, return_state=False,
                        name='encoder_lstm_1')
    encoder_outputs = encoder_lstm(encoder_inputs)
    
    encoder_lstm = LSTM(hidden_size, recurrent_dropout=0.2,
                        return_sequences=False, return_state=True,
                        name='encoder_lstm_2')
    encoder_outputs, state_h, state_c = encoder_lstm(encoder_outputs)
    # Nous ignorons `encoder_outputs` et ne conservons que les états.
    encoder_states = [state_h, state_c]

    # Configuration du décodeur en utilisant les `encoder_states` comme état initial.
    decoder_inputs = Input(shape=(None, nb_target_chars),
                           name='decoder_data')
    # Configuration du décodeur pour renvoyer des séquences de sortie complètes,
    # et pour renvoyer également les états internes. Nous n'utilisons pas les états de retour
    # dans le modèle d'entraînement, mais nous les utiliserons lors de l'inférence.
    decoder_lstm = LSTM(hidden_size, dropout=0.2, return_sequences=True,
                        return_state=True, name='decoder_lstm')
    decoder_outputs, _, _ = decoder_lstm(decoder_inputs,
                                         initial_state=encoder_states)
    decoder_softmax = Dense(nb_target_chars, activation='softmax',
                            name='decoder_softmax')
    decoder_outputs = decoder_softmax(decoder_outputs)

    # Le modèle principal transformera `encoder_input_data` & `decoder_input_data`
    # en `decoder_target_data`
    model = Model(inputs=[encoder_inputs, decoder_inputs],
                  outputs=decoder_outputs)
    
    adam = Adam(lr=0.001, decay=0.0)
    model.compile(optimizer=adam, loss='categorical_crossentropy',
                  metrics=['accuracy', truncated_acc, truncated_loss])
    
    # Définir le modèle d'encodeur séparément.
    encoder_model = Model(inputs=encoder_inputs, outputs=encoder_states)

    # Définir le modèle de décodeur séparément.
    decoder_state_input_h = Input(shape=(hidden_size,))
    decoder_state_input_c = Input(shape=(hidden_size,))
    decoder_states_inputs = [decoder_state_input_h, decoder_state_input_c]
    decoder_outputs, state_h, state_c = decoder_lstm(
        decoder_inputs, initial_state=decoder_states_inputs)
    decoder_states = [state_h, state_c]
    decoder_outputs = decoder_softmax(decoder_outputs)
    decoder_model = Model(inputs=[decoder_inputs] + decoder_states_inputs,
                          outputs=[decoder_outputs] + decoder_states)

    return model, encoder_model, decoder_model


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

def add_speling_erors(token, error_rate):
    """Simule quelques erreurs d'orthographe artificielles."""
    assert (0.0 <= error_rate < 1.0)
    if len(token) < 3:
        return token
    rand = np.random.rand()
    # Voici 4 façons différentes dont des erreurs d'orthographe peuvent se produire,
    # chacune ayant une chance égale.
    prob = error_rate / 4.0
    if rand < prob:
        # Remplacer un caractère par un caractère aléatoire.
        random_char_index = np.random.randint(len(token))
        token = token[:random_char_index] + np.random.choice(CHARS) \
                + token[random_char_index + 1:]
    elif prob < rand < prob * 2:
        # Supprimer un caractère.
        random_char_index = np.random.randint(len(token))
        token = token[:random_char_index] + token[random_char_index + 1:]
    elif prob * 2 < rand < prob * 3:
        # Ajouter un caractère aléatoire.
        random_char_index = np.random.randint(len(token))
        token = token[:random_char_index] + np.random.choice(CHARS) \
                + token[random_char_index:]
    elif prob * 3 < rand < prob * 4:
        # Transposer 2 caractères.
        random_char_index = np.random.randint(len(token) - 1)
        token = token[:random_char_index] + token[random_char_index + 1] \
                + token[random_char_index] + token[random_char_index + 2:]
    else:
        # Pas d'erreurs d'orthographe.
        pass
    return token


def transform(tokens, maxlen, error_rate=0.3, shuffle=True):
    """Transforme les tokens en entrées et cibles du modèle.
    Toutes les entrées et cibles sont remplies avec le caractère EOS jusqu'à maxlen.
    """
    if shuffle:
        print('Mélange des données.')
        np.random.shuffle(tokens)
    encoder_tokens = []
    decoder_tokens = []
    target_tokens = []
    for token in tokens:
        encoder = add_speling_erors(token, error_rate=error_rate)
        encoder += EOS * (maxlen - len(encoder))  # Rempli jusqu'à maxlen.
        encoder_tokens.append(encoder)
    
        decoder = SOS + token
        decoder += EOS * (maxlen - len(decoder))
        decoder_tokens.append(decoder)
    
        target = decoder[1:]
        target += EOS * (maxlen - len(target))
        target_tokens.append(target)
        
        assert(len(encoder) == len(decoder) == len(target))
    return encoder_tokens, decoder_tokens, target_tokens


def batch(tokens, maxlen, ctable, batch_size=128, reverse=False):
    """Divise les données en blocs de `batch_size` exemples."""
    def generate(tokens, reverse):
        while True:  # Ce drapeau génère un générateur infini.
            for token in tokens:
                if reverse:
                    token = token[::-1]
                yield token
    
    token_iterator = generate(tokens, reverse)
    data_batch = np.zeros((batch_size, maxlen, ctable.size),
                          dtype=np.float32)
    while True:
        for i in range(batch_size):
            token = next(token_iterator)
            data_batch[i] = ctable.encode(token, maxlen)
        yield data_batch


def datagen(encoder_iter, decoder_iter, target_iter):
    """Fonction utilitaire pour charger les données dans le format requis par le modèle."""
    inputs = zip(encoder_iter, decoder_iter)
    while True:
        encoder_input, decoder_input = next(inputs)
        target = next(target_iter)
        yield ([encoder_input, decoder_input], target)

def decode_sequences(inputs, targets, input_ctable, target_ctable,
                     maxlen, reverse, encoder_model, decoder_model,
                     nb_examples, sample_mode='argmax', random=True):
    input_tokens = []
    target_tokens = []
    
    if random:
        indices = np.random.randint(0, len(inputs), nb_examples)
    else:
        indices = range(nb_examples)
        
    for index in indices:
        input_tokens.append(inputs[index])
        target_tokens.append(targets[index])
    input_sequences = batch(input_tokens, maxlen, input_ctable,
                            nb_examples, reverse)
    input_sequences = next(input_sequences)
    
    # Procédure pour le mode d'inférence (échantillonnage) :
    # 1) Encoder l'entrée et récupérer l'état initial du décodeur.
    # 2) Exécuter une étape du décodeur avec cet état initial
    #    et un caractère de début de séquence comme cible.
    #    La sortie sera le prochain caractère cible.
    # 3) Répéter avec le caractère cible actuel et les états actuels.

    # Encoder l'entrée en tant que vecteurs d'état.
    states_value = encoder_model.predict(input_sequences)
    
    # Créer un lot de séquences cibles vides d'une longueur de 1 caractère.
    target_sequences = np.zeros((nb_examples, 1, target_ctable.size))
    # Remplir le premier élément de la séquence cible
    # avec le caractère de début de séquence.
    target_sequences[:, 0, target_ctable.char2index[SOS]] = 1.0

    # Boucle d'échantillonnage pour un lot de séquences.
    # Condition de sortie : atteindre la limite de caractères maximale
    # ou rencontrer le caractère de fin de séquence.
    decoded_tokens = [''] * nb_examples
    for _ in range(maxlen):
        # `char_probs` a une forme
        # (nb_examples, 1, nb_target_chars)
        char_probs, h, c = decoder_model.predict(
            [target_sequences] + states_value)

        # Réinitialiser les séquences cibles.
        target_sequences = np.zeros((nb_examples, 1, target_ctable.size))

        # Échantillonner le prochain caractère en utilisant le mode argmax ou multinomial.
        sampled_chars = []
        for i in range(nb_examples):
            if sample_mode == 'argmax':
                next_index, next_char = target_ctable.decode(
                    char_probs[i], calc_argmax=True)
            elif sample_mode == 'multinomial':
                next_index, next_char = target_ctable.sample_multinomial(
                    char_probs[i], temperature=0.5)
            else:
                raise Exception(
                    "`sample_mode` accepte `argmax` ou `multinomial`.")
            decoded_tokens[i] += next_char
            sampled_chars.append(next_char) 
            # Mettre à jour la séquence cible avec l'indice du prochain caractère.
            target_sequences[i, 0, next_index] = 1.0

        stop_char = set(sampled_chars)
        if len(stop_char) == 1 and stop_char.pop() == EOS:
            break
            
        # Mettre à jour les états.
        states_value = [h, c]
    
    # Échantillonnage terminé.
    input_tokens   = [re.sub('[%s]' % EOS, '', token)
                      for token in input_tokens]
    target_tokens  = [re.sub('[%s]' % EOS, '', token)
                      for token in target_tokens]
    decoded_tokens = [re.sub('[%s]' % EOS, '', token)
                      for token in decoded_tokens]
    return input_tokens, target_tokens, decoded_tokens


def restore_model(path_to_full_model, hidden_size):
    """Restaure le modèle pour construire l'encodeur et le décodeur."""
    model = load_model(path_to_full_model, custom_objects={
        'truncated_acc': truncated_acc, 'truncated_loss': truncated_loss})
    
    encoder_inputs = model.input[0]  # encoder_data
    encoder_lstm1 = model.get_layer('encoder_lstm_1')
    encoder_lstm2 = model.get_layer('encoder_lstm_2')
    
    encoder_outputs = encoder_lstm1(encoder_inputs)
    _, state_h, state_c = encoder_lstm2(encoder_outputs)
    encoder_states = [state_h, state_c]
    encoder_model = Model(inputs=encoder_inputs, outputs=encoder_states)

    decoder_inputs = model.input[1]  # decoder_data
    decoder_state_input_h = Input(shape=(hidden_size,))
    decoder_state_input_c = Input(shape=(hidden_size,))
    decoder_states_inputs = [decoder_state_input_h, decoder_state_input_c]
    decoder_lstm = model.get_layer('decoder_lstm')
    decoder_outputs, state_h, state_c = decoder_lstm(
        decoder_inputs, initial_state=decoder_states_inputs)
    decoder_states = [state_h, state_c]
    decoder_softmax = model.get_layer('decoder_softmax')
    decoder_outputs = decoder_softmax(decoder_outputs)
    decoder_model = Model(inputs=[decoder_inputs] + decoder_states_inputs,
                          outputs=[decoder_outputs] + decoder_states)
    return encoder_model, decoder_model
