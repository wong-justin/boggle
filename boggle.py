# Justin Wong
# Boggle Game

import random
import time
from threading import Thread
import threading
import copy
import sys
import re

old_cubes = [['R', 'I', 'F', 'O', 'B', 'X'],
             ['I', 'F', 'E', 'H', 'E', 'Y'],
             ['D', 'E', 'N', 'O', 'W', 'S'],
             ['U', 'T', 'O', 'K', 'N', 'D'],
             ['H', 'M', 'S', 'R', 'A', 'O'],
             ['L', 'U', 'P', 'E', 'T', 'S'],
             ['A', 'C', 'I', 'T', 'O', 'A'],
             ['Y', 'L', 'G', 'K', 'U', 'E'],
             ['Qu', 'B', 'M', 'J', 'O', 'A'],
             ['E', 'H', 'I', 'S', 'P', 'N'],
             ['V', 'E', 'T', 'I', 'G', 'N'],
             ['B', 'A', 'L', 'I', 'Y', 'T'],
             ['E', 'Z', 'A', 'V', 'N', 'D'],
             ['R', 'A', 'L', 'E', 'S', 'C'],
             ['U', 'W', 'I', 'L', 'R', 'G'],
             ['P', 'A', 'C', 'E', 'M', 'D']]

new_cubes = [['A', 'A', 'E', 'E', 'G', 'N'],
             ['A', 'B', 'B', 'J', 'O', 'O'],
             ['A', 'C', 'H', 'O', 'P', 'S'],
             ['A', 'F', 'F', 'K', 'P', 'S'],
             ['A', 'O', 'O', 'T', 'T', 'W'],
             ['C', 'I', 'M', 'O', 'T', 'U'],
             ['D', 'E', 'I', 'L', 'R', 'X'],
             ['D', 'E', 'L', 'R', 'V', 'Y'],
             ['D', 'I', 'S', 'T', 'T', 'Y'],
             ['E', 'E', 'G', 'H', 'N', 'W'],
             ['E', 'E', 'I', 'N', 'S', 'U'],
             ['E', 'H', 'R', 'T', 'V', 'W'],
             ['E', 'I', 'O', 'S', 'S', 'T'],
             ['E', 'L', 'R', 'T', 'T', 'Y'],
             ['H', 'I', 'M', 'N', 'U', 'Qu'],
             ['H', 'L', 'N', 'N', 'R', 'Z']]

dictionaries = {
    'shortest': 'popular',
    'short': 'ospd',
    'long': 'enable1',
    'longest': 'collins2015'
    }

CUBES = new_cubes
DIFFICULTY = 'short'
DICTIONARY_PATH = 'dictionaries/' + dictionaries[DIFFICULTY] + '.txt'

BOARD_SIZE = 4
game_board = []
MAX_TIME = 180
timer = MAX_TIME

lock = threading.Lock()

def random_shuffled_cube_sides():
    random.shuffle(CUBES)
    return [random.choice(cube) for cube in CUBES]
        
def fill_board(letters):
    global game_board
    game_board = [letters[i*BOARD_SIZE:(i+1)*BOARD_SIZE]
                  for i in range(BOARD_SIZE)]
    
def display_board():

    string = '\n'
    for row in game_board:
        string += ' ' + '  '.join(row) + '\n'

    print(string)
    
def set_timer():
    global timer
    
    time_start = time.time()
##    timer = max_time
    while timer > 0:
        if timer % 30 == 0:
            with lock:
                print('Time remaining: '+ str(timer / 60) +' mins\n')
                timer -= .1
        elapsed_time = time.time() - time_start
        timer_now = MAX_TIME - elapsed_time
        if int(timer_now) < timer:
            timer = int(timer_now)
    print("TIME'S UP!")

def calc_score(words):
    return sum([score(i) for i in words])

def score(word):
    score = 0
    if len(word) <= 4:
        score = 1
    elif len(word) == 5:
        score = 2
    elif len(word) == 6:
        score = 3
    elif len(word) == 7:
        score = 5
    else:
        score = 11
    return score
        
def accept_word_inputs():
    found_words = []
    
    while timer > 0:
        word = input().upper()
        with lock:
            if valid_word(word, words=found_words, debug=True):
                found_words.append(word)
            display_board()
        
    print('Words:', len(found_words))
    print('Score:', calc_score(found_words))
    print(found_words)
    all_words = auto_solve()
    print('Max words:', len(all_words))
    print('Max score:', calc_score(all_words))
    words_not_found = [word for word in all_words
                       if word not in set(found_words)]
    print('Words missed:')
    print(words_not_found)

def valid_word(word, words=[], debug=False):
    is_valid = False
    msg = word + ' '
    if len(word) < 3:
        msg += 'is too small.'
        pass
    elif len(word) > (BOARD_SIZE ** 2) + 1:    # largest when QU used
        msg += 'is too long.'
        pass
    elif word in words:
        msg += 'already typed.'
        pass
    elif not is_word_on_board(word):
        msg += 'not on board.'
        pass
    elif not is_word_in_dict(word):
        msg += 'not in dictionary.'
        pass
    else:
        msg += 'is completely valid!'
        is_valid = True
        
    if debug:
        print(msg)
    return is_valid
    
def is_word_in_dict(word):
    with open(DICTIONARY_PATH) as file:
        contents = file.read()
        return re.search(r'\b' + re.escape(word.lower()) +r'\b', contents)

def is_word_on_board(word):    
    all_possible_locations = [(r, c)
                              for r in range(BOARD_SIZE)
                              for c in range(BOARD_SIZE)]
    
    for row, col in all_possible_locations:
        if is_word_at(word, row, col, game_board):
            return True
    return False

def is_word_at(word, row, col, board):
    
    if len(word) == 0:   # finish
        return True
    
    elif first_char(word) == board[row][col].upper():   # continue
        reduced_word = trim(word, first_char(word))
        return search_adjacent(row,
                               col,
                               reduced_word,
                               new_marked_board_at(row, col, board))
    else:   # fail
        #print('curr loc', row, col, 'does not have letter', char_word)
        return False
    
def search_adjacent(row, col, word, board):    
    for row_adj, col_adj in adjacent_locations(row, col):
        if is_word_at(word, row_adj, col_adj, board):
            return True
    return False

def first_char(word):
    return word[0] if word[0] != 'Q' else word[:2]  # QU

def trim(word, first_char):
    return word[len(first_char):]   # trims first char unless QU (then trims 2)

def new_marked_board_at(row, col, board):
    marker = '-1'
    board_copy_marked = copy.deepcopy(board)
    board_copy_marked[row][col] = marker
    return board_copy_marked
    
def adjacent_locations(r, c):
    all_adjacent = [
        (r+1, c+1),
        (r+1, c),
        (r+1, c-1),
        (r, c-1),
        (r-1, c-1),
        (r-1, c),
        (r-1, c+1),
        (r, c+1)
    ]
    return [(r, c) for r, c in all_adjacent
            if (r >= 0 and r < BOARD_SIZE) and (c >= 0 and c < BOARD_SIZE)]

def auto_solve():
    with open(DICTIONARY_PATH) as file:
        valid_words = [word.upper() for word in file.read().splitlines()
                       if valid_word(word.upper())]
        return valid_words
    
def start():
    fill_board(random_shuffled_cube_sides())
    display_board()
    Thread(target=set_timer).start()
    accept_word_inputs()

start()
