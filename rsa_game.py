import pygame
import sys
import random
import math

pygame.init()

# Screen dimensions and grid settings
WIDTH, HEIGHT = 600, 400
GRID_SIZE = 20
INFO_HEIGHT = 130      # Height for instruction section (top)
BUTTON_BAR_HEIGHT = 40 # Height for external button bar (bottom)

# Colors
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED   = (255, 0, 0)
BLACK = (0, 0, 0)
BLUE  = (0, 0, 255)

# Directions
UP    = (0, -1)
DOWN  = (0, 1)
LEFT  = (-1, 0)
RIGHT = (1, 0)

# Initialize screen and font.
# Total screen height = INFO_HEIGHT + HEIGHT (playing area) + BUTTON_BAR_HEIGHT.
screen = pygame.display.set_mode((WIDTH, INFO_HEIGHT + HEIGHT + BUTTON_BAR_HEIGHT))
pygame.display.set_caption("RSA Snake Game")
font = pygame.font.Font(None, 28)
clock = pygame.time.Clock()

# Global game variables for buttons, pause, leaderboard, and difficulty.
paused = False
pause_start_time = 0
game_command = None   # Used to signal a command from a button (restart, main, newplayer).
leaderboard = {}      # Maps player_name to best (lowest) round time.
# 'difficulty' will be set when the game starts (via the welcome screen)

# -------------------------------------------------------------------
# Helper functions for buttons and pause functionality

def get_button_rects():
    """Return a dictionary mapping button id to a pygame.Rect in the button bar."""
    buttons = {}
    # The button bar is drawn at y = INFO_HEIGHT + HEIGHT.
    buttons["pause"] = pygame.Rect(10, INFO_HEIGHT + HEIGHT + 5, 100, 30)
    buttons["restart"] = pygame.Rect(120, INFO_HEIGHT + HEIGHT + 5, 100, 30)
    buttons["main"] = pygame.Rect(230, INFO_HEIGHT + HEIGHT + 5, 100, 30)
    buttons["newplayer"] = pygame.Rect(340, INFO_HEIGHT + HEIGHT + 5, 110, 30)
    buttons["leaderboard"] = pygame.Rect(460, INFO_HEIGHT + HEIGHT + 5, 130, 30)
    return buttons

def draw_button_bar():
    """Draw the external button bar at the bottom of the window."""
    button_rects = get_button_rects()
    # Draw background for the button bar.
    pygame.draw.rect(screen, (50, 50, 50), (0, INFO_HEIGHT + HEIGHT, WIDTH, BUTTON_BAR_HEIGHT))
    for key, rect in button_rects.items():
        pygame.draw.rect(screen, BLUE, rect)
        text_surface = font.render(key.capitalize(), True, WHITE)
        text_x = rect.x + (rect.width - text_surface.get_width()) // 2
        text_y = rect.y + (rect.height - text_surface.get_height()) // 2
        screen.blit(text_surface, (text_x, text_y))

def check_button_click(pos):
    """Return the id (a string) of the button that was clicked, or None."""
    button_rects = get_button_rects()
    for key, rect in button_rects.items():
        if rect.collidepoint(pos):
            return key
    return None

def handle_pause(start_time):
    """While the game is paused, display an overlay and wait for an arrow key to resume.
       When resuming, adjust start_time so that the timer is frozen during pause."""
    global paused, pause_start_time, game_command
    while paused:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            # Allow button clicks even while paused.
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                command = check_button_click(event.pos)
                if command is not None:
                    if command == "leaderboard":
                        show_leaderboard()
                    elif command in ("restart", "main", "newplayer"):
                        game_command = command
                        paused = False
                        return start_time
            if event.type == pygame.KEYDOWN:
                # Resume when any arrow key is pressed.
                if event.key in (pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT):
                    resume_time = pygame.time.get_ticks()
                    start_time += (resume_time - pause_start_time)
                    paused = False
        # Draw pause overlay on the playing area.
        pause_overlay = pygame.Surface((WIDTH, HEIGHT))
        pause_overlay.set_alpha(128)
        pause_overlay.fill(BLACK)
        screen.blit(pause_overlay, (0, INFO_HEIGHT))
        paused_text = font.render("Paused", True, WHITE)
        screen.blit(paused_text, (WIDTH // 2 - paused_text.get_width() // 2,
                                  INFO_HEIGHT + HEIGHT // 2 - paused_text.get_height() // 2))
        draw_button_bar()
        pygame.display.flip()
        clock.tick(10)
    return start_time

# -------------------------------------------------------------------
# Game functions (stages)

def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True

def generate_numbers(difficulty):
    """
    For easy, generate 5 unique numbers.
    For medium/hard, generate 8 unique numbers.
    This ensures that when 7 food values are needed later,
    there is a large enough pool to choose from.
    """
    if difficulty == "easy":
        target_count = 5
        low, high = 10, 50
    elif difficulty == "medium":
        target_count = 8
        low, high = 50, 150
    else:  # hard
        target_count = 8
        low, high = 150, 500

    numbers = []
    primes = []
    while len(numbers) < target_count:
        num = random.randint(low, high)
        if num not in numbers:
            numbers.append(num)
            if is_prime(num):
                primes.append(num)
    # Ensure at least two primes.
    if len(primes) < 2:
        return generate_numbers(difficulty)
    return (numbers, primes[:2])

def wrap_position(pos):
    x, y = pos
    if x < 0:
        x = WIDTH - GRID_SIZE
    elif x >= WIDTH:
        x = 0
    if y < 0:
        y = HEIGHT - GRID_SIZE
    elif y >= HEIGHT:
        y = 0
    return (x, y)

def draw_snake(snake):
    for segment in snake:
        # Draw snake with offset = INFO_HEIGHT.
        pygame.draw.rect(screen, GREEN, (segment[0], segment[1] + INFO_HEIGHT, GRID_SIZE, GRID_SIZE))

def draw_food(food_positions, food_values):
    for i, pos in enumerate(food_positions):
        # Draw food with offset = INFO_HEIGHT.
        pygame.draw.rect(screen, RED, (pos[0], pos[1] + INFO_HEIGHT, GRID_SIZE, GRID_SIZE))
        text = font.render(str(food_values[i]), True, WHITE)
        screen.blit(text, (pos[0] + 5, pos[1] + INFO_HEIGHT + 5))

def draw_info_section(text_lines):
    pygame.draw.rect(screen, BLUE, (0, 0, WIDTH, INFO_HEIGHT))
    for idx, line in enumerate(text_lines):
        text_surface = font.render(line, True, WHITE)
        screen.blit(text_surface, (10, 5 + idx * 25))

def reposition_snake(snake):
    """Reposition the snake in the center, preserving its length."""
    length = len(snake)
    centered_snake = []
    center_x = WIDTH // 2
    center_y = HEIGHT // 2
    for i in range(length):
        centered_snake.append((center_x - i * GRID_SIZE, center_y))
    return centered_snake

def stage1(snake, difficulty, start_time):
    """Stage 1: Eat two prime numbers (p and q) to be used later."""
    numbers, correct_primes = generate_numbers(difficulty)
    primes_required = correct_primes[:]
    primes_collected = []
    
    # Determine food count: 7 for medium/hard, 4 for easy.
    food_count = 7 if difficulty in ("medium", "hard") else 4

    food_positions = [
        (random.randint(0, (WIDTH // GRID_SIZE) - 1) * GRID_SIZE,
         random.randint(0, (HEIGHT // GRID_SIZE) - 1) * GRID_SIZE)
        for _ in range(food_count)
    ]
    food_values = random.sample(numbers, food_count)

    direction = None
    global paused, game_command, pause_start_time
    while True:
        if paused:
            start_time = handle_pause(start_time)
            if game_command is not None:
                cmd = game_command
                game_command = None
                return ("command", cmd)
        current_ticks = pygame.time.get_ticks()
        elapsed_time = (current_ticks - start_time) / 1000.0

        screen.fill(BLACK)
        info = [
            "Stage 1: Eat two largest prime numbers (p and q).",
            "These two numbers will be multiplied to form n.",
            f"Hint: Required primes: {primes_required}" if difficulty != "hard" else " ",
            f"Collected: {primes_collected}",
            f"Time Elapsed: {elapsed_time:.2f} seconds"
        ]
        draw_info_section(info)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                command = check_button_click(event.pos)
                if command is not None:
                    if command == "pause":
                        if not paused:
                            paused = True
                            pause_start_time = pygame.time.get_ticks()
                    elif command in ("restart", "main", "newplayer"):
                        game_command = command
                        return ("command", command)
                    elif command == "leaderboard":
                        show_leaderboard()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and direction != DOWN:
                    direction = UP
                elif event.key == pygame.K_DOWN and direction != UP:
                    direction = DOWN
                elif event.key == pygame.K_LEFT and direction != RIGHT:
                    direction = LEFT
                elif event.key == pygame.K_RIGHT and direction != LEFT:
                    direction = RIGHT

        if direction:
            head = snake[0]
            new_head = (head[0] + direction[0] * GRID_SIZE,
                        head[1] + direction[1] * GRID_SIZE)
            # Check for collision with walls (playing area boundaries) or itself.
            if (new_head[0] < 0 or new_head[0] >= WIDTH or 
                new_head[1] < 0 or new_head[1] >= HEIGHT or 
                new_head in snake):
                return stage1(reposition_snake(snake), difficulty, start_time)
            snake.insert(0, new_head)
            if new_head in food_positions:
                index = food_positions.index(new_head)
                value_eaten = food_values[index]
                if value_eaten in primes_required and value_eaten not in primes_collected:
                    primes_collected.append(value_eaten)
                # Respawn food.
                food_positions = [
                    (random.randint(0, (WIDTH // GRID_SIZE) - 1) * GRID_SIZE,
                     random.randint(0, (HEIGHT // GRID_SIZE) - 1) * GRID_SIZE)
                    for _ in range(food_count)
                ]
                food_values = random.sample(numbers, food_count)
                if len(primes_collected) == 2:
                    return primes_required, snake
            else:
                snake.pop()

        draw_snake(snake)
        draw_food(food_positions, food_values)
        draw_button_bar()
        pygame.display.flip()
        clock.tick(10)

def stage2(snake, p, q, start_time):
    """Stage 2: Select a valid key exponent e (coprime with φ(n))."""
    global difficulty, paused, game_command, pause_start_time
    n = p * q
    phi = (p - 1) * (q - 1)

    upper_bound = phi if phi < 1000 else 1000
    valid_options = [e for e in range(3, upper_bound) if math.gcd(e, phi) == 1]
    if not valid_options:
        valid_options = [e for e in range(3, phi) if math.gcd(e, phi) == 1]
    valid_e = random.sample(valid_options, 3) if len(valid_options) >= 3 else valid_options[:]

    # Determine food count.
    food_count = 7 if difficulty in ("medium", "hard") else 4

    invalid_numbers = []
    low_bound = max(2, phi - 100)
    high_bound = phi + 10
    while len(invalid_numbers) < (food_count - 1):
        num = random.randint(low_bound, high_bound)
        if math.gcd(num, phi) != 1 and num not in valid_e:
            invalid_numbers.append(num)

    food_positions = [
        (random.randint(0, (WIDTH // GRID_SIZE) - 1) * GRID_SIZE,
         random.randint(0, (HEIGHT // GRID_SIZE) - 1) * GRID_SIZE)
        for _ in range(food_count)
    ]
    current_food_values = ([random.choice(valid_e)] if valid_e else [])
    current_food_values.extend(random.sample(invalid_numbers, food_count - 1))
    random.shuffle(current_food_values)

    direction = None
    while True:
        if paused:
            start_time = handle_pause(start_time)
            if game_command is not None:
                cmd = game_command
                game_command = None
                return ("command", cmd)
        current_ticks = pygame.time.get_ticks()
        elapsed_time = (current_ticks - start_time) / 1000.0

        screen.fill(BLACK)
        info = [
            "Stage 2: Select a valid key exponent e (coprime with φ(n)).",
            f"n = {n}, φ(n) = {phi}",
            f"Hint: Valid e options: {valid_e}",
            f"Time Elapsed: {elapsed_time:.2f} seconds"
        ]
        draw_info_section(info)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                command = check_button_click(event.pos)
                if command is not None:
                    if command == "pause":
                        if not paused:
                            paused = True
                            pause_start_time = pygame.time.get_ticks()
                    elif command in ("restart", "main", "newplayer"):
                        game_command = command
                        return ("command", command)
                    elif command == "leaderboard":
                        show_leaderboard()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and direction != DOWN:
                    direction = UP
                elif event.key == pygame.K_DOWN and direction != UP:
                    direction = DOWN
                elif event.key == pygame.K_LEFT and direction != RIGHT:
                    direction = LEFT
                elif event.key == pygame.K_RIGHT and direction != LEFT:
                    direction = RIGHT

        if direction:
            head = snake[0]
            new_head = (head[0] + direction[0] * GRID_SIZE,
                        head[1] + direction[1] * GRID_SIZE)
            if (new_head[0] < 0 or new_head[0] >= WIDTH or
                new_head[1] < 0 or new_head[1] >= HEIGHT or
                new_head in snake):
                return stage2(reposition_snake(snake), p, q, start_time)
            else:
                snake.insert(0, new_head)
                if new_head in food_positions:
                    index = food_positions.index(new_head)
                    selected_number = current_food_values[index]
                    if selected_number in valid_e:
                        e_selected = selected_number
                        d = mod_inverse(e_selected, phi)
                        return (e_selected, d, snake)
                    else:
                        food_positions = [
                            (random.randint(0, (WIDTH // GRID_SIZE) - 1) * GRID_SIZE,
                             random.randint(0, (HEIGHT // GRID_SIZE) - 1) * GRID_SIZE)
                            for _ in range(food_count)
                        ]
                        current_food_values = ([random.choice(valid_e)] if valid_e else [])
                        current_food_values.extend(random.sample(invalid_numbers, food_count - 1))
                        random.shuffle(current_food_values)
                else:
                    snake.pop()

        draw_snake(snake)
        draw_food(food_positions, current_food_values)
        draw_button_bar()
        pygame.display.flip()
        clock.tick(10)

def stage3(snake, n, e, start_time):
    """Stage 3: Collect letters to form a target word."""
    global difficulty, paused, game_command, pause_start_time
    valid_words = [
        "HELLO", "WORLD", "APPLE", "BANANA", "ORANGE", "PEACH",
        "MANGO", "CHERRY", "LEMON", "PYTHON", "COMPUTER", "KEYBOARD"
    ]
    # Choose a word with at least 5 letters.
    target_word = random.choice([w for w in valid_words if len(w) >= 5])
    progress_index = 0

    def generate_food():
        global difficulty
        food_count = 7 if difficulty in ("medium", "hard") else 4
        food_positions = [
            (random.randint(0, (WIDTH // GRID_SIZE) - 1) * GRID_SIZE,
             random.randint(0, (HEIGHT // GRID_SIZE) - 1) * GRID_SIZE)
            for _ in range(food_count)
        ]
        correct_letter = target_word[progress_index]
        letters = [correct_letter]
        while len(letters) < food_count:
            letter = random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
            if letter == correct_letter:
                continue
            letters.append(letter)
        random.shuffle(letters)
        return food_positions, letters

    food_positions, food_letters = generate_food()
    direction = None
    while True:
        if paused:
            start_time = handle_pause(start_time)
            if game_command is not None:
                cmd = game_command
                game_command = None
                return ("command", cmd)
        current_ticks = pygame.time.get_ticks()
        elapsed_time = (current_ticks - start_time) / 1000.0

        screen.fill(BLACK)
        info = [
            f"Stage 3: Collect letters to form: {target_word}",
            f"Next letter: {target_word[progress_index]}",
            f"Time Elapsed: {elapsed_time:.2f} seconds"
        ]
        draw_info_section(info)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                command = check_button_click(event.pos)
                if command is not None:
                    if command == "pause":
                        if not paused:
                            paused = True
                            pause_start_time = pygame.time.get_ticks()
                    elif command in ("restart", "main", "newplayer"):
                        game_command = command
                        return ("command", command)
                    elif command == "leaderboard":
                        show_leaderboard()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and direction != DOWN:
                    direction = UP
                elif event.key == pygame.K_DOWN and direction != UP:
                    direction = DOWN
                elif event.key == pygame.K_LEFT and direction != RIGHT:
                    direction = LEFT
                elif event.key == pygame.K_RIGHT and direction != LEFT:
                    direction = RIGHT

        if direction:
            head = snake[0]
            new_head = (head[0] + direction[0] * GRID_SIZE,
                        head[1] + direction[1] * GRID_SIZE)
            if (new_head[0] < 0 or new_head[0] >= WIDTH or
                new_head[1] < 0 or new_head[1] >= HEIGHT or
                new_head in snake):
                return stage3(reposition_snake(snake), n, e, start_time)
            else:
                snake.insert(0, new_head)
                if new_head in food_positions:
                    index = food_positions.index(new_head)
                    letter_eaten = food_letters[index]
                    if letter_eaten == target_word[progress_index]:
                        progress_index += 1
                        if progress_index == len(target_word):
                            plaintext = target_word
                            ascii_codes = [ord(c) for c in plaintext]
                            encrypted = [pow(m, e, n) for m in ascii_codes]
                            screen.fill(BLACK)
                            disp_text = "Encrypted message: " + ' '.join(map(str, encrypted))
                            text_surface = font.render(disp_text, True, WHITE)
                            screen.blit(text_surface, (10, HEIGHT // 2))
                            pygame.display.flip()
                            waiting = True
                            while waiting:
                                for ev in pygame.event.get():
                                    if ev.type == pygame.QUIT:
                                        pygame.quit(); sys.exit()
                                    if ev.type == pygame.KEYDOWN:
                                        waiting = False
                            return (plaintext, encrypted, snake)
                        else:
                            food_positions, food_letters = generate_food()
                    else:
                        food_positions, food_letters = generate_food()
                else:
                    snake.pop()

        draw_snake(snake)
        draw_food(food_positions, food_letters)
        draw_button_bar()
        pygame.display.flip()
        clock.tick(10)

def stage4(snake, n, d, plaintext, encrypted, start_time, player_name):
    """Stage 4: Decryption Challenge. Collect first n then d.
       Also updates the leaderboard with the round time."""
    global difficulty, paused, game_command, pause_start_time, leaderboard
    target_sequence = [n, d]
    progress_index = 0

    def generate_food():
        global difficulty
        food_count = 7 if difficulty in ("medium", "hard") else 4
        food_positions = [
            (random.randint(0, (WIDTH // GRID_SIZE) - 1) * GRID_SIZE,
             random.randint(0, (HEIGHT // GRID_SIZE) - 1) * GRID_SIZE)
            for _ in range(food_count)
        ]
        correct_value = target_sequence[progress_index]
        food_values = [correct_value]
        while len(food_values) < food_count:
            candidate = random.randint(1, n + 10)
            if candidate == correct_value:
                continue
            food_values.append(candidate)
        random.shuffle(food_values)
        return food_positions, food_values

    food_positions, food_values = generate_food()
    direction = None
    while True:
        if paused:
            start_time = handle_pause(start_time)
            if game_command is not None:
                cmd = game_command
                game_command = None
                return ("command", cmd)
        current_ticks = pygame.time.get_ticks()
        elapsed_time = (current_ticks - start_time) / 1000.0

        screen.fill(BLACK)
        info = [
            "Stage 4: Decryption Challenge",
            "Encrypted: " + ' '.join(map(str, encrypted)),
            "Collect in order: first n then d",
            f"Hint: n = {n}, d = {d}",
            f"Time Elapsed: {elapsed_time:.2f} seconds"
        ]
        draw_info_section(info)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                command = check_button_click(event.pos)
                if command is not None:
                    if command == "pause":
                        if not paused:
                            paused = True
                            pause_start_time = pygame.time.get_ticks()
                    elif command in ("restart", "main", "newplayer"):
                        game_command = command
                        return ("command", command)
                    elif command == "leaderboard":
                        show_leaderboard()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and direction != DOWN:
                    direction = UP
                elif event.key == pygame.K_DOWN and direction != UP:
                    direction = DOWN
                elif event.key == pygame.K_LEFT and direction != RIGHT:
                    direction = LEFT
                elif event.key == pygame.K_RIGHT and direction != LEFT:
                    direction = RIGHT

        if direction:
            head = snake[0]
            new_head = (head[0] + direction[0] * GRID_SIZE, head[1] + direction[1] * GRID_SIZE)
            if (new_head[0] < 0 or new_head[0] >= WIDTH or 
                new_head[1] < 0 or new_head[1] >= HEIGHT or 
                new_head in snake):
                return stage4(reposition_snake(snake), n, d, plaintext, encrypted, start_time, player_name)
            else:
                snake.insert(0, new_head)
                if new_head in food_positions:
                    index = food_positions.index(new_head)
                    value_eaten = food_values[index]
                    if value_eaten == target_sequence[progress_index]:
                        progress_index += 1
                        if progress_index == len(target_sequence):
                            total_ms = pygame.time.get_ticks() - start_time
                            total_seconds = total_ms / 1000.0
                            # Update leaderboard: record best (lowest) time for this player.
                            if player_name not in leaderboard or total_seconds < leaderboard[player_name]:
                                leaderboard[player_name] = total_seconds
                            decrypted_chars = [chr(pow(c, d, n)) for c in encrypted]
                            decrypted_message = ''.join(decrypted_chars)
                            
                            result_msg = f"Decryption Success! Plaintext: {plaintext}" if decrypted_message == plaintext \
                                         else f"Decryption Failed! Expected: {plaintext}, got: {decrypted_message}"
                            timer_msg = f"Player {player_name} took {total_seconds:.2f} seconds"
                            
                            screen.fill(BLACK)
                            text_surface = font.render(result_msg, True, WHITE)
                            screen.blit(text_surface, (10, HEIGHT // 2 - 20))
                            text_timer = font.render(timer_msg, True, WHITE)
                            screen.blit(text_timer, (10, HEIGHT // 2 + 20))
                            pygame.display.flip()
                            
                            waiting = True
                            while waiting:
                                for ev in pygame.event.get():
                                    if ev.type == pygame.QUIT:
                                        pygame.quit(); sys.exit()
                                    if ev.type == pygame.KEYDOWN:
                                        waiting = False
                            return snake
                        else:
                            food_positions, food_values = generate_food()
                    else:
                        food_positions, food_values = generate_food()
                else:
                    snake.pop()

        draw_snake(snake)
        draw_food(food_positions, food_values)
        draw_button_bar()
        pygame.display.flip()
        clock.tick(10)

# -------------------------------------------------------------------
# Math helpers

def extended_gcd(a, b):
    if a == 0:
        return (b, 0, 1)
    else:
        g, y, x = extended_gcd(b % a, a)
        return (g, x - (b // a) * y, y)

def mod_inverse(e, phi):
    g, x, y = extended_gcd(e, phi)
    if g != 1:
        return None
    else:
        return x % phi

# -------------------------------------------------------------------
# Menus

def show_leaderboard():
    """Display the leaderboard page. Press the Back button to return."""
    global leaderboard
    running = True
    while running:
        screen.fill(BLACK)
        title_text = font.render("Leaderboard", True, WHITE)
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 20))
        sorted_leaderboard = sorted(leaderboard.items(), key=lambda x: x[1])
        y_offset = 60
        for i, (player, time_val) in enumerate(sorted_leaderboard):
            entry_text = font.render(f"{i+1}. {player}: {time_val:.2f}s", True, WHITE)
            screen.blit(entry_text, (50, y_offset))
            y_offset += 30
        # Draw Back button.
        back_rect = pygame.Rect(WIDTH // 2 - 50, INFO_HEIGHT + HEIGHT + BUTTON_BAR_HEIGHT - 35, 100, 30)
        pygame.draw.rect(screen, BLUE, back_rect)
        back_text = font.render("Back", True, WHITE)
        screen.blit(back_text, (back_rect.x + (back_rect.width - back_text.get_width()) // 2, 
                                  back_rect.y + (back_rect.height - back_text.get_height()) // 2))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if back_rect.collidepoint(event.pos):
                    running = False
        clock.tick(10)

def show_welcome_screen():
    screen.fill(BLACK)
    font_large = pygame.font.Font(None, 48)
    text_title = font_large.render("RSA Snake Game", True, WHITE)
    screen.blit(text_title, (WIDTH // 2 - 100, HEIGHT // 2 - 100))

    font_small = pygame.font.Font(None, 32)
    text_easy = font_small.render("Press E for Easy", True, WHITE)
    text_medium = font_small.render("Press M for Medium", True, WHITE)
    text_hard = font_small.render("Press H for Hard", True, WHITE)
    screen.blit(text_easy, (WIDTH // 2 - 90, HEIGHT // 2 - 40))
    screen.blit(text_medium, (WIDTH // 2 - 90, HEIGHT // 2))
    screen.blit(text_hard, (WIDTH // 2 - 90, HEIGHT // 2 + 40))

    # Optional Back button.
    back_rect = pygame.Rect(10, 10, 80, 30)
    pygame.draw.rect(screen, BLUE, back_rect)
    text_back = font_small.render("Back", True, WHITE)
    screen.blit(text_back, (back_rect.x + 10, back_rect.y + 3))

    pygame.display.flip()

    selected_difficulty = None

    while not selected_difficulty:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if back_rect.collidepoint(event.pos):
                    show_welcome_screen()
                    return show_welcome_screen()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e:
                    selected_difficulty = "easy"
                elif event.key == pygame.K_m:
                    selected_difficulty = "medium"
                elif event.key == pygame.K_h:
                    selected_difficulty = "hard"
        clock.tick(10)

    return selected_difficulty

def register_player():
    """Show a registration screen for the player to enter their name."""
    input_name = ""
    while True:
        screen.fill(BLACK)
        prompt = "Enter your name: " + input_name
        font_large = pygame.font.Font(None, 36)
        input_text = font_large.render(prompt, True, WHITE)
        screen.blit(input_text, (50, HEIGHT // 2))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and input_name.strip() != "":
                    return input_name.strip()
                elif event.key == pygame.K_BACKSPACE:
                    input_name = input_name[:-1]
                else:
                    input_name += event.unicode
        clock.tick(30)

# -------------------------------------------------------------------
# Main game loop

def main():
    global game_command, paused, difficulty
    player_name = register_player()  # Register player's profile.
    difficulty = show_welcome_screen()
    snake = [(WIDTH // 2, HEIGHT // 2)]
    current_stage = 1
    start_time = pygame.time.get_ticks()  # Start stopwatch before Stage 1.

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

        if current_stage == 1:
            result = stage1(snake, difficulty, start_time)
            if isinstance(result, tuple) and result[0] == "command":
                cmd = result[1]
                game_command = None
                if cmd == "restart":
                    snake = [(WIDTH // 2, HEIGHT // 2)]
                    current_stage = 1
                    start_time = pygame.time.get_ticks()
                    continue
                elif cmd == "main":
                    difficulty = show_welcome_screen()
                    snake = [(WIDTH // 2, HEIGHT // 2)]
                    current_stage = 1
                    start_time = pygame.time.get_ticks()
                    continue
                elif cmd == "newplayer":
                    player_name = register_player()
                    difficulty = show_welcome_screen()
                    snake = [(WIDTH // 2, HEIGHT // 2)]
                    current_stage = 1
                    start_time = pygame.time.get_ticks()
                    continue
            else:
                primes, snake = result
                current_stage = 2
        elif current_stage == 2:
            result = stage2(snake, primes[0], primes[1], start_time)
            if isinstance(result, tuple) and result[0] == "command":
                cmd = result[1]
                game_command = None
                if cmd == "restart":
                    snake = [(WIDTH // 2, HEIGHT // 2)]
                    current_stage = 1
                    start_time = pygame.time.get_ticks()
                    continue
                elif cmd == "main":
                    difficulty = show_welcome_screen()
                    snake = [(WIDTH // 2, HEIGHT // 2)]
                    current_stage = 1
                    start_time = pygame.time.get_ticks()
                    continue
                elif cmd == "newplayer":
                    player_name = register_player()
                    difficulty = show_welcome_screen()
                    snake = [(WIDTH // 2, HEIGHT // 2)]
                    current_stage = 1
                    start_time = pygame.time.get_ticks()
                    continue
            else:
                e, d, snake = result
                n = primes[0] * primes[1]
                current_stage = 3
        elif current_stage == 3:
            result = stage3(snake, n, e, start_time)
            if isinstance(result, tuple) and result[0] == "command":
                cmd = result[1]
                game_command = None
                if cmd == "restart":
                    snake = [(WIDTH // 2, HEIGHT // 2)]
                    current_stage = 1
                    start_time = pygame.time.get_ticks()
                    continue
                elif cmd == "main":
                    difficulty = show_welcome_screen()
                    snake = [(WIDTH // 2, HEIGHT // 2)]
                    current_stage = 1
                    start_time = pygame.time.get_ticks()
                    continue
                elif cmd == "newplayer":
                    player_name = register_player()
                    difficulty = show_welcome_screen()
                    snake = [(WIDTH // 2, HEIGHT // 2)]
                    current_stage = 1
                    start_time = pygame.time.get_ticks()
                    continue
            else:
                plaintext, encrypted, snake = result
                current_stage = 4
        elif current_stage == 4:
            result = stage4(snake, n, d, plaintext, encrypted, start_time, player_name)
            if isinstance(result, tuple) and result[0] == "command":
                cmd = result[1]
                game_command = None
                if cmd == "restart":
                    snake = [(WIDTH // 2, HEIGHT // 2)]
                    current_stage = 1
                    start_time = pygame.time.get_ticks()
                    continue
                elif cmd == "main":
                    difficulty = show_welcome_screen()
                    snake = [(WIDTH // 2, HEIGHT // 2)]
                    current_stage = 1
                    start_time = pygame.time.get_ticks()
                    continue
                elif cmd == "newplayer":
                    player_name = register_player()
                    difficulty = show_welcome_screen()
                    snake = [(WIDTH // 2, HEIGHT // 2)]
                    current_stage = 1
                    start_time = pygame.time.get_ticks()
                    continue
            else:
                snake = result
                # Reset snake, stage, and restart timer for a new round.
                snake = [(WIDTH // 2, HEIGHT // 2)]
                current_stage = 1
                start_time = pygame.time.get_ticks()
        clock.tick(10)

if __name__ == "__main__":
    main()
