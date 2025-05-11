import random

board = dict()

# Board initialization with spaces as keys and lists of checkers as values
# Example: {1: ['b'], 2: [], 3: ['w', 'w']}
def init():
    board = {i: [] for i in range(1, 25)}
    board[1] = ['w']*15
    board[13] = ['b']*15

def roll_dice():
    die1 = random.randint(1, 6)
    die2 = random.randint(1, 6)
    return (die1, die2)

def display_board():
    for space in range(1, 25):
        checkers = ''.join(board[space])
        print(f"{space}: {checkers}")

def is_valid_move(start, end, color, startHeadMoves):
    if color == 'w' and (end < 1 or end > 24 or (start == 1 and startHeadMoves == 0)):
        return False
    if color == 'b' and (end < 1 or end > 24 or (start == 13 and startHeadMoves == 0)):
        return False
    if board[end] and board[end][0] != color:
        return False
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
        if color == 'w' and not (-1 > pos or pos > 24):
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
            if possible_moves[start] == []:
                del possible_moves[start]
    return possible_moves

def calculate_end_position(start, roll, color):
    if color == 'w':
        end = start + roll
    elif color == 'b':
        end = (start + roll - 1) % 24 + 1
    return end

def select_checker(color, possible_moves):
    while True:
        try:
            checker = int(input(f"Select a checker to move (spaces: {list(possible_moves.keys())}): "))
            if checker in possible_moves and possible_moves[checker]:
                return checker
        except ValueError:
            pass
        print("Invalid selection. Try again.")

def select_move(possible_moves, checker):
    while True:
        try:
            move = int(input(f"Select a move for checker at space {checker} (moves: {possible_moves[checker]}): "))
            if move in possible_moves[checker]:
                return move
        except ValueError:
            pass
        print("Invalid move. Try again.")

def move_checker(start, end):
    checker = board[start].pop(0)
    board[end].insert(0, checker)

def play_turn(color, isFirstTurn):
    #roll dice
    rolls = (1,2) #roll_dice()
    print(f"Rolled: {rolls[0]}, {rolls[1]}")
    
    #tracks how many checkers may be moved off the starting head
    #an extra move off the head is allowed if:
    #   this is the first turn
    #   the roll is doubles of 3, 4, or 6
    startHeadMoves = 1
    if isFirstTurn and rolls[0] == rolls[1] and rolls[0] in [3, 4, 6]:
        startHeadMoves = 2
    
    #4 rolls for doubles, 2 otherwise
    rolls = [rolls[0]] * 4 if rolls[0] == rolls[1] else [rolls[0], rolls[1]]
    initial_rolls = rolls.copy()
    
    #iterate for the number of rolls
    while rolls:
        print("Startheadmoves", startHeadMoves)
        #get all possible moves
        possible_moves = get_possible_moves(color, rolls, startHeadMoves)
        
        #if no possible moves returned
        if not possible_moves:
            print("No valid moves available.")
            break
        
        
        display_board()
        
        #gather checker to move from user
        checker = select_checker(color, possible_moves)
        
        #gather move from user
        move = select_move(possible_moves, checker)
        
        #move checker
        move_checker(checker, move)
        
        #if checker was moved off the head, count the move
        if (color == 'w' and checker == 1) or (color == 'b' and checker == 13):
            startHeadMoves -= 1
        
        #update rolls
        rolls.remove(abs(calculate_end_position(checker, move-checker, color) - checker))

        # Check if all moves for this turn are completed
        if not rolls and len(initial_rolls) == 2:
            break

def main():
    init()
    #set beginning turn
    current_turn = 'w'
    turn_number = 0
    isFirstTurn = True
    while True:
        print(f"{current_turn.upper()}'s turn")
        play_turn(current_turn, isFirstTurn)
        current_turn = 'w' if current_turn == 'b' else 'b'
        if input("Continue? (y/n): ").lower() != 'y':
            break
        if isFirstTurn and turn_number <= 1:
            turn_number += 1
        else:
            isFirstTurn = False

if __name__ == "__main__":
    main()

