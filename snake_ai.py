import pygame
import random
from enum import Enum
from collections import namedtuple
import numpy as np

pygame.init()
font = pygame.font.Font('arial.ttf', 25)


# reset function
# reward
# play(action) -> direction
# game_iteration
# is_collision


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


class SnakeGameAI:
    def __init__(self, w=640, h=480):
        self.w = w
        self.h = h

        # init display
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('Snake')
        self.clock = pygame.time.Clock()  # This is for controlled gaming speed.
        self.reset()

    def reset(self):
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
        self.frame_iteration = 0

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

    def play_step(self, action):
        """
        Controls the game via the user's input.
        :return: score (int)
        """
        self.frame_iteration += 1
        # This for loop gets all the events from the user, within ONE play_step invoke.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()  # exit our Python program

        # Move the snake
        self._move(action)  # update the head
        self.snake.insert(0, self.head)  # insert the new head at the beginning of the list of snake.

        # Check if the game is over, quit if this is the case
        reward = 0
        game_over = False
        if self.is_collision() or self.frame_iteration > 100 * len(
                self.snake):  # If game time is greater than 100 x length of the snake.
            game_over = True
            reward = -10
            return reward, game_over, self.score

        # Place new food or just move
        if self.head == self.food:
            self.score += 1
            reward = 10
            self.speed += 2
            self._place_food()
        else:
            self.snake.pop()  # removes the last element of our snake. Because we have inserted one at the beginning.

        # Update the pygame ui and clock
        self._update_ui()
        self.clock.tick(self.speed)

        # Return if the game is over or not and user's score.
        return reward, game_over, self.score

    def is_collision(self, pt=None):  # needs to be public because Agent should access this.
        """
        Checks if the collision is happened or not.
        :return: (bool)
        """
        if pt is None:
            pt = self.head
        # If hits boundary
        if (pt.x > self.w - BLOCK_SIZE or pt.x < 0) or \
                (pt.y > self.h - BLOCK_SIZE or pt.y < 0):
            return True

        # If hits self
        if pt in self.snake[1:]:
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

    def _move(self, action):
        # [straight, right, left]

        # All possible directions in a clockwise order
        clockwise = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
        idx = clockwise.index(self.direction)

        # Go straight, keep current direction
        if np.array_equal(action, [1, 0, 0]):
            new_dir = clockwise[idx]  # no change
        elif np.array_equal(action, [0, 1, 0]):
            next_idx = (idx + 1) % 4
            new_dir = clockwise[next_idx]  # Right turn r -> d -> l -> u
        else:  # [0, 0, 1]
            next_idx = (idx - 1) % 4  # go counter clockwise
            new_dir = clockwise[next_idx]  # Left turn r -> u -> l -> d

        self.direction = new_dir

        # Extract x and y coordinates of the head
        x, y = self.head.x, self.head.y
        if self.direction == Direction.RIGHT:
            x += BLOCK_SIZE
        elif self.direction == Direction.LEFT:
            x -= BLOCK_SIZE
        elif self.direction == Direction.DOWN:  # Down increases the y.
            y += BLOCK_SIZE
        elif self.direction == Direction.UP:
            y -= BLOCK_SIZE

        self.head = Point(x, y)
