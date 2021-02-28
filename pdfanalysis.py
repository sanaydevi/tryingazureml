import fitz
import io
from PIL import Image
from google.cloud import vision
import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="My Project-1e4ce3b18f75.json"
def detect_text(path):
    """Detects text in the file."""
    # check if pdf

    flag = 0
    client = vision.ImageAnnotatorClient()

    with io.open(path, 'rb') as image_file:
        content = image_file.read()

    image = vision.Image(content=content)

    response = client.text_detection(image=image)
    texts = response.text_annotations
    print('Texts:')

    for text in texts:
        print('\n"{}"'.format(text.description))

        vertices = (['({},{})'.format(vertex.x, vertex.y)
                    for vertex in text.bounding_poly.vertices])
        if len(vertices) > 0:
            flag += 1
        print('bounds: {}'.format(','.join(vertices)))

    if response.error.message:
        raise Exception(
            '{}\nFor more info on error messages, check: '
            'https://cloud.google.com/apis/design/errors'.format(
                response.error.message))
    return flag


def seperatePDF(file):
    pdf_file = fitz.open(file)
    #file1 = open("textFileGenerated/OutputText.txt", "w")
    scoreImage = 0
    for page_index in range(len(pdf_file)):
        # get the page itself
        page = pdf_file[page_index]
        text = page.get_textpage().extractText()
        #file1.write(text)
        filepciScore = 0
        image_list = page.getImageList()
        if image_list:
            print(f"[+] Found a total of {len(image_list)} images in page {page_index}")
        else:
            print("[!] No images found on page", page_index)
        for image_index, img in enumerate(page.getImageList(), start=1):
            xref = img[0]
            print(xref)
            print("-------")
            # extract the image bytes
            base_image = pdf_file.extractImage(xref)
            image_bytes = base_image["image"]
            # get the image extension
            image_ext = base_image["ext"]
            # load it to PIL
            image = Image.open(io.BytesIO(image_bytes))
            # save it to local disk
            image.save(open(f"images/image{page_index+1}_{image_index}.{image_ext}", "wb"))
            scoreImage += detect_text(f"images/image{page_index+1}_{image_index}.{image_ext}")
    return filepciScore,scoreImage

