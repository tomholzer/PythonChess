import chess
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime

# Slova pro figurky
symbols = {
    'P': '♙', 'N': '♘', 'B': '♗', 'R': '♖', 'Q': '♕', 'K': '♔',
    'p': '♟', 'n': '♞', 'b': '♝', 'r': '♜', 'q': '♛', 'k': '♚'
}

# Fonty
piece_font = ImageFont.truetype("C:\\Windows\\Fonts\\seguisym.ttf", 35)
coord_font = ImageFont.truetype("C:\\Windows\\Fonts\\seguisym.ttf", 12)
move_font = ImageFont.truetype("C:\\Windows\\Fonts\\arial.ttf", 16)

# 🧠 Funkce pro načtení šachovnice ze souboru pozice.txt
def load_board_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = [line.strip() for line in file if line.strip()]

    board = chess.Board.empty()
    for rank in range(8):
        row = content[rank].split()
        for file in range(8):
            square = chess.square(file, 7 - rank)
            piece = row[file]
            if piece != '.':
                board.set_piece_at(square, chess.Piece.from_symbol(piece))

    print("Šachovnice načtena.")
    return board

# 🧠 Funkce pro načtení tahů ze souboru tahy.txt
def load_moves_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = [line.strip() for line in file if line.strip()]

    moves = []
    for line in content:
        parts = line.split()
        for part in parts:
            if part.endswith('.'):
                continue
            moves.append(part)

    print(f"Načtené tahy: {moves}")
    return moves

# 🎨 Funkce pro vykreslení šachovnice
def draw_board(board, move_san=None):
    square_size = 60
    board_size = square_size * 8
    img_width = board_size
    img_height = board_size + 40  # Černý pruh pro popis tahu
    img = Image.new("RGB", (img_width, img_height), "white")
    draw = ImageDraw.Draw(img)

    colors = ["#f0d9b5", "#b58863"]

    for rank in range(8):
        for file in range(8):
            color = colors[(rank + file) % 2]
            x0 = file * square_size
            y0 = rank * square_size
            draw.rectangle([x0, y0, x0 + square_size, y0 + square_size], fill=color)

            square = chess.square(file, 7 - rank)
            piece = board.piece_at(square)
            if piece:
                symbol = symbols.get(piece.symbol(), '?')
                ascent, descent = piece_font.getmetrics()
                bbox = piece_font.getbbox(symbol)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                offset_y = ascent - text_height // 2
                center_x = x0 + square_size / 2 - text_width / 2
                center_y = y0 + square_size / 2 - offset_y
                draw.text((center_x, center_y), symbol, fill="black", font=piece_font)

    # Písmena (a–h)
    for i, letter in enumerate("abcdefgh"):
        x = (i + 1) * square_size - 2
        y = 8 * square_size + 2
        draw.text((x, y), letter, fill="black", font=coord_font, anchor="rd")

    # Čísla (1–8)
    for i in range(8):
        number = str(8 - i)
        x = 4 - 2
        y = i * square_size + 4 - 5
        draw.text((x, y), number, fill="black", font=coord_font, anchor="la")

    # Černý pruh pro popis tahu
    if move_san:
        pruh_y0 = board_size
        pruh_y1 = img_height
        draw.rectangle([0, pruh_y0, img_width, pruh_y1], fill="black")
        draw.text((10, pruh_y0 + 10), f"Move: {move_san}", fill="white", font=move_font)

    return img

# 🏁 Hlavní běh programu
board = load_board_from_file("pozice.txt")
moves = load_moves_from_file("tahy.txt")

if board.turn == chess.WHITE:
    print("Začíná bílý.")
else:
    print("Začíná černý.")

images = []
durations = []

# Přidáme první snímek, který bude s delším zpožděním (např. 1500ms)
initial_image = draw_board(board)
images.append(initial_image)
durations.append(1500)

# Výchozí prodleva pro běžný tah
default_delay = 1000
check_delay = 2000
mate_delay = 2500
castle_delay = 2000
final_move_delay = 4000

for i, move in enumerate(moves):
    print(f"Zpracovávám tah {i + 1}: {move}")
    try:
        chess_move = chess.Move.from_uci(move)
        if chess_move in board.legal_moves:
            san = board.san(chess_move)
            board.push(chess_move)
            img = draw_board(board, san)
            images.append(img)

            # Nastavení výchozí prodlevy
            delay = default_delay

            # Speciální tahy (může přepsat výchozí delay)
            if '#' in san:
                delay = mate_delay
            elif '+' in san:
                delay = check_delay
            elif san in ["O-O", "O-O-O"]:
                delay = castle_delay

            # Poslední tah přepíše všechno ostatní
            if i == len(moves) - 1:
                delay = final_move_delay

            durations.append(delay)
        else:
            print(f"Nelegální tah: {move}")
    except Exception as e:
        print(f"Chyba při zpracování tahu {move}: {e}")


# Kontrola a uložení výsledného GIFu
if len(images) == 0:
    print("❌ Žádné obrázky nebyly vytvořeny. Zkontroluj tahy a soubor.")
else:
    timestamp = datetime.now().strftime("%y%m%d_%H%M%S")
    gif_filename = f"chess_{timestamp}.gif"

    images[0].save(
        gif_filename,
        save_all=True,
        append_images=images[1:],
        duration=durations,
        loop=0
    )

    print(f"✅ Hotovo: {gif_filename} vytvořen.")