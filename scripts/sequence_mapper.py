import os

from functools import reduce
from math import floor
from re import match
from shutil import copyfile
from PIL import Image

MAX_BATCHES = '$MAX_BATCHES'
CLASSES = '$CLASSES'
STEPS = '$STEPS'
FILTERS = '$FILTERS'

def convert_rect(rects, size):
  img_width, img_height = size

  center_x = (rects[0] + (rects[2] - rects[0]) / 2) / img_width
  width = (rects[2] - rects[0]) / img_width
  center_y = (rects[3] + (rects[5] - rects[3]) / 2) / img_height
  height = (rects[5] - rects[3]) / img_height

  return [center_x, center_y, width, height]

def convert_dataset(classes_lines):
  print('converting dataset')

  os.mkdir('./data')
  os.mkdir('./data/obj')

  for (line_order, line) in enumerate(classes_lines):
    name = line.strip()
    with open(f'./sequences/{name}/groundtruth.txt', 'r') as ground_truth_f:
      rects = [
        [float(val) for val in line.strip().split(',')]
        for line in ground_truth_f.readlines()
      ]

      for (image_order, image) in enumerate(os.listdir(f'./sequences/{name}/color')):
        im = Image.open(f'./sequences/{name}/color/{image}')
        im_size = im.size
        im.close()

        new_name = match('(.+)\.jpg', f'{name}__{image}').group(1)
        print(new_name)

        copyfile(f'./sequences/{name}/color/{image}', f'./data/obj/{new_name}.jpg')

        with open(f'./data/obj/{new_name}.txt', 'w+') as image_txt_f:
          rect_data = " ".join(
            [str(val) for val in convert_rect(rects[image_order], im_size)]
          )

          image_txt_f.write(f'{line_order} {rect_data}')

          print('done!')

def create_obj_data(classes_lines):
  print('creating obj.data')

  with open(f'./data/obj.data', 'w+') as obj_data_f:
    obj_data_f.write(
f'classes = {len(classes_lines)}\n\
train = data/train.txt\n\
valid = data/test.txt\n\
names = data/obj.names\n\
backup = backup')

    print('done!')

def create_obj_names(classes_lines):
  print('creating obj.names')

  with open(f'./data/obj.names', 'w+') as obj_names_f:
    obj_names_f.writelines(classes_lines)

    print('done!')

def group_images_filenames(accum, name):
  match_result = match('(\\w+)__.+\\.jpg', name)

  if match_result is not None:
    group_name = match_result.group(1)

    try:
      accum[group_name].append(name)
    except KeyError:
      accum[group_name] = []
    
  return accum

# split_ratio = train / all
def split_dataset(split_ratio):
  print('spliting dataset')

  train_txt_f = open('./data/train.txt', 'w+')
  test_txt_f = open('./data/test.txt', 'w+')

  grouped_imgs = reduce(group_images_filenames, os.listdir(f'./data/obj'), {})

  for (class_name, images) in grouped_imgs.items():
    lines = ['./data/obj/' + img + '\n' for img in images]
    slice_length = floor(len(lines) * split_ratio)

    train_txt_f.writelines(lines[:slice_length])
    test_txt_f.writelines(lines[slice_length:])

  train_txt_f.close()
  test_txt_f.close()

  print('done!')

def create_yolo_cfg(template_src, out_src, classes_lines):
  yolo_template_f = open(template_src, 'r')
  yolo_cfg_f = open(out_src, 'w+')

  config = yolo_template_f.readlines()
  classes_count = len(classes_lines)
  max_batches = classes_count * 2000

  for line in config:
    line = line.replace(MAX_BATCHES, str(max_batches))
    line = line.replace(STEPS, f'{floor(max_batches * 0.8)},{floor(max_batches * 0.9)}')
    line = line.replace(CLASSES, str(classes_count))
    line = line.replace(FILTERS, str((classes_count + 5) * 3))

    yolo_cfg_f.write(line)

  yolo_template_f.close()
  yolo_cfg_f.close()


def main():
  classes_f = open('./sequences/list.txt', 'r')
  classes_lines = classes_f.readlines()
  classes_f.close()

  # create_yolo_cfg(
  #   template_src='./yolo-obj.template.cfg',
  #   out_src='./yolo-obj.cfg',
  #   classes_lines=classes_lines
  # )

  # convert_dataset(classes_lines)
  # create_obj_data(classes_lines)
  # create_obj_names(classes_lines)
  split_dataset(split_ratio = 0.8)

main()