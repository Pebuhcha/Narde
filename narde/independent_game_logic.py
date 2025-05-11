#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 30 17:10:15 2024

@author: jake
"""
import random

board = dict()

#ready to bear off indicators
w_rtb = False
b_rtb = False
#bearing off counters
w_bear_count = 0
b_bear_count = 0

#winner of the game
winner = ''

# Board initialization with spaces as keys and lists of checkers as values
# Example: {1: ['b'], 2: [], 3: ['w', 'w']}
def init():
    global board
    board = {i: [] for i in range(1, 25)}
    board[1] = ['w']*15
    board[13] = ['b']*15

#rolls two die
def roll_dice():
    die1 = random.randint(1, 6)
    die2 = random.randint(1, 6)
    return (die1, die2)

#displays the full board
def display_board():
    for space in range(1, 25):
        checkers = ''.join(board[space])
        print(f"{space}: {checkers}")

#identifies if the proposed move is valid
def is_valid_move(start, end, color, startHeadMoves):
    #checker will end between 1 and 24 and if moving from the first white pos, 
    #not using more than the allowed starting head moves
    if color == 'w' and (end < 1 or end > 24 or (start == 1 and startHeadMoves <= 0)):
        return False
    
    #checker will end between 1 and 24 and if moving from the first black pos, 
    #not using more than the allowed starting head moves. Also does not cross
    #from the end of black's play (12) to the start (13)
    if color == 'b' and (end < 1 or end > 24 or (start == 13 and startHeadMoves <= 0)
        or start <= 12 and end >= 13):
        return False
    
    #if opponent has their checker present at the destination, cannot move
    if board[end] and board[end][0] != color:
        return False
    
    #if moving this piece will create 6 consecutive spaces with this color of checker, cannot move
    if count_consecutive_checkers(start, end, color) >= 6:
        return False
    return True

#identify how many consecutive checkers the movement of end would create
def count_consecutive_checkers(start, end, color):
    #accumulate the consecutive spaces to be considered around end
    consecutive_area = []
    #gather the 5 spaces prior and after the end
    for i in range(-5, 6):
        #get the space of i
        pos = calculate_end_position(end, i, color)
        
        #if the color is white, simply identify if pos goes outside the board
        if color == 'w' and not (1 > pos or pos > 24):
            consecutive_area.append(pos)
            
        #if the color is black, identify if end is within 6 spaces of either end of black's board 
        #and if pos goes beyond one of those ends
        elif color == 'b' :
            if 13 <= end <= 17:
                if pos >= 13:
                    consecutive_area.append(pos)
            elif 7 < end <= 12:
                if pos <= 12:
                    consecutive_area.append(pos)
            else:
                consecutive_area.append(pos)
    
    #count the number of consecutive checkers for this color
    count = 0
    max_count = 0
    for space in consecutive_area:
        
        #automatically count if end == space (it won't be current on the board)
        #count if the space contains a checker of this color
        #the movement from start would vacate this color from this space unless another checker is already present
        if end == space or \
            (board[space] and board[space][0] == color and \
             (space != start or len(board[space]) >= 2)):
                
            #increment count and update the max_count
            count += 1
            max_count = max(max_count, count)
        else:
            #reset count if space does not contain a checker of this color
            count = 0
    return max_count

def get_possible_moves(color, rolls, startHeadMoves):
    #key=space value=list_of_moves
    possible_moves = dict()
    for start in range(1, 25):
        if board[start] and board[start][0] == color:
            
            #accumulate moves
            possible_moves[start] = []
            for roll in rolls:
                #get end position after move
                end = calculate_end_position(start, roll, color)
                
                #add if valid move
                if is_valid_move(start, end, color, startHeadMoves):
                    possible_moves[start].append(end)
            #if none of the moves are valid for this start, remove entry
            if possible_moves[start] == []:
                del possible_moves[start]
    return possible_moves

#returns the ending position based on the roll and accounts for the wrapping of
#black from 24 to 1
def calculate_end_position(start, roll, color):
    if color == 'w':
        end = start + roll
    elif color == 'b':
        end = (start + roll - 1) % 24 + 1
    return end

#gathers checker input from user
def select_checker(possible_moves):
    while True:
        checker = int(input(f"Select a checker to move (spaces: {list(possible_moves.keys())}): "))
        if checker in possible_moves and possible_moves[checker]:
            return checker
        print("Invalid selection. Try again.")

#gathers move input from user
def select_move(possible_moves, checker):
    while True:
        move = int(input(f"Select a move for checker at space {checker} (moves: {possible_moves[checker]}): "))
        if move in possible_moves[checker]:
            return move
        print("Invalid move. Try again.")

#moves checker on the board or bears off the checker
def move_checker(start, end):
    checker = board[start].pop(0)
    #bear off checker
    if end >= 25:
        if checker == 'w':
            global w_bear_count
            w_bear_count += 1
        else:
            global b_bear_count
            b_bear_count += 1
    #simply move checker
    else:
        board[end].insert(0, checker)

#handles bearing off movement behavior
def bear_off_moves(color, rolls):
    possible_moves = get_possible_moves(color, rolls, 0)
    move_found = bool(possible_moves)

    #if no traditional moves are possible (no move <= 24), 
    #then search for a move from the furthest point from the end of the board 
    #that will bear off (indicated by move > 24)
    if not move_found:
        for roll in sorted(rolls, reverse=True):
            
            #search each finishing board corresponding to the color
            if color == 'w':
                for space in range(25-roll, 25):
                    #does this space contain a 'w' checker
                    if board[space] and board[space][0] == 'w':

                        #add move to possible moves and indicate that a move is found
                        if space not in possible_moves.keys():
                            possible_moves[space] = []
                        possible_moves[space].append(space+roll)
                        move_found = True
                        break
            elif color == 'b':
                for space in range(13-roll, 13):
                    #does this space contain a 'b' checker
                    if board[space] and board[space][0] == 'b':

                        #add move to possible moves and indicate that a move is found
                        if space not in possible_moves.keys():
                            possible_moves[space] = []
                        possible_moves[space].append(space+roll)
                        move_found = True
                        break

            #end search when move is found
            if move_found:
                break
    return possible_moves

def play_turn(color, isFirstTurn):
    #roll dice
    rolls = roll_dice()
    print(f"Rolled: {rolls[0]}, {rolls[1]}")
    
    #tracks how many checkers may be moved off the starting head
    #an extra move off the head is allowed if:
    #   this is the first turn and
    #   the roll is doubles of 3, 4, or 6
    startHeadMoves = 1
    if isFirstTurn and rolls[0] == rolls[1] and rolls[0] in [3, 4, 6]:
        startHeadMoves = 2
    
    #4 rolls for doubles, 2 otherwise
    rolls = [rolls[0]] * 4 if rolls[0] == rolls[1] else [rolls[0], rolls[1]]
    

    #iterate for the number of rolls
    while rolls:
        #get all possible moves
        possible_moves = dict()
        
        if ready_to_bear(color):
            possible_moves = bear_off_moves(color, rolls)
        else:
            possible_moves = get_possible_moves(color, rolls, startHeadMoves)
        
        #if no possible moves returned
        if not possible_moves:
            print("No valid moves available.")
            break
        
        
        display_board()
        
        #gather checker to move from user
        checker = select_checker(possible_moves)
        
        #gather move from user
        move = select_move(possible_moves, checker)
        
        #move checker
        move_checker(checker, move)
        
        #if checker was moved off the head, count the move
        if (color == 'w' and checker == 1) or (color == 'b' and checker == 13):
            startHeadMoves -= 1
        
        #update rolls
        if move < 13 and checker > 12:
            #accomodates for the wrapping around of a black checker
            rolls.remove(abs(calculate_end_position(checker, move-checker, color) - checker + 24))
        else:
            rolls.remove(abs(calculate_end_position(checker, move-checker, color) - checker))

#returns if the color is ready to bear
def ready_to_bear(color):
    if color == 'w':
        return w_rtb
    elif color == 'b':
        return b_rtb
    else:
        return False

#evaluates if the color is ready to bear
def check_ready_to_bear(color):
    #if already ready, return
    if ready_to_bear(color):
        return
    
    #count the number of checkers on the finishing board
    finish_tbl_count = 0
    #spaces [19:24] for white and [7:12] for black
    finish_tbl_spaces = range(19,25) if color == 'w' else range(7,13)

    #sum up the number of checkers on the finishing board
    for space in finish_tbl_spaces:
        if board[space] and board[space][0] == color:
            finish_tbl_count += len(board[space])
    
    #if all checkers are present, that color is ready to bear (rtb)
    if finish_tbl_count == 15:
        if color == 'w':
            global w_rtb
            w_rtb = True
        elif color == 'b':
            global b_rtb
            b_rtb = True

#checks how many checkers have beared off and 
#returns whether or not a player has won
def win_condition():
    global winner
    if w_bear_count == 15:
        winner = 'w'
    elif b_bear_count == 15:
        winner = 'b'
    else:
        return False
    return True

def main():
    init()
    #set beginning turn
    current_turn = 'w'
    turn_number = 0
    isFirstTurn = True

    #each loop is a turn for either player
    while True:
        print(f"{current_turn.upper()}'s turn")
        
        #simulates a player's full turn
        play_turn(current_turn, isFirstTurn)

        #checks if a player is ready to bear
        check_ready_to_bear(current_turn)
        
        #switch turn
        current_turn = 'w' if current_turn == 'b' else 'b'
        
        #determine if win condition has been met
        if (w_rtb or b_rtb) and win_condition():
            break
        
        #controls first turn tracking for special movement rules
        if isFirstTurn and turn_number <= 1:
            turn_number += 1
        else:
            isFirstTurn = False

    #announce winner
    print(f"{winner.upper()} is the winner!")


        
        
if __name__ == "__main__":
    main()
