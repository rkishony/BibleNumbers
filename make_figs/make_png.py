from PIL import Image

img = Image.open("TanahMesupar.png").convert("RGBA")
datas = img.getdata()

orange = (255, 165, 0, 255)
grey = (150, 150, 150, 255)
transparent = (0, 0, 0, 0)
new_data = []
for item in datas:
    # Assume background is near-black (e.g., RGB < 30)
    if item[0] > item[2] * 2:
        new_data.append(orange)
    elif item[0] > 100 and item[1] > 100 and item[2] > 100:
        new_data.append(grey)
    else:
        new_data.append(transparent)

img.putdata(new_data)
img.save("transparent_icon.png")
