
# I AM COOKIN


history = [None]

ply = 0  # Keep count of ply

move_50 = 0  # Keep count of moves without capture or pawn move

colors = [None] * 64  # Used for checking what color is the piece standing on a square
piece = [None] * 64  # Used for checking what piece is on the square 'K' is white king and 'k' black

# 10x12 board representation where A1 is 56 and A8 is 0
# this allows for simple checks for moves off the board

# Board representation where 0-63 represents the actual chess board and all the -1 are imaginary square's
# outside the board for the purpose of move gen
board = [
    -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,
    -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,
    -1,  0,  1,  2,  3,  4,  5,  6,  7, -1,
    -1,  8,  9, 10, 11, 12, 13, 14, 15, -1,
    -1, 16, 17, 18, 19, 20, 21, 22, 23, -1,
    -1, 24, 25, 26, 27, 28, 29, 30, 31, -1,
    -1, 32, 33, 34, 35, 36, 37, 38, 39, -1,
    -1, 40, 41, 42, 43, 44, 45, 46, 47, -1,
    -1, 48, 49, 50, 51, 52, 53, 54, 55, -1,
    -1, 56, 57, 58, 59, 60, 61, 62, 63, -1,
    -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,
    -1, -1, -1, -1, -1, -1, -1, -1, -1, -1]

# Real board for move's 21-->0 and so on
mailbox = [
    21, 22, 23, 24, 25, 26, 27, 28,
    31, 32, 33, 34, 35, 36, 37, 38,
    41, 42, 43, 44, 45, 46, 47, 48,
    51, 52, 53, 54, 55, 56, 57, 58,
    61, 62, 63, 64, 65, 66, 67, 68,
    71, 72, 73, 74, 75, 76, 77, 78,
    81, 82, 83, 84, 85, 86, 87, 88,
    91, 92, 93, 94, 95, 96, 97, 98]

side_to_move = 0  # if 0 white to move if 1 black to move

black_short_side_castle = True
black_long_side_castle = True
white_short_side_castle = True
white_long_side_castle = True


king_moved_white = False
king_moved_black = False


en_passant_target = None


def pawn_gen(position, color):
    single_moves = []
    double_moves = []

    direction = -1 if color == 'white' else 1

    single_move = position + (direction * 10)
    if board[single_move] != -1:
        single_moves.append(single_move)

    if direction == -1 and 81 <= position <= 88:
        double_move = position + (direction * 20)
        if board[double_move] != -1:
            double_moves.append(double_move)

    if direction == 1 and 31 <= position <= 38:
        double_move = position + (direction * 20)
        if board[double_move] != -1:
            double_moves.append(double_move)

    return single_moves, double_moves


def rook_gen(position):
    vertical_moves = []
    horizontal_moves = []

    # Generate vertical moves upwards
    up = position + 10
    while board[up] != -1:
        vertical_moves.append(up)
        up += 10

    # Generate vertical moves downwards
    down = position - 10
    while board[down] != -1:
        vertical_moves.append(down)
        down -= 10

    # Generate horizontal moves left
    left = position - 1
    while board[left] != -1:
        horizontal_moves.append(left)
        left -= 1

    # Generate horizontal moves right
    right = position + 1
    while board[right] != -1:
        horizontal_moves.append(right)
        right += 1

    return vertical_moves, horizontal_moves


def bishop_gen(position):
    right_up = []
    right_down = []
    left_up = []
    left_down = []

    # Generate right up moves

    ru = position - 9
    while board[ru] != -1:
        right_up.append(ru)
        ru -= 9

    # Generate right down moves

    rd = position + 11
    while board[rd] != -1:
        right_down.append(rd)
        rd += 11

    # Generate left up moves

    lu = position - 11
    while board[lu] != -1:
        left_up.append(lu)
        lu -= 11

    # Generate left down moves

    ld = position + 9
    while board[ld] != -1:
        left_down.append(ld)
        ld += 9

    return right_up, right_down, left_down, left_up


def queen_gen(position):
    diagonal_moves = []
    ver_horizontal_moves = []
    diagonal_moves.extend(bishop_gen(position))
    ver_horizontal_moves.extend(rook_gen(position))

    return diagonal_moves, ver_horizontal_moves


def king_gen(position):
    one_each_direction = []

    # Generate moves in each direction
    directions = [10, -10, 1, -1, -9, -11, 9, 11]

    for direction in directions:
        next_position = position + direction

        # Check if the next position is within the board
        if board[next_position] != -1:
            one_each_direction.append(next_position)

    return one_each_direction


def knight_gen(position):
    l_moves = []

    # Generate moves in each direction
    directions = [-21, -19, -12, -8, 8, 12, 19, 21]

    for direction in directions:
        next_position = position + direction

        # Check if the next position is within the board
        if board[next_position] != -1:
            l_moves.append(next_position)

    return l_moves

# Move validation begins here
# We want validation function for all pieces and pawn
# We want to check if destination square is occupied by a friendly piece if yes move invalid
# We want to check if the received destination is actually somewhere that the piece
# should be able to move in the first place for example for rook is the destination in the same row or column
# theoretically I don't need it if my move gen is correct ? idk Probably should add it as it won't take long ?
# Worst case scenario I can remove it later in the name of "optimization" lol
# We also still didn't touch en passant unsure where to handle it. Probably should just add some def en_passant_gen
# above but idk maybe it will fit into move validation as we can check for it after a double move from a pawn
# save it if we find it and pass it along to the next side in play ? That seems smart.
# We also want to check for check on the player making the move that way if after the move player would be in check
# move is invalid


def is_check_after_move(source, destination):
    step = 0
    target = None
    s = board[source]
    d = board[destination]
    search = None
    # Make a copy of the board to simulate the move
    mailbox_copy = mailbox[:]
    piece_copy = piece[:]
    colors_copy = colors[:]

    # Perform the move on the copied board we move to the destination
    mailbox_copy[d] = mailbox_copy[s]
    mailbox_copy[s] = None
    piece_copy[d] = piece_copy[s]
    piece_copy[s] = None
    colors_copy[d] = colors_copy[s]
    colors_copy[s] = None

    # Now somehow check if the players king is in check
    # We search for the players, that made the move, king
    if side_to_move == 0:
        search = 'K'  # if white K
    else:
        search = 'k'  # if black k
    # We get the index of the square where the king stands
    for index, pieced in enumerate(piece_copy):
        if pieced == search:
            target = index
            break
    # We determine the direction of the move
    column_source = source % 10
    row_source = source // 10
    column_destination = destination % 10
    row_destination = destination // 10
    # Take index of king square in pieces and get the numer of board

    # We need to identify where the piece was before the move in relation to the king
    # Then check if it stayed in the same column/row/diagonal
    # If not then scan the new space for the adequate pieces also we should check for checks from knight possible square
    # even before that
    # We probably can change dest and source to indexes on the pices board and work from that
    # Since we will need to check the pieces list anyway

    target = mailbox[target]

    # Now the first point.
    column_up = 0
    column_down = 0
    row_left = 0
    row_right = 0
    up_right = 0
    up_left = 0
    down_right = 0
    down_left = 0

    # Start by checking row

    if target // 10 == row_source == row_destination:
        return False
    if target // 10 == row_source != row_destination:
        if source > destination:
            row_right = 1
            step = 1
        else:
            row_left = 1
            step = 1
    if target % 10 == column_source == column_destination:
        return False
    if target % 10 == column_source != column_destination:
        if source > destination:
            column_up = 1
            step = -10
        else:
            column_down = 1
            step = 10
    # Check for the diagonals
    if abs(target % 10 - column_source) == abs(target // 10 - row_source):
        if target % 10 > column_source:
            if target // 10 > row_source:
                down_right = 1
                step = 11
            else:
                up_right = 1
                step = -9
        else:
            if target // 10 > row_source:
                down_left = 1
                step = 9
            else:
                up_left = 1
                step = -11
# Now we need to scan the right direction, we probably can just scan the mailbox board ? or we can scan the pieces
# list I dont know what could possible differ and honestly unsure of why would I need the pieces and colors board any
# way if Im using BIG and SMALL letters for different sides on mailbox ? Going to go with simply going through mailbox
# can change it latter

    # Need to scan the right direction until it hits a piece of any sort  <-where the piece list can come in clutch?
    # or if it reaches the end of the board<--board check necessary ?
    # Then check if that piece is of different color than the side that moved and then check if it's
    # piece that can put the king in check
    check = source
    check = check + step
    transition = board[check]
    square = piece[transition]
    # Check for knight checks
    knight_moves = [-21, -19, -12, -8, 8, 12, 19, 21]  # Possible knight moves
    for move in knight_moves:
        check = source + move
        if board[check] != -1 and piece[board[check]].lower() == 'n':
            # Knight of the opposite side can check the king
            return False

    while square is None and board[check] != -1:
        if side_to_move == 0 and (row_right == 1 or row_left == 1 or column_up == 1 or column_down == 1):
            if square == 'q' or square == 'r':
                return False
            else:
                check = check + step
                transition = board[check]
                square = piece[transition]
        if side_to_move == 1 and (row_right == 1 or row_left == 1 or column_up == 1 or column_down == 1):
            if square == 'Q' or square == 'R':
                return False
            else:
                check = check + step
                transition = board[check]
                square = piece[transition]
        if side_to_move == 0 and (down_left == 1 or down_left == 1 or up_left == 1 or up_right == 1):
            if square == 'q' or square == 'b':
                return False
            else:
                check = check + step
                transition = board[check]
                square = piece[transition]
        if side_to_move == 1 and (down_left == 1 or down_left == 1 or up_left == 1 or up_right == 1):
            if square == 'Q' or square == 'B':
                return False
            else:
                check = check + step
                transition = board[check]
                square = piece[transition]


def rook_val(source,destination):
    source = source
    destination = destination
    step_1 = 0
    # Check first for the same row and then for same column
    if source // 10 != destination // 10 and source % 10 != destination % 10:
        return False
    # Check if in the destination square we already have some piece of the same color if yes we cant move and stop
    s = board[source]
    d = board[destination]
    if colors[d] is not None and colors[s] is not None and colors[d] == colors[s]:
        return False
    # Check for pieces blocking the path
    # vertical move check if we go up step 10 if down -10
    if source % 10 == destination % 10:
        if source < destination:
            step = 10
        else:
            step = -10
    # if not vertical then horizontal if right 1 else -1
    else:
        if source < destination:
            step = 1
        else:
            step = -1
    # Loop through all the squares from source to destination checking on everyone if its empty
    position = source + step_1
    position = board[position]
    while mailbox[position] != destination:
        if piece[position] is not None:
            return False
        position = position + step

    # Last we check if after the move would the player end up in check we will do this in different function

    if not is_check_after_move(source, destination):
        return False

    return True


def bishop_val(source, destination):
    step = 0
    step_1 = 0
    # For bishop move cant be in the same row or column
    if source // 10 == destination // 10 and source % 10 == destination % 10:
        return False
    # Check for piece of same color in destination
    s = board[source]
    d = board[destination]
    if colors[d] is not None and colors[s] is not None and colors[d] == colors[s]:
        return False
    mod_s = source % 10
    mod_d = destination % 10
    if mod_s < mod_d and destination > source:
        step_1 = 11
        step = 9
    if mod_s < mod_d and destination < source:
        step_1 = -9
        step = -7
    if mod_s > mod_d and destination < source:
        step_1 = -11
        step = -9
    if mod_s > mod_d and destination > source:
        step_1 = 9
        step = 7

    position = source + step_1
    position = board[position]
    while mailbox[position] != destination:
        if piece[position] is not None:
            return False
        position = position + step

    if not is_check_after_move(source, destination):
        return False

    return True


def knight_val(source, destination):
    # For knight move cant be in the same row or column
    if source // 10 == destination // 10 and source % 10 == destination % 10:
        return False
    # Check for piece of same color in destination
    s = board[source]
    d = board[destination]
    if colors[d] is not None and colors[s] is not None and colors[d] == colors[s]:
        return False
    # We don't need to check for blocking pieces because knight jumps over them :) so we just check for check
    if is_check_after_move(source, destination):
        return False

    return True


def queen_val(source, destination):
    step_1 = 0
    step = 0
    # We need to check if the destination is on the same column or row or diagonals
    source_row = source // 10
    source_col = source % 10
    dest_row = destination // 10
    dest_col = destination % 10
    if source_row != dest_row and source_col != dest_col and abs(source_row-dest_row) != abs(source_col-dest_col):
        return False
    # Check if in the destination square we already have some piece of the same color if yes we cant move and stop
    s = board[source]
    d = board[destination]
    if colors[d] is not None and colors[s] is not None and colors[d] == colors[s]:
        return False
    # Now we want to check for blocking pieces
    mod_s = source % 10
    mod_d = destination % 10
    if source_row == dest_row and source > destination:
        step_1 = -1
        step = -1
    elif source_row == dest_row and source < destination:
        step_1 = 1
        step = 1
    elif source_col == dest_col and source > destination:
        step_1 = -10
        step = -8
    elif source_col == dest_col and source < destination:
        step_1 = 10
        step = 8
    elif mod_s < mod_d and destination > source:
        step_1 = 11
        step = 9
    elif mod_s < mod_d and destination < source:
        step_1 = -9
        step = -7
    elif mod_s > mod_d and destination < source:
        step_1 = -11
        step = -9
    elif mod_s > mod_d and destination > source:
        step_1 = 9
        step = 7

    position = source + step_1
    position = board[position]
    while mailbox[position] != destination:
        if piece[position] is not None:
            return False
        position = position + step

    if is_check_after_move(source, destination):
        return False

    return True


def pawn_val(source, destination):

    start_row = source // 10
    start_col = source % 10
    end_row = destination // 10
    end_col = destination % 10

    # Determine the direction of movement based on the pawn's color
    if side_to_move == 0:
        direction = -1
    elif side_to_move == 1:
        direction = 1
    else:
        return False

    # Check if the move is within the allowed range for a pawn
    if start_col == end_col:
        if (start_row + direction == end_row) or (start_row + 2 * direction == end_row and start_row in (3, 8)):
            if is_check_after_move(source,destination):
                return True

    return False

