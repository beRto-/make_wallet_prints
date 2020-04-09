import PIL.Image as Image
import math


def resize(size, hwRatio):
    """
    Return the minimum size of image that is at least "size" but
    maintains the provided aspect ratio
    """
    if size[0] * hwRatio > size[1]:
        return (size[0], int(math.ceil(size[0]*hwRatio)))
    else:
        return (int(math.ceil(1.0*size[1] / hwRatio)), size[1])


def cropimage(size, hwRatioCropped):
    """
    Return the size of image that crops image to hwRatioCropped
    while minimizing cropping required.
    Crops evenly from both sides (keeps middle of image).
    """
    if size[0] * hwRatioCropped > size[1]:
        trim = size[0] - size[1]/hwRatioCropped
        #print size[0], size[1], trim
        #print int(math.ceil(trim/2)), 0, int(math.ceil(size[0] - 1.0*trim/2)), size[1]
        return (int(math.ceil(trim/2)), 0, int(math.ceil(size[0] - 1.0*trim/2)), size[1])
    else:
        trim = size[1] - size[0]*hwRatioCropped
        #print size[0], size[1], trim
        #print 0, int(math.ceil(trim/2)), int(math.ceil(size[1] - 1.0*trim/2)), size[0]
        return (0, int(math.ceil(trim/2)), size[0], int(math.ceil(size[1] - 1.0*trim/2)))


def tile(dimensions, src, hwRatio=0.6667, paddingPercent=0.05, 
         borderBg=(255,255,255), pageBg=(0,0,0), outsideBorderPercent=0.1, 
         applyCrop=False):
    """
    Tile an image and return a new image with the resulting tiled image
    with borders and stuff like that.

    dimensions: A tuple in form (width, height) that indicates the
        number of tiles horizontally and vertically in the output image.

    src: A PIL Image object with the source image you wish to tile

    hwRatio: Ratio of height to width required in output image.  Lets
        you create an image with exactly a 4x6 ratio for printing to
        online photo services.

    paddingPercent: Poorly named but this is the border that surrounds
        each image expressed as a fraction of it's width!

    borderBg: a tuple in the form (r,g,b) that provides the border
        color for the images.  ie) you will have a border of this
        color at a width of paddingPercent * sourceImage.width
        around each image.

    pageBg: a tuple in the form (r,g,b) that sets the color for
        the background image.  This will be seen between images
        as well as around the entire image.

    outsideBorderPercent: width of outside border as fraction of
        output image width and height.  This allows for extra
        padding to compensate for poor cropping by photo finishers.

    applyCrop: False if you do not want original image cropped.
        True if you want image cropped to fit exactly and fill photo.

    EG:
        # this tiles an image 2x3 with a 5% red border and saves it
        import Image
        src = Image.load('test.jpg')
        dest = tile((2,3), src, 4.0/6, 0.05, (255,0,0))
        dest.save('test-tiled.jpg')

    """

    nw, nh = dimensions
    iw, ih = src.size

    if applyCrop == True:
        #calculate aspect ratio of image within photo
        #depending on tile orientation, this is not the
        #same as the photo (paper) aspect ratio
        imageRatio = hwRatio * dimensions[0] / dimensions[1]
        src = src.crop(cropimage((iw, ih), imageRatio))
    elif applyCrop == 'SQUARE':
        #print 'square crop requested'
        imageRatio = 1 #square
        src = src.crop(cropimage((iw, ih), imageRatio))

    #print iw, ih
    iw, ih = src.size
    #print iw, ih

    pp = paddingPercent
    # padding is a fraction of the source image size
    pah = int(math.ceil(pp * iw))
    paw = int(math.ceil(pp * iw))
    # optimal image dimensions
    # img = B1+B2+IMG+B2+B1+B2+IMG+B2+B1
    niw = iw * nw + paw * (4+3*(nw-1))
    nih = ih * nh + pah * (4+3*(nh-1))
    # compute min image size that has the correct AR
    fw, fh = resize((niw, nih), hwRatio)
    #print niw,fw, nih,fh
    # outside border as fraction of the total size
    fw = int(fw * (1+ outsideBorderPercent));
    fh = int(fh * (1+ outsideBorderPercent));
    # calculate offsets for the image to center the tiles in the output image
    woff, hoff = int((fw-niw)/2.0), int((fh-nih)/2.0)
    dest = Image.new('RGB', (fw,fh),pageBg)
    border = Image.new('RGB', (iw+2*paw, ih+2*pah),borderBg)
    for w in range(nw):
        for h in range(nh):
            dx = paw + woff + w * (iw + paw*3)
            dy = pah + hoff + h * (ih + pah*3)
            dest.paste(border, (dx, dy))
            dest.paste(src, (dx+paw, dy+pah))
    return dest


if __name__=='__main__':
    print("Copyright (C) 2003 Jeffrey Clement")
    print("This is free software; see the source for copying conditions.  There is NO")
    print("warranty; not even for MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.")
    print("")
    print("(view the source code for details on using this library)")

