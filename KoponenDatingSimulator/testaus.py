import os, shutil, pygame, math, concurrent.futures, time

pygame.init()
main_display = pygame.display.set_mode((600,600))

angle = 45

k = 0

p1 = (0,0)
p2 = (1,2)

k = (p2[1] - p1[1])/(p2[0]- p1[0])

print(round(math.tan(math.radians(angle))))

print("ssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssss")

def sleep(value):
    print(f"Sleeping {value} seconds")
    time.sleep(value)
    print("Done sleeping")

with concurrent.futures.ThreadPoolExecutor() as executor:
    for _ in range(10):
        thread = executor.submit(sleep, 1)
    
print("All done")
