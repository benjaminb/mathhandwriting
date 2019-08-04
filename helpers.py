import os, re
import PIL
import xml.etree.ElementTree as ET
import numpy as np
from matplotlib import image
from inkml2img import inkml2img

def generate_dataset(filelist):
    labels = []
    labels, ok_files, problem_files = extract_labels(filelist)
    print('Problem files:', len(problem_files))
    labels, ok_files, more_problems = generate_images(ok_files, labels)
    problem_files.extend(more_problems)

    return labels, ok_files, problem_files

def create_image_path(inkml_path):
    img_path = re.sub(r'data/', '', inkml_path)
    img_path = re.sub(r'/', '_', img_path)
    img_path = re.sub(r'.inkml', '', img_path)
    img_path = 'images/' + img_path + '.png'
    return img_path


def extract_labels(inkml_files):
    labels, successes, failures = [], [], []

    for file in inkml_files:
        try:
            label = get_label(file)
        except:
            print('Could not get label of', file)
            failures.append(file)
            continue

        # Successfully retrieved a label
        labels.append(label)
        successes.append(file)
    print('Labels {}, Successes {}'.format(len(labels), len(successes)))
    if len(labels) != len(successes):
        print("Not equal!")
    return labels, successes, failures

def generate_images(inkml_files, labels):
    successes, failures, to_delete = [], [], []

    print('{} files and {} labels'.format(len(inkml_files), len(labels)))

    for i, infile in enumerate(inkml_files):
        print('index:', i)
        # Create a unique filename
        outfile = create_image_path(infile)
        try:
            inkml2img(infile, outfile)
        except:
            # print('Could not convert', infile)
            failures.append(infile)
            # Delete the label so files & labels stay synced
            to_delete.append(i)
            # del labels[i]
            continue

        # Update globals
        successes.append(outfile)
        print('Converted', outfile)

    for i in sorted(to_delete, reverse=True):
        print('deleting labels index', i)
        del labels[i]
        
    return labels, successes, failures

# Gets the latex label from the tree of a parsed inkml file
def get_label(file):
    root = ET.parse(file).getroot()
    ANNOTATION = '{http://www.w3.org/2003/InkML}annotation'

    for node in root.findall(ANNOTATION):

        if node.get('type') == 'truth':
            label = node.text
            # Strip off $'s
            label = re.sub(r"^\$", '', label)
            label = re.sub(r'\$$', '', label)
            return label

    return None



def get_max_dims(image_paths):
    heights = [image.imread(file).shape[0] for file in image_paths]
    widths = [image.imread(file).shape[1] for file in image_paths]
    return max(heights), max(widths)

def process_images(image_paths):
    max_dims = get_max_dims(image_paths)
    img_arrays = []

    for path in image_paths:
        # Convert to grayscale
        TEMP_FILE = 'temp_gs_conversion.png'

        img = PIL.Image.open(path)
        gs_img = img.convert(mode='L')
        gs_img.save(TEMP_FILE)

        # Convert to np.array
        img_array = image.imread(TEMP_FILE)
        img_array = normalize_image_dims(arr=img_array, max_dims=max_dims)
        img_array = img_array.astype('float32')
        img_arrays.append(img_array)
        os.remove(TEMP_FILE)

    return img_arrays


def normalize_image_dims(arr, max_dims):
    shape = arr.shape

    for i in range(2):
        diff = max_dims[i] - shape[i]
        if diff != 0:
            size = [0, 0]
            size[i] = diff
            size[1-i] = max_dims[1-i]

            arr = np.append(arr, np.ones(size), axis=i)

    return arr
