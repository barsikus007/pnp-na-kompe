from pathlib import Path

from PIL import Image
from PIL import ImageFile

from src.models.file import FileBase
from src.models.image import Image as ImageDB
from src.schemas.image import ImageSizes


ImageFile.LOAD_TRUNCATED_IMAGES = True
files_folder = Path("./files")


def resize_image(path: Path):
    sizes = ImageSizes()
    with Image.open(path) as img:
        width, height = img.size
        old_size = max(width, height)
        if old_size > 2560:
            filename = path.with_name(path.with_suffix("").name + "_2560" + path.suffix)
            img_2560 = img.copy()
            img_2560.thumbnail((2560, 2560), Image.ANTIALIAS)
            img_2560.save(filename)
            sizes.size_2560 = str(filename)
            del img_2560
        if old_size > 1920:
            filename = path.with_name(path.with_suffix("").name + "_1920" + path.suffix)
            img_1920 = img.copy()
            img_1920.thumbnail((1920, 1920), Image.ANTIALIAS)
            img_1920.save(filename)
            sizes.size_1920 = str(filename)
            del img_1920
        if old_size > 1280:
            filename = path.with_name(path.with_suffix("").name + "_1280" + path.suffix)
            img_1280 = img.copy()
            img_1280.thumbnail((1280, 1280), Image.ANTIALIAS)
            img_1280.save(filename)
            sizes.size_1280 = str(filename)
            del img_1280
    return width, height, sizes


def generate_sizes(image: ImageDB, file: FileBase):
    path = Path(file.path)
    sizes = ImageSizes()
    old_size = max(map(int, image.size.split('x')))
    if old_size > 2560:
        filename = path.with_name(path.with_suffix("").name + "_2560" + path.suffix)
        sizes.size_2560 = str(filename)
    if old_size > 1920:
        filename = path.with_name(path.with_suffix("").name + "_1920" + path.suffix)
        sizes.size_1920 = str(filename)
    if old_size > 1280:
        filename = path.with_name(path.with_suffix("").name + "_1280" + path.suffix)
        sizes.size_1280 = str(filename)
    return sizes
