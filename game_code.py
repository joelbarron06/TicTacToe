def winning_line(strings):
    strings = set(strings)
    return len(strings) == 1 and ' ' not in strings

def row_winner(board):
    return any(winning_line(row) for row in board)

def column_winner(board):
    return row_winner(zip(*board))

def main_diagonal_winner(board):
    return winning_line(row[i] for i, row in enumerate(board))

#enumurate is a command i got from workshop example, it returns a tuple of index and value

def diagonal_winner(board):
    return main_diagonal_winner(board) or main_diagonal_winner(reversed(board))

def winner(board):
    return row_winner(board) or column_winner(board) or diagonal_winner(board)

def format_board(board):
    size = len(board)
    line = f'\n  {"+".join("-" * size)}\n'
    rows = [f'{i + 1} {"|".join(row)}' for i, row in enumerate(board)]
    return f'  {" ".join(str(i + 1) for i in range(size))}\n{line.join(rows)}'

def play_move(board, player):
    print(f'{player} to play:')
    try:
        row = int(input("Row: ")) - 1
        col = int(input("Column: ")) - 1
    except ValueError:
        print("Invalid input, please enter numbers only.")
        return play_move(board, player)
    if check_legal(board, row, col):
        board[row][col] = player
        print(format_board(board))
    else:
        play_move(board, player)

def check_legal(board, row, col):
    try:
        if board[row][col] == ' ':
            return True
        else:
            print("Illegal move, try again.")
            return False
    except IndexError:
        print("Invalid position, try again.")
        return False
    
def make_board(size):
    return [[' '] * size for _ in range(size)]

def print_winner(player):
    print(f'{player} wins!')

def print_draw():
    print("It's a draw!")

def play_game(board_size, player1, player2):
    board = make_board(board_size)
    print(format_board(board))

    
    a = 0
    while True:
        play_move(board, player1)
        a += 1
        if winner(board):
            print_winner(player1)
            break
        if a >= board_size*board_size:
            print_draw()
            break
        play_move(board, player2)
        a += 1
        if winner(board):
            print_winner(player2)
            break
        if a >= board_size*board_size:
            print_draw()
            break
        
play_game(3, 'X', 'O')

# This code implements a simple console-based Tic-Tac-Toe game for two players. 
#Future improvements could include:
# - Making a 'bot' player that plays automatically: different difficulty levels could be implemented