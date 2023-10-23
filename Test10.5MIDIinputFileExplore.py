import pygame
import sys
import rtmidi
import random
import math
import mido
import time
import threading
import os
import tkinter as tk
from tkinter import filedialog

import tkinter as tk
from tkinter import filedialog
global mid
def choose_midi_file():
    global mid
    selected_file = filedialog.askopenfilename(filetypes=[("MIDI Files", "*.mid")])
    
    if selected_file:
        print(f"Selected file: {selected_file}")
        mid = mido.MidiFile(selected_file)
        print(mid)
        root.destroy()
        # You can work with the selected MIDI file here

root = tk.Tk()
root.title("Choose MIDI File")

# Calculate the screen width and height
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# Calculate the window's width and height
window_width = 400
window_height = 150

# Center the window on the screen
x = (screen_width - window_width) // 2
y = (screen_height - window_height) // 2

root.geometry(f"{window_width}x{window_height}+{x}+{y}")

# Make the button bigger
button = tk.Button(root, text="Choose MIDI File", command=choose_midi_file, height=3, width=20)
button.pack(pady=20)

def on_closing():
    root.destroy()
    sys.exit()

root.protocol("WM_DELETE_WINDOW", on_closing)  # Close button event

root.mainloop()



pygame.init()
# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
video_infos = pygame.display.Info()
#SCREEN_WIDTH, SCREEN_HEIGHT = video_infos.current_w, video_infos.current_h
BAR_COLOR = (0, 255, 0)
BAR_WIDTH = 9 #for notes make it 9
BAR_MAX_HEIGHT = 600  # Maximum height of the bar
BAR_SPEED = 15
def is_Note(message):
    return message[0][0] == 144

def is_On(message):
    return message[0][2] != 0
def process_midi_messages():
    for message in mid:
        time.sleep(message.time)
        if not message.is_meta:
            msg = message
            outputPort.send(message)
            #print("yuh")
            if msg.type == 'note_on' or msg.type == 'note_off':
                if  msg.velocity > 0:#msg.type == 'note_on':
                    expanding_bars[msg.note-21][0].expanding = True
                    expanding_bars[msg.note-21][1] = msg.velocity


                elif msg.velocity == 0:#msg.type == 'note_off':
                    expanding_bars[msg.note-21][0].expanding = False
                    expanding_bars[msg.note-21][1] = msg.velocity
def map_midi_velocity_to_intensity(velocity):
    # MIDI velocity ranges from 0 to 127
    # Map it to a range of 0 to 255 using a logistic function
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
BAR_SPEED = 7
class ExpandingBottomBar:
    def __init__(self, x, y):
        self.x = x
        self.bottom_y = y
        self.height = 0
        self.expanding = False
        self.color = (0, 255, 0)
        self.particles = []

    def expand(self, velocity):
        self.color = (50, map_midi_velocity_to_intensity(velocity), 50)
        if self.height < BAR_MAX_HEIGHT:
            self.height += BAR_SPEED
            # Create particles when expanding
            for _ in range(10):
                particle_x = random.uniform(self.x, self.x + BAR_WIDTH)
                particle_y = random.uniform(self.bottom_y - self.height, self.bottom_y)
                particle_color = self.color
                particle_velocity = random.uniform(1, 5)
                particle_lifetime = random.randint(30, 90)  # Random lifetime between 1 and 3 seconds
                self.particles.append(Particle(particle_x, particle_y, particle_color, particle_velocity, particle_lifetime, 'up'))

    def shrink(self):
        if self.height > 0:
            self.height -= BAR_SPEED * 7
            # Create fading particles when shrinking
            for _ in range(10):
                particle_x = random.uniform(self.x, self.x + BAR_WIDTH)
                particle_y = random.uniform(self.bottom_y - self.height, self.bottom_y)
                particle_color = self.color
                particle_velocity = random.uniform(0.1, 2)
                particle_lifetime = random.randint(30, 90)  # Random lifetime between 1 and 3 seconds
                self.particles.append(Particle(particle_x, particle_y, particle_color, particle_velocity, particle_lifetime, 'up'))

    def update_particles(self):
        new_particles = []
        for particle in self.particles:
            particle.move()
            if particle.lifetime > 0:
                new_particles.append(particle)
        self.particles = new_particles

    def draw(self, screen):
        self.update_particles()
        for particle in self.particles:
            particle.draw(screen)
        pygame.draw.rect(screen, self.color, (self.x, self.bottom_y - self.height, BAR_WIDTH, self.height))


PARTICLE_MAX_SPEED = 5
PARTICLE_MAX_RADIUS = 5
PARTICLE_MAX_LIFETIME = 60
class ExpandingMiddleBar:
    def __init__(self, x):
        self.middle_x = x
        self.expanding = False
        self.height = 0
        self.color = (0, 255, 0)
        self.particles_up = []  # List for particles moving upwards
        self.particles_down = []  # List for particles moving downwards

    def expand(self, velocity):
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
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE| pygame.SCALED) #pygame.RESIZABLE | pygame.SCALED)
pygame.display.set_caption("Expanding Bars")


# List to hold the expanding bars
#expanding_bars = [[bar1, 0], [bar2, 0], [bar3, 0]] #bar, velocity
expanding_bars = [[ExpandingBottomBar(9*(i-20), SCREEN_HEIGHT), 0] for i in range(21,109)]
expanding_bars = [[ExpandingMiddleBar(9*(i-20)), 0] for i in range(21,109)]
# Main game loop
running = True
clock = pygame.time.Clock()
midiin = rtmidi.MidiIn()
ports = range(midiin.get_port_count())
pedalOn = False #this is a boolean if pedal is on

if ports[0]: #if midi has inputport
    midiin.open_port(0)
    while running:
        m = midiin.get_message()
        
        if m:
            if m[0][2] > 0:
                expanding_bars[m[0][1] - 21][0].expanding = True
                expanding_bars[m[0][1] - 21][1] = m[0][2]
            elif m[0][2] == 0:
                expanding_bars[m[0][1] - 21][0].expanding = False
                expanding_bars[m[0][1] - 21][1] = m[0][2]

            else: #pedal
                if is_On(m):
                    pedalOn = True
                else:
                    pedalOn = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("quit")
                running = False
                midiin.close_port()
            
        # Update the expanding bars
        for bar in expanding_bars:
            if bar[0].expanding:
                bar[0].expand(bar[1]) #bar[0] is actual bar object, bar[1] is the velocity
            else:
                bar[0].shrink()

        # Clear the screen
        if pedalOn:
            screen.fill((random.randint(0,255),random.randint(0,255),random.randint(0,255)))
        else:
            screen.fill((0, 0, 0))

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
else:
    #print("bros")

    outputPorts = mido.get_output_names()
    outputPort = mido.open_output(outputPorts[1])
    #print("bros2")

    # Create a thread for MIDI processing
    midi_thread = threading.Thread(target=process_midi_messages)
    midi_thread.start()
    # Main loop
    running = True
    pedalOn = False  # Your pedal state variable

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False


        # Update the expanding bars
        for bar in expanding_bars:
            if bar[0].expanding:
                bar[0].expand(bar[1])
            else:
                bar[0].shrink()
                

        # Clear the screen
        if pedalOn:
            screen.fill((random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
        else:
            screen.fill((0, 0, 0))

        # Draw the expanding bars
        for bar in expanding_bars:
            bar[0].draw(screen)

        # Update the display
        pygame.display.flip()

        # # Start the MIDI processing thread (if not already started)
        # if not midi_thread.is_alive():
        #     midi_thread.start()

        # Limit the frame rate
        clock.tick(60)



    # Quit Pygame
    pygame.quit()
    os._exit(1)
    midi_thread.join()
    sys.exit(0)

    


