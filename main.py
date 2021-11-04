
from os import path
import numpy as np
import matplotlib.pyplot as plt
import pickle

from galaxyNumberCount.colouredPrint import printC, bcolors
from galaxyNumberCount import core

ROOT_PATH = path.dirname(__file__)
MOSIC_PATH = path.join(ROOT_PATH,'ExtragalacticFieldSurvey_A1.fits')
CACHE_PATH = path.join(ROOT_PATH,'FieldImageCache.pickle')

USE_CACHED = True

if USE_CACHED:
    CACHE_PART_MINUS_3_STD = path.join(ROOT_PATH,'FieldImageCache_4000x1000_0_-3std.pickle')
    CACHE_ALL_MINUS_3_STD = path.join(ROOT_PATH,'FieldImageCache_ALL_0_-3std.pickle')
    CACHE_PATH = CACHE_ALL_MINUS_3_STD

### END CONFIG ###

if USE_CACHED:
    with open(CACHE_PATH,'rb') as file:
        img = pickle.load(file)
    img.printBackgroundInfo()
else:
    img = core.FieldImage(MOSIC_PATH)
    img.blackoutRectangleOrMask((slice(1038,3094),slice(2482,-1)))

    img.printSignificanceThresholdInfo()
    img.printBackgroundInfo()

    # img.blackoutRectangleOrMask((slice(0,-1),slice(0,1000)))
    # img.blackoutRectangleOrMask((slice(0,4000),slice(0,-1)))

    img.identifyObjects(
        img.galaxy_significance_threshold + 0 * img.backgroundStd,
        img.galaxy_significance_threshold - 3 * img.backgroundStd
    )
    with open(CACHE_PATH,'wb') as file:
        pickle.dump(img,file)

for object in img.objects:
    object.isDiscarded = False
    
    if object.shape[0] > 50 or object.shape[1] > 50:
        object.isDiscarded = True

    if object.numberPixels > 1 and object.getNaiveBrightness() == 0:
        plt.imshow(object.croppedPixel)
        plt.scatter(*object.localCentreMean)
        plt.scatter(*object.localPeak)
        plt.show()

image = img.image.copy()
image[~img.globalObjectMask] = 0
plt.imshow(np.log(image))
plt.show()

plt.plot(
    *img.brightnessCount().getBrightnessWithoutBackground(),
    marker='',label='Naive | Subtracted background'
)
plt.plot(
    *img.brightnessCount().getBrightnessWithoutLocalBackground(),
    marker='',label='Naive | Subtracted local'
)
plt.plot(
    *img.brightnessCount().getCircularApertureBrightness(15),
    marker='',label='Aperture | Subtracted background'
)
plt.plot(
    *img.brightnessCount().getCircularApertureBrightness(15,'local'),
    marker='',label='Aperture | Local background'
)
plt.xlabel('Brightness')
plt.ylabel('Objects brighter')
plt.yscale('log')
plt.xscale('log')
plt.legend()
plt.tight_layout()
plt.show()

