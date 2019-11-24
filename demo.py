import requests
from PIL import Image

from autoaugment import RandAugment

url = "https://images.pexels.com/photos/356378/pexels-photo-356378.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940"
img = Image.open(requests.get(url, stream=True).raw)
img.show()
random_transform = RandAugment()
for i in range(10):
    img_ = random_transform(img)
    img_.show()
