import numpy as np
from PIL import Image

img = Image.open("tanah_mesupar2.png").convert("RGBA")
datas = img.getdata()
arr = np.array(img)

numpy_arr = img.load()


orange = (255, 165, 0, 255)
grey = (150, 150, 150, 255)
transparent = (0, 0, 0, 0)

is_letter = (arr[:, :, 3] != 0) & (arr[:, :, 0] != 255)
is_red = (arr[:, :, 0] == 255) & (arr[:, :, 1] == 0) & (arr[:, :, 2] == 0)

arr = np.zeros(arr.shape, dtype=np.uint8)
arr[is_letter] = grey
arr[is_red] = orange

arr = arr[120:-200, :, :]  # remove the white space on the left and right

# save
img = Image.fromarray(arr)
img.save("../docs/transparent_icon.png")
