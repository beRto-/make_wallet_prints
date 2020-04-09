import os
from PIL import Image

import libtile


def imageProcessor(self, inputDir, fname, saveDir, prefix=''): #, hw_paperDims, long_short_print_px, wh_tilePattern, applyCrop=False, resizeForPrint=False):
    src = Image.open( os.path.join(inputDir, fname) )
    w_pic, h_pic = src.size
    hw_pic = h_pic / w_pic

    h_paper, w_paper = list(map(float, self.dictPaperSizes.get(self.hw_paperDims) ))
    #print 'hw: ' + str(h_paper) + ' ' + str(w_paper)
    hw_paper = h_paper/w_paper

    w_tiles, h_tiles = self.wh_tilePattern
    w_frame = w_paper / w_tiles
    h_frame = h_paper / h_tiles

    hw_frame = h_frame / w_frame

    long_px, short_px = self.long_short_print_px

    if imageOrientation(hw_pic) != imageOrientation(hw_frame):
        #photo not aligned with tile frame
        #swap paper orientation
        w_tiles, h_tiles = h_tiles, w_tiles #swap
        #self.wh_tilePattern = self.wh_tilePattern[::-1]
# reverse list here, but no longer reverse dims (since str) ---> disconnect on next load

        # no longer reverse list, since this is a string, not actual dims
        #self.hw_paperDims = self.hw_paperDims[::-1]
        #h_paper, w_paper = self.hw_paperDims

        h_paper, w_paper = w_paper, h_paper    #swap
        hw_paper = h_paper/w_paper
        #REF: reverse order of tuple
        #http://stackoverflow.com/questions/10201977/how-to-reverse-tuples-in-python

    if h_paper > w_paper:
        #height > width
        wh_print_px = (short_px, long_px)
    else:
        wh_print_px = (long_px, short_px)

    #dest = libtile.tile(self.wh_tilePattern,src,hw_paper,0,(0,0,0),(255,255,255),0, self.applyCrop)
    dest = libtile.tile([w_tiles, h_tiles],src,hw_paper,0,(0,0,0),(255,255,255),0, self.applyCrop)
    if self.resizeForPrinting == True:
        dest.thumbnail(wh_print_px, Image.ANTIALIAS)
    dest.save( os.path.join(saveDir, prefix+fname), 'JPEG', quality=100)


def imageOrientation(hwRatio):
    if hwRatio > 1:
        return "portrait"
    elif hwRatio < 1:
        return "landscape"
    elif hwRatio == 1:
        return "square"
    else:
        return "orientation error"


class makeWallet:
    processImage = imageProcessor

    def __init__(self, hw_paperDims, wh_tilePattern, long_short_print_px, 
                 inputdir, outputdir, dictPaperSizes, applyCrop=False,
                 resizeForPrinting=False, paramFile='inputs.csv'):
        #load user-defined variables
        self.applyCrop = applyCrop
        self.resizeForPrinting = resizeForPrinting
        self.hw_paperDims = hw_paperDims
        self.wh_tilePattern = wh_tilePattern
        self.long_short_print_px = long_short_print_px
        self.inputdir = inputdir
        self.outputdir = outputdir
        self.dictPaperSizes = dictPaperSizes
        self.paramFile = paramFile

    def set_applyCrop(self, applyCrop):
        self.applyCrop = applyCrop

    def get_applyCrop(self):
        return self.applyCrop

    def set_resizeForPrinting(self, resizeForPrinting):
        self.resizeForPrinting = resizeForPrinting

    def get_resizeForPrinting(self):
        return self.resizeForPrinting

    def set_hw_paperDims(self, hw_paperDims):
        self.hw_paperDims = hw_paperDims

    def get_hw_paperDims(self):
        return self.hw_paperDims

    def set_wh_tilePattern(self, wh_tilePattern):
        self.wh_tilePattern = wh_tilePattern

    def get_wh_tilePattern(self):
        return self.wh_tilePattern

    def set_long_short_print_px(self, long_short_print_px):
        self.long_short_print_px = long_short_print_px

    def get_long_short_print_px(self):
        return self.long_short_print_px

    def set_inputdir(self, inputdir):
        self.inputdir = inputdir

    def get_inputdir(self):
        return self.inputdir

    def set_outputdir(self, outputdir):
        self.outputdir = outputdir

    def get_outputdir(self):
        return self.outputdir

    def set_dictPaperSizes(self, dictPaperSizes):
        self.dictPaperSizes = dictPaperSizes

    def get_dictPaperSizes(self):
        return self.dictPaperSizes

    def set_paramFile(self, paramFile):
        self.paramFile = paramFile

    def get_paramFile(self):
        return self.paramFile


if __name__ == "__main__":
    print('launch this from makeWallets.py')