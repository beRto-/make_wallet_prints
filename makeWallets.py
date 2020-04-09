import os
import sys
import csv

import makeWalletsClass as mwClass
import makeWalletsGUI as gui


def getInputs(inputFileName):
    dictVar = {
             'applyCrop':(),
             'resizeForPrinting':(),
             'hw_paperDims':(),
             'wh_tilePattern':(),
             'long_short_print_px':(),
             'inputdir':(),
             'outputdir':()
             }

    tilerPath = os.path.join( gui.module_path(), gui.paramDir() )
    #print tilerPath

    with open( os.path.join(tilerPath, inputFileName), 'r') as csvfile:
        inputreader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in inputreader:
            dictVar[row[0]]=row[1:]

    #print dictVar

    try:
        applyCrop = gui.convertToBoolean(dictVar['applyCrop'][0])
        resizeForPrinting = gui.convertToBoolean(dictVar['resizeForPrinting'][0])
        hw_paperDims = dictVar['hw_paperDims'][0]
        wh_tilePattern = list(map(int, dictVar['wh_tilePattern']))
        long_short_print_px = list(map(int, dictVar['long_short_print_px']))
        inputdir = dictVar['inputdir'][0]
        outputdir = dictVar['outputdir'][0]
    except:
        print("Exiting: error on input setup - " + inputFileName)
        sys.exit(0)

    #make user input of imgdir optional
    #apply current dir, if user value is blank
    if inputdir == '':
        inputdir = tilerPath

    if outputdir == '':
        outputdir = tilerPath

    #print applyCrop, resizeForPrinting, hw_paperDims, wh_tilePattern, long_short_print_px, imgdir
    return (applyCrop, resizeForPrinting, hw_paperDims, wh_tilePattern, long_short_print_px, inputdir, outputdir)


def readSizes(inputFileName):
    tilerPath = gui.module_path()

    dictSizes={}

    f = open( os.path.join(tilerPath, gui.paramDir(), inputFileName), 'r' )
    try:
        reader = csv.reader(f, delimiter=',', quotechar='"')

        #http://stackoverflow.com/questions/6740918/creating-a-dictionary-from-a-csv-file
        # Python 2.7 --> dictSizes = {rows[0]:map(float, rows[1:]) for rows in reader} #convert entries to dictionary
        dictSizes = dict((rows[0],rows[1:]) for rows in reader) #Python 2.6
    except:
        print('failed on reading: ' + inputFileName)
        print('(most likely due to blank row at end of file)')
    finally:
        f.close()

    return dictSizes


def main():
    inputParamsFilename = 'inputs.csv'
    paperSizeFilename = 'sizes.csv'

    try:
        (applyCrop, resizeForPrinting, hw_paperDims, wh_tilePattern, 
         long_short_print_px, inputdir, outputdir) = getInputs(inputParamsFilename)
    except Exception as e:
        print('Exiting: error on reading ' + inputParamsFilename)
        print(e)
        sys.exit(0)

    dictPaperSizes = readSizes(paperSizeFilename)
    #print dictPaperSizes

    mw = mwClass.makeWallet(hw_paperDims, wh_tilePattern, long_short_print_px, 
                            inputdir, outputdir, dictPaperSizes, applyCrop,
                            resizeForPrinting, inputParamsFilename)

    #start the GUI
    gui.runGUI(mw)


if __name__ == "__main__":
    main()

