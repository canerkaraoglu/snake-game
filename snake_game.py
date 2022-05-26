import pygame
import random
from enum import Enum
from collections import namedtuple

# Initialize all pygame modules
pygame.init()

# Create font for the text.
font = pygame.font.Font('arial.ttf', 25)


# Constants. We can only use one of these values because of the Enum inheritance.
class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4


# Namedtuple declaration. Point name, 'x,y' elements.
Point = namedtuple('Point', 'x, y')

# Size of the block. Constant
BLOCK_SIZE = 20

# Speed of the game
SPEED = 10

# Colors for the screen elements

WHITE = (255, 255, 255)
RED = (200, 0, 0)
BLUE1 = (0, 0, 255)
BLUE2 = (0, 100, 255)
BLACK = (0, 0, 0)


class SnakeGame:
    def __init__(self, w=640, h=480):
        self.w = w
        self.h = h

        # init display
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('Snake')
        self.clock = pygame.time.Clock()  # This is for controlled gaming speed.

        # init game state
        self.direction = Direction.RIGHT  # starting direction

        # initialize the snake
        self.head = Point(self.w / 2, self.h / 2)  # half of width and height. Snake starts in the middle of the display

        # Snake. [head coordinate, middle coordinate, tail coordinate]. Y's are same. X coordinate changes
        # proportional to the block size.

        self.snake = [self.head, Point(self.head.x - BLOCK_SIZE, self.head.y),
                      Point(self.head.x - (2 * BLOCK_SIZE), self.head.y)]

        # Initially score is 0, and we place the food randomly on the screen.
        self.score = 0
        self.food = None

        self.speed = SPEED
        self._place_food()

    def _place_food(self):
        """
        Randomly creates a coordinate in the boundaries of the display and places the food.
        """
        x = random.randint(0, (self.w - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        y = random.randint(0, (self.h - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        self.food = Point(x, y)
        # If random point is inside the snake's boundaries, discard it and call the function recursively
        if self.food in self.snake:
            self._place_food()

    def play_step(self):
        """
        Controls the game via the user's input.
        :return: score (int)
        """

        # This for loop gets all the events from the user, within ONE play_step invoke.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()  # exit from pygame instance
                quit()  # exit our Python program

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.direction = Direction.LEFT
                elif event.key == pygame.K_RIGHT:
                    self.direction = Direction.RIGHT
                elif event.key == pygame.K_UP:
                    self.direction = Direction.UP
                elif event.key == pygame.K_DOWN:
                    self.direction = Direction.DOWN

        # Move the snake
        self._move(self.direction)  # update the head
        self.snake.insert(0, self.head)  # insert the new head at the beginning of the list of snake.

        # Check if the game is over, quit if this is the case
        game_over = False
        if self._is_collision():
            game_over = True
            return game_over, self.score

        # Place new food or just move
        if self.head == self.food:
            self.score += 1
            self.speed += 2
            self._place_food()
        else:
            self.snake.pop()  # removes the last element of our snake. Because we have inserted one at the beginning.

        # Update the pygame ui and clock
        self._update_ui()
        self.clock.tick(self.speed)

        # Return if the game is over or not and user's score.
        return game_over, self.score

    def _is_collision(self):
        """
        Checks if the collision is happened or not.
        :return: (bool)
        """
        # If hits boundary
        if (self.head.x > self.w - BLOCK_SIZE or self.head.x < 0) or \
                (self.head.y > self.h - BLOCK_SIZE or self.head.y < 0):
            return True

        # If hits self
        if self.head in self.snake[1:]:
            return True

        return False

    def _update_ui(self):
        """
        Updates the user interface of the pygame display. Order is important!

        """
        self.display.fill(BLACK)

        # Draw the snake
        for pt in self.snake:
            # Rectangle for the snake, BLOCK_SIZExBLOCK_SIZE sized.
            pygame.draw.rect(self.display, BLUE1, pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE))
            # 12 x 12 light blue +4, +4 coordinate of x and y.
            pygame.draw.rect(self.display, BLUE2, pygame.Rect(pt.x + 4, pt.y + 4, 12, 12))

        # Draw the food
        pygame.draw.rect(self.display, RED, pygame.Rect(self.food.x, self.food.y, BLOCK_SIZE, BLOCK_SIZE))

        # Draw the score on the upper left.
        text = font.render("Score: " + str(self.score), True, WHITE)
        self.display.blit(text, [0, 0])
        pygame.display.flip()  # updating the full display

    def _move(self, direction):
        """
        Controls the movement of the snake.
        :param direction: (Direction) enum class object for the predetermined directions

        """
        # Extract x and y coordinates of the head
        x, y = self.head.x, self.head.y
        if direction == Direction.RIGHT:
            x += BLOCK_SIZE
        elif direction == Direction.LEFT:
            x -= BLOCK_SIZE
        elif direction == Direction.DOWN:  # Down increases the y.
            y += BLOCK_SIZE
        elif direction == Direction.UP:
            y -= BLOCK_SIZE

        self.head = Point(x, y)


if __name__ == '__main__':
    game = SnakeGame()

    # game loop
    while True:
        game_over, score = game.play_step()

        # break if game over
        if game_over:
            break

    print("Final Score", score)

    # Print the score
    pygame.quit()
