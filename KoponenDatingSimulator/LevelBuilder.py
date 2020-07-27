import os, pygame
from pygame.locals import *
import threading

pygame.init()
display_size = (1600, 800)

main_display = pygame.display.set_mode(display_size)
pygame.display.set_caption("KDS Level Builder")
main = True

inputThread_running = False

def inputThread():
    global inputThread_running, main
    inputThread_running = True
    data = input("input -->  ")

    print("Your data: " + data)
    inputThread_running = False
    if not main:
        inputThread_running = False

while main:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            main = False
            inputThread_running = True
            thread._stop()

    if not inputThread_running and main == True:
        thread = threading.Thread(target=inputThread)
        thread.start()