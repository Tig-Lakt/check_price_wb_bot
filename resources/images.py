import os
import sys

project_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_path)

from aiogram.types import FSInputFile

# Определение базового каталога для изображений
IMAGES_DIR = os.path.join(project_path, 'data', 'images')

# Создайте пути к файлам, используя os.path.join для кросс-платформенной совместимости.
img_clean_agile = FSInputFile(os.path.join(IMAGES_DIR, 'clean_agile.jpg'))
img_clean_architecture = FSInputFile(os.path.join(IMAGES_DIR, 'clean_architecture.jpg'))
img_clean_code = FSInputFile(os.path.join(IMAGES_DIR, 'clean_code.jpg'))
img_ideal_job = FSInputFile(os.path.join(IMAGES_DIR, 'ideal_job.jpg'))
img_ideal_programmer = FSInputFile(os.path.join(IMAGES_DIR, 'ideal_programmer.jpg'))

images = {
  "6411515": img_ideal_programmer,
  "6034394": img_clean_code,
  "5417786": img_clean_architecture,
  "12989895": img_clean_agile,
  "94341513": img_ideal_job
}