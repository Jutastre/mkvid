import os, sys, shutil
from tqdm import tqdm
from PIL import Image
import numpy as np
import moviepy.editor as mpy

FPS = 30
FACTOR = 16
SAVE_IMAGES = False
SAVE_VIDEO = True
VERBOSE = True
COSINE = 0.5


def main(argv:list):
    global FPS, FACTOR, VERBOSE
    directoryName = "output" if SAVE_IMAGES else "tmp"
    while len(argv) > 1:
        if argv[0].lower() in ['--fps','-fps','-f']:
            FPS = int(argv[1])
        if argv[0].lower() in ['--interpolationfactor','-i']:
            FACTOR = int(argv[1])
        if argv[0].lower() in ['--cosine','-c']:
            FACTOR = float(argv[1])
        if argv[0].lower() in ['--verbose','-v']:
            VERBOSE = True
        if argv[0].lower() in ['--silent','-s']:
            VERBOSE = False
        argv.pop()
    while len(argv) > 0:
        if argv[0].lower() in ['--verbose','-v']:
            VERBOSE = True
        if argv[0].lower() in ['--silent','-s']:
            VERBOSE = False
        argv.pop()
    #print([2**i for i in range(1,16)])
    if FACTOR not in [2**i for i in range(1,16)]:
        raise Exception
    if not (1 < FPS < 255):
        raise Exception
    if not (0 <= COSINE <= 1):
        raise Exception

    try:
        os.mkdir(directoryName)
    except:
        pass

    if FACTOR != 1:


        allFiles = os.listdir(os.getcwd())
        imageFiles = [filename for filename in allFiles if filename[-4:].lower() == ".png"]

        if not imageFiles:
            print("Error: No png files found!")
            sys.exit(1)

        output = []

        i = 1

        output.append(Image.open(imageFiles[0]))

        for i in tqdm(
            range(1, len(imageFiles)),
            desc="Interpolating",
            leave=True if VERBOSE else False,
        ):

            # while i < len(imagelist):

            lastImage = Image.open(imageFiles[i - 1])
            currentImage = Image.open(imageFiles[i])

            for j in range(FACTOR - 1):
                # print (j)
                linear = (1.0 / FACTOR) * (j + 1)

                cosine = 0.5-(np.cos(linear*np.pi)/2)
                #print(cosine)

                blend = (linear * (1-COSINE)) + (cosine * COSINE)
                # print (blend)
                output.append(Image.blend(lastImage, currentImage, blend))

            output.append(currentImage)
            i += 1

        if VERBOSE:
            print("Finished interpolating")

        n = 0

        for image in tqdm(
            output,
            desc=f"Saving Images in /{directoryName}/",
            leave=True if VERBOSE else False,
        ):
            image.save(
                os.path.join(directoryName, f"{str(n).rjust(8,'0') }.png"), "PNG"
            )
            n += 1
        if VERBOSE:
            print(f"Finished saving images in /{directoryName}/")

    if SAVE_VIDEO:
        print('Saving video...',end='\r')
        if FACTOR != 1:
            allFiles = os.listdir(os.path.join(os.getcwd(), directoryName))
            imagelist = [
                os.path.join(directoryName, filename)
                for filename in allFiles
                if filename[-4:].lower() == ".png"
            ]
        else:
            allFiles = os.listdir(os.getcwd())
            imagelist = [
                filename for filename in allFiles if filename[-4:].lower() == ".png"
            ]

        clip = mpy.ImageSequenceClip(imagelist, fps=FPS)
        clip.write_videofile("output.mp4", verbose=True, logger=None)
        if VERBOSE:
            print("Saved output as output.mp4")

    if not SAVE_IMAGES:
        if VERBOSE:
            print(f"Removing /{directoryName}/")
        shutil.rmtree(directoryName)

    if VERBOSE:
        print(f"Done!")


if __name__ == "__main__":
    main(sys.argv[1:])
