import pygame
import sys
import rtmidi
import random
import math

# Initialize pygame
pygame.init()


# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BAR_COLOR = (0, 255, 0)
BAR_WIDTH = 9  # for notes make it 9
BAR_MAX_HEIGHT = 600  # Maximum height of the bar
BAR_SPEED = 7
PARTICLE_MAX_SPEED = 5
PARTICLE_MAX_RADIUS = 5
PARTICLE_MAX_LIFETIME = 60

def is_Note(message):
    return message[0][0] == 144

def is_On(message):
    return message[0][2] != 0

def map_midi_velocity_to_intensity(velocity):
    return int(255 / (1 + math.exp(-(velocity - 64) / 16)))

class Particle:
    def __init__(self, x, y, color, velocity, lifetime, direction):
        self.x = x
        self.y = y
        self.color = color
        self.velocity = velocity
        self.lifetime = lifetime
        self.direction = direction  # 'up' or 'down'

    def move(self):
        if self.direction == 'up':
            self.y -= self.velocity
        else:
            self.y += self.velocity
        self.lifetime -= 1

    def draw(self, screen):
        alpha_surface = pygame.Surface((3, 3), pygame.SRCALPHA)
        alpha = int(255 * self.lifetime / 90)  # Fade away over the particle's lifetime
        final_color = self.color + (alpha,)
        pygame.draw.circle(alpha_surface, final_color, (1, 1), 2)
        screen.blit(alpha_surface, (int(self.x), int(self.y)))

class ExpandingMiddleBar:
    def __init__(self, x):
        self.middle_x = x
        self.expanding = False
        self.height = 0
        self.color = (0, 255, 0)
        self.particles_up = []  # List for particles moving upwards
        self.particles_down = []  # List for particles moving downwards

    def expand(self, velocity):
        #self.color = (map_midi_velocity_to_intensity(velocity), map_midi_velocity_to_intensity(velocity), map_midi_velocity_to_intensity(velocity)*0.7)
        self.color = ( abs(70-map_midi_velocity_to_intensity(velocity)*0.3), abs(30-map_midi_velocity_to_intensity(velocity)),  map_midi_velocity_to_intensity(velocity))
        
        if self.height < (SCREEN_HEIGHT // 2):
            self.height += BAR_SPEED

            # Create particles when expanding (upward)
            for _ in range(10):
                particle_x = random.uniform(self.middle_x - BAR_WIDTH // 2, self.middle_x + BAR_WIDTH // 2)
                particle_y = random.uniform((SCREEN_HEIGHT // 2) - self.height, (SCREEN_HEIGHT // 2))
                particle_color = self.color
                particle_velocity = random.uniform(1, PARTICLE_MAX_SPEED)
                particle_lifetime = random.randint(30, PARTICLE_MAX_LIFETIME)
                self.particles_up.append(Particle(particle_x, particle_y, particle_color, particle_velocity, particle_lifetime, 'up'))

            # Create particles when expanding (downward)
            for _ in range(10):
                particle_x = random.uniform(self.middle_x - BAR_WIDTH // 2, self.middle_x + BAR_WIDTH // 2)
                particle_y = random.uniform((SCREEN_HEIGHT // 2), (SCREEN_HEIGHT // 2) + self.height)
                particle_color = self.color
                particle_velocity = random.uniform(1, PARTICLE_MAX_SPEED)
                particle_lifetime = random.randint(30, PARTICLE_MAX_LIFETIME)
                self.particles_down.append(Particle(particle_x, particle_y, particle_color, particle_velocity, particle_lifetime, 'down'))

    def shrink(self):
        if self.height > 0:
            self.height -= BAR_SPEED * 7
            # Create particles when expanding (upward)
            for _ in range(10):
                particle_x = random.uniform(self.middle_x - BAR_WIDTH // 2, self.middle_x + BAR_WIDTH // 2)
                particle_y = random.uniform((SCREEN_HEIGHT // 2) - self.height, (SCREEN_HEIGHT // 2))
                particle_color = self.color
                particle_velocity = random.uniform(1, PARTICLE_MAX_SPEED)
                particle_lifetime = random.randint(30, PARTICLE_MAX_LIFETIME)
                self.particles_up.append(Particle(particle_x, particle_y, particle_color, particle_velocity, particle_lifetime, 'up'))

            # Create particles when expanding (downward)
            for _ in range(10):
                particle_x = random.uniform(self.middle_x - BAR_WIDTH // 2, self.middle_x + BAR_WIDTH // 2)
                particle_y = random.uniform((SCREEN_HEIGHT // 2), (SCREEN_HEIGHT // 2) + self.height)
                particle_color = self.color
                particle_velocity = random.uniform(1, PARTICLE_MAX_SPEED)
                particle_lifetime = random.randint(30, PARTICLE_MAX_LIFETIME)
                self.particles_down.append(Particle(particle_x, particle_y, particle_color, particle_velocity, particle_lifetime, 'down'))

    def update_particles(self):
        new_particles_up = []
        new_particles_down = []
        for particle in self.particles_up:
            particle.move()
            if particle.lifetime > 0:
                new_particles_up.append(particle)
        self.particles_up = new_particles_up

        for particle in self.particles_down:
            particle.move()
            if particle.lifetime > 0:
                new_particles_down.append(particle)
        self.particles_down = new_particles_down

    def draw(self, screen):
        self.update_particles()
        for particle in self.particles_up:
            particle.draw(screen)
        for particle in self.particles_down:
            particle.draw(screen)

        top_y = (SCREEN_HEIGHT // 2) - self.height
        bottom_y = (SCREEN_HEIGHT // 2) + self.height
        pygame.draw.rect(screen, self.color, (self.middle_x - BAR_WIDTH // 2, top_y, BAR_WIDTH, 2 * self.height))

    def setColor(self, color):
        self.color = color

# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE | pygame.SCALED)
pygame.display.set_caption("Expanding Bars")

# List to hold the expanding bars
expanding_bars = [[ExpandingMiddleBar(9 * (i - 20)), 0] for i in range(21, 109)]

# Main game loop
running = True
clock = pygame.time.Clock()
midiin = rtmidi.MidiIn()
ports = range(midiin.get_port_count())
pedalOn = False  # This is a boolean if the pedal is on

if ports:  # If MIDI has a port
    midiin.open_port(0)
    while running:
        m = midiin.get_message()
#144 , 128
        if m:
            print(m)
            if m[0][2] > 0:
                expanding_bars[m[0][1] - 21][0].expanding = True
                expanding_bars[m[0][1] - 21][1] = m[0][2]
            elif m[0][2] == 0:
                expanding_bars[m[0][1] - 21][0].expanding = False
                expanding_bars[m[0][1] - 21][1] = m[0][2]

            else:  # Pedal
                if is_On(m):
                    pedalOn = True
                else:
                    pedalOn = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                midiin.close_port()

        # Update the expanding bars
        for bar in expanding_bars:
            if bar[0].expanding:
                bar[0].expand(bar[1])
            else:
                bar[0].shrink()

        # Clear the screen
        if pedalOn:
            screen.fill((20, 100, random.randint(89, 127)))
        else:
            #screen.fill((20, 100, 80))
            screen.fill((0,0,0))

        # Draw the expanding bars
        for bar in expanding_bars:
            bar[0].draw(screen)

        # Update the display
        pygame.display.flip()

        # Limit the frame rate
        clock.tick(60)

    # Quit the game
    pygame.quit()
    sys.exit()
