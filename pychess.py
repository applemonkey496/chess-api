
from chess import *
import chess.engine as chess_engine
from chess.svg import board as draw_board
import subprocess

# The colour the human is playing as, either 
# 'white' or 'black'. Change as wanted.
player = 'white'

# Number of seconds the chess engine 
# is given to think each turn.
engine_time_per_move = 1

# When rendering the board, this is used to determine
# which way around it's facing. Set it to face the player.
orientation = WHITE if player == 'white' else BLACK


def get_move(board : Board) -> Move:
    """Gets a move from the user.

    Args:
        board (Board): The current board position (used to validate the move).

    Returns:
        Move: The move entered by the user.
    """

    def get_square(to : bool = False) -> str:
        """General function to get a square on the board.

        Args:
            to (bool, optional): Determines whether the square is the moving from square 
            or the moving to square. This only affects the prompt. Defaults to 'from' (False).

        Returns:
            str: the square.
        """

        # Get the square via user input. This could be modified on the robot to be via buttons.
        square = input('To square: ') if to else input('From square: ')
        square = square.strip() # Remove any leading or trailing whitespace
        
        # Validate that it is two characters long. Otherwise, print an 
        # error and reprompt the user by calling this function again.
        if len(square) != 2: 
            print("Sorry, invalid input. ")
            return get_square(retry=True)

        # Destructure string into row and column
        col, row = list(square)

        # Validate that the column is a-h and the row 
        # is 1-8 (the valid squares on a chess board).
        cond_b = col in ('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h')
        cond_c = row in ('1', '2', '3', '4', '5', '6', '7', '8')

        # If the row and the column are not both valid, also error.
        if not (cond_b and cond_c): 
            print("Sorry, invalid input. ")
            return get_square(retry=True)

        return square

    # Get the from and to squares. The get_square function does its
    # own validation, so we know these are safe inputs. Create a Move
    # object from the from and to squares (this format is called UCI).
    from_square, to_square = get_square(to=False), get_square(to=True)
    move = Move.from_uci(from_square + to_square)
    
    print()

    # Ensure that the move is legal given the board position, otherwise
    # ask for a new move by calling this function again.
    if not board.is_legal(move): 
        print("This move is a legal format, but it isn't possible in "
              + "this board position. Please enter a different move.")
        return get_move(board)

    # Otherwise, we know the move is valid.
    else: return move


def game(display=True):
    """Play a game of chess with the AI.

    Args:
        display (bool, optional): If enabled, this creates an image of the chess board
        every turn in a file "board.png". Defaults to True.
    """

    # Initialise Stockfish engine and board
    engine = chess_engine.SimpleEngine.popen_uci("./stockfish")
    board = Board()

    # Game loop, run until game over
    engine_turn = True if player == 'black' else False
    while not board.is_game_over():

        # Computer's move
        if engine_turn:
            # Get engine move and update board.
            print('Thinking... ')
            engine_move = engine.play(board, chess_engine.Limit(engine_time_per_move)).move
            print(f'Moved {engine_move}')
            board.push(engine_move)
            
            # After the engine's move, if display is enabled, display the board.
            if display:
                # Get SVG for board
                state = draw_board(board, orientation=orientation, lastmove=board.peek())

                # Write the SVG to a temporary file board.svg
                with open('board.svg', 'w+') as f:
                    f.write(state)

                # Convert the temporary SVG to a PNG with size 1024x1024, and remove
                # temporary file. The 1024x1024 size is arbitrary, the height and width
                # just have to be the same value to make it a square or the image will 
                # look stretched out.
                # ! NOTE: this command only works on Unix-like systems.
                subprocess.run(
                    'inkscape -z -f board.svg -w 1024 -h 1024 -e board.png > /dev/null 2>&1'
                    + '&& rm board.svg', shell=True
                )

        # Player's move.
        else:
            print()
            move = get_move(board)
            board.push(move)
        
        # Next turn. If it was the computer's turn,
        # now it's the player's turn, and vice versa.
        engine_turn = not engine_turn

    # End the engine so the process doesn't hang. 
    engine.quit()
    print(''.join(['\n', 'Game Over', '\n']))

game()
