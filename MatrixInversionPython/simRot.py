import zmq
import pickle
import pygame
import numpy as np
from noise import pnoise1
import time

def init_pygame(screen_width:float, screen_height:float):
    # Initialize Pygame
    pygame.init()
    pygame.display.set_caption("Simulation")
    return pygame.display.set_mode((screen_width, screen_height))

def rotate_point(point:np.ndarray, angle:float) -> np.ndarray:
    """Rotate a point around the origin (0, 0) by the given angle."""
    rotation_matrix = np.array([
        [np.cos(angle), -np.sin(angle)],
        [np.sin(angle), np.cos(angle)]
    ])
    return np.dot(rotation_matrix, point)

def draw_rotated_polygon(surface:pygame.Surface, color:tuple, center:np.ndarray, angle:float, sz:int = 50) -> None:
    """Draw a rotated polygon."""
    corners = [
        np.array([sz, 0]),
        np.array([-sz/2, sz/2]),
        np.array([0, 0]),
        np.array([-sz/2, -sz/2])
    ]

    rotated_corners = [rotate_point(corner, angle) + center for corner in corners]
    pygame.draw.polygon(surface, color, rotated_corners)


def display_text(surface, text, position, font):
    """Display multiline text on the screen."""
    lines = text.split('\n')
    y_offset = 0
    for line in lines:
        text_surface = font.render(line, True, davys_gray)
        surface.blit(text_surface, (position[0], position[1] + y_offset))
        y_offset += font.get_linesize()

if __name__ == '__main__':
    screen_width = 250
    screen_height = 300
    screen = init_pygame(screen_width, screen_height)

    # Colors
    white = (255, 255 , 255)
    black = (0, 0, 0)
    davys_gray = (80, 81, 79)
    space_cadet = (40, 48, 68)

    # Polygon
    p_center = np.array([screen_width // 2, screen_height * 3 // 4])
    angle = 0

    # Font for text
    fontSmall = pygame.font.SysFont(None, 32)
    fontBig = pygame.font.SysFont(None, 80)

    # Perlin noise parameters
    time_ = 0
    time_increment = 0.01

    # Initialize ZMQ comms
    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    # socket.setsockopt(zmq.SNDHWM, 0)
    socket.bind("tcp://*:12345")

    clock = pygame.time.Clock()
    hz = 100
    # Main game loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Update the angle using Perlin noise
        angle = pnoise1(time_*0.08) * 2 * np.pi  # Scale the noise value to a full rotation range
        # angle = np.sin(time_*10) * 2 * np.pi
        # angle = time_
        time_ += time_increment

        # Clear the screen
        screen.fill(white)

        # Draw the rotated rectangle
        draw_rotated_polygon(screen, space_cadet, p_center, angle)

        A = np.array([
            [np.cos(angle), -np.sin(angle)],
            [np.sin(angle), np.cos(angle)]
        ])

        # Send zmq data
        data = pickle.dumps(A)
        socket.send(data)


        # Display multiline text
        multiline_text = f"{A[0,0]: >7.2f}  {A[0,1]: >7.2f}\n{A[1,0]: >7.2f}  {A[1,1]: >7.2f}"
        display_text(screen, "R(t) = ", (10, 30), fontSmall)
        display_text(screen, multiline_text, (75, 20), fontSmall)
        display_text(screen, "(        )", (70, 15), fontBig)

        # Update the display
        pygame.display.flip()
        clock.tick(hz)

    socket.close()
    context.term()

    # Quit Pygame
    pygame.quit()
