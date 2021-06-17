from PIL import Image

while True:
    path = input("Enter file path: ")

    with Image.open(path, "r") as im:
        image = im.convert("RGBA")

    pixels = image.load()
    for x in range(image.size[0]):
        for y in range(image.size[1]):
            pxl = pixels[x, y]
            if pxl[3] >= 128:
                pixels[x, y] = (pxl[0], pxl[1], pxl[2], 255)
            else:
                pixels[x, y] = (255, 255, 255, 0)

    image.save(path + "-rmAlpha.png")