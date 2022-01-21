from math import floor

MAX_BATCHES = '$MAX_BATCHES'
CLASSES = '$CLASSES'
STEPS = '$STEPS'
FILTERS = '$FILTERS'

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

  create_yolo_cfg(
    template_src='./templates/yolo-obj.template.cfg',
    out_src='./yolo-obj.cfg',
    classes_lines=classes_lines
  )

main()