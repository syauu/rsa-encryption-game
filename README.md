RSA SNAKE GAME

The RSA Snake Game is a hybrid project that combines the classic mechanics of the Snake game with interactive RSA encryption challenges. Built with Python and Pygame, it aims to make learning about cryptography engaging and fun.

⸻

GAME FLOW

The game progresses through four main stages, integrating both Snake gameplay and RSA concepts:

Stage 1 – Prime Collection
	•	Objective: Collect food items labeled with prime numbers.
	•	Mechanics: Random numbers appear; only some are prime.
	•	Challenge: Eating prime numbers grows the snake. Mistakes or collisions reset the stage.

Stage 2 – RSA Exponent Selection
	•	Objective: Choose a valid RSA encryption exponent (e).
	•	Mechanics: Based on the primes collected, the game computes n and φ(n). Valid e values are hinted.
	•	Challenge: Collect the correct e. Wrong choices reset the stage.

Stage 3 – Word Challenge & Encryption
	•	Objective: Form a target word by collecting letters in order.
	•	Mechanics: Each letter collected is encrypted with RSA.
	•	Challenge: Once completed, the encrypted message is displayed.

Stage 4 – Decryption Challenge
	•	Objective: Decrypt the previously encrypted word.
	•	Mechanics: Collect n (RSA modulus) and d (decryption key).
	•	Challenge: If the decrypted text matches the word, the stage is cleared. Otherwise, retry.

After completing all stages, the game loops back to Stage 1 with increasing difficulty.

⸻

INSTALLATION & SETUP
	1.	Install Python
	•	Ensure you have Python 3.x installed.
	2.	Install Pygame
Run this command in terminal or command prompt:
pip install pygame
	3.	Download the Code
	•	Clone this repository or download the source code.
	4.	Run the Game
Navigate to the project directory and run:
python rsa_snake_game.py

⸻

CONTROLS
	•	Movement: Arrow Keys (Up, Down, Left, Right)
	•	Select Difficulty (Welcome Screen):
E = Easy
M = Medium
H = Hard
	•	Exit Game: Close the game window

⸻

GAMEPLAY NOTES
	•	Follow the on-screen instructions during each stage.
	•	Each stage has hints, time limits, and progress information at the top of the screen.
	•	Mistakes reset the current stage, not the entire game.
	•	Difficulty affects number ranges, speed, and challenge complexity.

⸻

TECHNOLOGIES USED
	•	Python 3.x
	•	Pygame

⸻

PROJECT PURPOSE

This project was created to:
	•	Demonstrate the integration of cryptographic concepts into a classic game.
	•	Help players learn RSA encryption and decryption through interactive challenges.
	•	Provide a fun, educational twist on the Snake game.

⸻

Developed as part of a project on RSA Encryption Course.
