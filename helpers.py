import xml.etree.ElementTree as ET
import re
from inkml2img import inkml2img

def generate_dataset(filelist):
    labels = []
    labels, ok_files, problem_files = extract_labels(filelist)
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

    return labels, successes, failures

def generate_images(inkml_files, labels):
    successes = []
    failures = []

    for i, infile in enumerate(inkml_files):
        # Create a unique filename
        outfile = create_image_path(infile)
        try:
            inkml2img(infile, outfile)
        except:
            print('Could not convert', infile)
            failures.append(infile)
            # Delete the label so files & labels stay synced
            del labels[i]
            continue

        # Update globals
        successes.append(outfile)
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

# def make_images_from_valid_labels(Y):
#     to_delete = []
#     for i, y in enumerate(Y):
#         outfile = create_image_path(file)
#         file = y['inkml_path']
#         try:
#             inkml2img(file, outfile)
#         except:
#             print('Could not convert', file)
#             unconvertable.append(i)
#             to_delete.append(i)
#             continue
#
#         # Update globals
#         y.update({'image_path': outfile})


# def remove_invalid_labels(deletions):
#     for i in sorted(deletions, reverse=True):
#         del Y[i]


def get_max_dims(image_paths):
    heights = [image.imread(file).shape[0] for file in image_paths]
    widths = [image.imread(file).shape[1] for file in image_paths]
    return max(heights), max(widths)

def process_images(image_paths):

    for path in image_paths:
        # Convert to grayscale
        TEMP_FILE = 'temp_gs_conversion.png'

        img = PIL.Image.open(path)
        gs_img = img.convert(mode='L')
        gs_img.save(TEMP_FILE)

        # Convert to np.array
        img_array = image.imread(TEMP_FILE)
        img_array = normalize_image_dims(arr=img_array, max_dims=max_dims)
        X.append(img_array)
        os.remove(TEMP_FILE)

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