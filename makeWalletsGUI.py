# useful references
# http://effbot.org/tkinterbook/entry.htm
# http://effbot.org/tkinterbook/grid.htm <--- grid manager
# http://effbot.org/zone/tkinter-callbacks.htm <-- passing argument to tk button
# http://stackoverflow.com/questions/550050/removing-the-tk-icon-on-python-tkinter-windows
# http://stackoverflow.com/questions/17005961/displaying-images-with-tkinter
# http://code.activestate.com/recipes/438123-file-tkinter-dialogs/


import os
import sys
import tkinter as tk
import tkinter.filedialog
import tkinter.font
from PIL import Image, ImageTk
import shutil
import csv


def createInputTextBox(parent, inputDir):
    global entryBoxInputText
    global strInputDir
    strInputDir = tk.StringVar()
    entryBoxInputText = tk.Entry(parent, textvariable=strInputDir, font=customFont, width=20)
    #entryBoxInputText.see(tk.END) #want to show rightmost, w/o scroll bar (justify=tk.RIGHT does not affect display)
    strInputDir.set(inputDir)


def buttonSetInputTextBox():
    newInputDir = dirSelect( strInputDir.get() )
    #print newInputDir
    if newInputDir != None:
        strInputDir.set(newInputDir)


def createOutputTextBox(parent, outputDir):
    global entryBoxOutputText
    global strOutputDir
    strOutputDir = tk.StringVar()
    entryBoxOutputText = tk.Entry(parent, textvariable=strOutputDir, font=customFont, width=20)
    strOutputDir.set(outputDir)


def buttonSetOutputTextBox():
    newOutputDir = dirSelect( strOutputDir.get() )
    #print newOutputDir
    if newOutputDir != None:
        strOutputDir.set(newOutputDir)


def dirSelect(startDirectory):
    #root.withdraw() #use to hide tkinter window
    dirname = None
    #tempdir = tkFileDialog.askdirectory(parent=root,initialdir="/",title='Please select a directory')
    tempdir = tkinter.filedialog.askdirectory(parent=root, initialdir=startDirectory, title='Please select a directory')
    if len(tempdir) > 0:
        #print "You chose %s" % tempdir
        dirname = tempdir
    return dirname


def setRunParameters(makeWallet):
    #print 'set run parameters'

    makeWallet.set_inputdir( strInputDir.get() )
    makeWallet.set_outputdir( strOutputDir.get() )

    wh_tile = list(map(int, [grid_w.get(), grid_h.get()] ))
    makeWallet.set_wh_tilePattern( wh_tile )

    wh_resolution = list(map(int, [res_w.get(), res_h.get()] ))
    makeWallet.set_long_short_print_px( wh_resolution )

#     hw_paperDims = makeWallet.get_dictPaperSizes()[ paperSizeString.get() ]
#     hw_paperDims = map(float, hw_paperDims)
#     makeWallet.set_hw_paperDims( hw_paperDims )
    makeWallet.set_hw_paperDims( paperSizeString.get() )

    makeWallet.set_applyCrop( convertToBoolean(varApplyCrop.get()) )
    makeWallet.set_resizeForPrinting( bool(varResizePrint.get()) )


def convertToBoolean(strText):
    if strText.upper() == 'TRUE':
        return True
    elif strText.upper() == 'FALSE':
        return False
    else:
        return strText.upper()


def runMakeWallets(makeWallet): #call from GUI; no arguments

    setRunParameters(makeWallet)

    inputdir = makeWallet.get_inputdir()
    outputdir = makeWallet.get_outputdir()

    #files = os.listdir(imgdir + 'originalPictures/')
    files = os.listdir(inputdir)

    #process each jpg in directory
    for fname in files:
        if fname.lower().endswith('.jpg'):
            print('processing: ' + fname)
            writeToLog('processing: ' + fname)
            makeWallet.processImage(inputdir, fname, outputdir, 'wallet-')

    if bool(varSaveParameters.get()) == True:
        print('update inputs')
        updateRunParameters( makeWallet.get_paramFile() , makeWallet)

    print('done')
    writeToLog('done')


def quit():
    #root.quit()
    root.destroy()


def module_path():
    #http://stackoverflow.com/questions/729583/getting-file-path-of-imported-module
    #currentDirectory = os.path.dirname( inspect.getsourcefile(local_function) )

    #http://stackoverflow.com/questions/17398426/error-when-compiling-shitil-with-pyinstaller
    #currentDirectory = os.path.dirname( sys.argv[0] )  # needed for .exe approach.

    #http://stackoverflow.com/questions/2292703/how-can-i-get-the-executables-current-directory-in-py2exe
    #currentDirectory = os.path.realpath( os.path.dirname(sys.argv[0]) )
    #print currentDirectory


    # determine if application is a script file or frozen exe
    # http://stackoverflow.com/questions/404744/determining-application-path-in-a-python-exe-generated-by-pyinstaller
    if getattr(sys, 'frozen', False):
        currentDirectory = os.path.dirname(sys.executable)
        #print 'frozen: ' + currentDirectory
    elif __file__:
        currentDirectory = os.path.dirname(__file__)
        #print 'file: ' + currentDirectory

    return currentDirectory


def preview(makeWallet):

    setRunParameters(makeWallet)

    # override resolution for preview
    orig_wh_resolution = makeWallet.get_long_short_print_px()
    makeWallet.set_long_short_print_px( previewRes )

    fname = 'preview.jpg'
    #print 'processing: ' + fname
    inputdir = os.path.join(module_path(), paramDir() )
    outputdir = inputdir

    makeWallet.processImage(inputdir, fname, outputdir, 'wallet-')

    # restore original resolution
    makeWallet.set_long_short_print_px( orig_wh_resolution )

    newimg = Image.open( os.path.join(inputdir,'wallet-preview.jpg') )
    newimg.thumbnail(previewRes, Image.ANTIALIAS) #operates on original; maintains aspect ratio; only shrinks image
    im = ImageTk.PhotoImage(newimg) # Keep a reference, prevent garbage collector

    display.configure(image=im)
    display.image = im


def writeToLog(msg):
    # http://www.tkdocs.com/tutorial/text.html
    numlines = outputLog.index('end - 1 line').split('.')[0]
    outputLog['state'] = 'normal'
    # *deletes* data if it exceeds outputLogMaxLines
#     if int(numlines)==outputLogMaxLines:
#         outputLog.delete(1.0, 2.0)
    if outputLog.index('end-1c')!='1.0':
        outputLog.insert('end', '\n')
    outputLog.insert('end', msg)
    outputLog.see(tk.END) #instead of delete, just keep scrolling to end
    outputLog.update_idletasks()  #forces refresh
    outputLog['state'] = 'disabled'


def updateRunParameters(filename, makeWallet):
    currPath = os.path.join(module_path(), paramDir())

    # backup current input parameters
    # http://stackoverflow.com/questions/6996603/how-do-i-delete-a-file-or-folder-in-python
    try:
        # if a previous backup exists, delete it
        os.remove( os.path.join(currPath, filename.replace('.csv', '.bak')) )
    except:
        pass

    # copy current input file to a ".bak" version
    inputFilePath = os.path.join(currPath,filename)
    shutil.copy( inputFilePath, inputFilePath.replace('.csv', '.bak') )

    # open input file
    f = open( os.path.join(currPath, filename), 'w')
    writer = csv.writer(f, delimiter=',', quotechar='"')

    # output current values to the input file
    writer.writerow(['applyCrop', str(makeWallet.get_applyCrop()) ])
    writer.writerow(['resizeForPrinting', str(makeWallet.get_resizeForPrinting()) ])
    writer.writerow(['hw_paperDims', str(makeWallet.get_hw_paperDims()) ])
    writer.writerow(['wh_tilePattern'] + makeWallet.get_wh_tilePattern() )
    writer.writerow(['long_short_print_px'] + makeWallet.get_long_short_print_px() )
    writer.writerow(['inputdir', str(makeWallet.get_inputdir()) ])
    writer.writerow(['outputdir', str(makeWallet.get_outputdir()) ])

    # exit
    f.close()


def buildGUI(makeWallet):
    global root
    root = tk.Tk()
    #root.geometry("300x200+300+300")
    #root.iconbitmap(default='transparent.ico')
    root.title("makeWallets")
    root.wm_resizable(0,0) #makes window NOT resizeable

    global customFont
    customFont = tkinter.font.Font(family="Helvetica", size=9)

    global buttonFont
    buttonFont = tkinter.font.Font(family="Helvetica", size=6)

    #section to select file input / output directories
    inputDir = makeWallet.get_inputdir()
    outputDir = makeWallet.get_outputdir()

    tk.Label(root, text="input", font=customFont).grid(row=0,column=0,sticky=tk.E)
    createInputTextBox(root, inputDir)
    entryBoxInputText.grid(row=0, column=1, columnspan=2, sticky=tk.E+tk.W)
    buttonSetInputDirectory = tk.Button(root, text="...", font=buttonFont, height=1, command=buttonSetInputTextBox ) #cannot pass arguments
    buttonSetInputDirectory.grid(row=0, column=3)

    tk.Label(root, text="output", font=customFont).grid(row=1,column=0,sticky=tk.E)
    createOutputTextBox(root, outputDir)
    entryBoxOutputText.grid(row=1, column=1, columnspan=2, sticky=tk.E+tk.W)
    buttonSetOutputDirectory = tk.Button(root, text="...", font=buttonFont, height=1, command=buttonSetOutputTextBox ) #cannot pass arguments
    buttonSetOutputDirectory.grid(row=1, column=3)

    #section to specify run parameters
    tk.Label(root, text='grid pattern', font=customFont).grid(row=2,column=0,columnspan=2)
    global grid_w
    global grid_h
    grid_w = tk.Entry(root, width=4, font=customFont)
    grid_w.grid(row=3,column=0)
    grid_w.insert(0, makeWallet.get_wh_tilePattern()[0]) #initialize
    grid_h = tk.Entry(root, width=4, font=customFont)
    grid_h.grid(row=4,column=0)
    grid_h.insert(0, makeWallet.get_wh_tilePattern()[1]) #initialize
    tk.Label(root, text='w', font=customFont).grid(row=3,column=1,sticky=tk.W)
    tk.Label(root, text='h', font=customFont).grid(row=4,column=1,sticky=tk.W)

    tk.Label(root, text='resolution', font=customFont).grid(row=2,column=2,columnspan=2)
    global res_w
    global res_h
    res_w = tk.Entry(root, width=4, font=customFont)
    res_w.grid(row=3,column=2)
    res_w.insert(0, makeWallet.get_long_short_print_px()[0]) #initialize
    res_h = tk.Entry(root, width=4, font=customFont)
    res_h.grid(row=4,column=2)
    res_h.insert(0, makeWallet.get_long_short_print_px()[1]) #initialize
    tk.Label(root, text='w', font=customFont).grid(row=3,column=3,sticky=tk.W)
    tk.Label(root, text='h', font=customFont).grid(row=4,column=3,sticky=tk.W)

    #print size drop down menu
    tk.Label(root, text='print size', font=customFont).grid(row=5,column=0,columnspan=2,sticky=tk.E)

    paperSizeOptions = list(makeWallet.get_dictPaperSizes().keys())


    global paperSizeString
    paperSizeString = tk.StringVar(root)
    paperSizeString.set( makeWallet.get_hw_paperDims() ) # default value (NOTE: dictionary key order is not guaranteed / defined)

    paperSize = tk.OptionMenu(*(root, paperSizeString) + tuple(paperSizeOptions))
    paperSize.config(font=customFont,width=6)
    paperSize.grid(row=5,column=2,columnspan=2,sticky=tk.W)

    #apply crop (convert to drop down - need "SQUARE" option - not Boolean
    tk.Label(root, text='crop image', font=customFont).grid(row=6,column=0,columnspan=2,sticky=tk.E)
    global varApplyCrop #make global to keep ref; else garbage collect; check does not display
    varApplyCrop = tk.StringVar(root)
    varApplyCrop.set( str(makeWallet.get_applyCrop()) )
    optApplyCrop = tk.OptionMenu(root, varApplyCrop, "True", "False", "Square")
    optApplyCrop.config(font=customFont,width=6)
    optApplyCrop.grid(row=6,column=2,columnspan=2,sticky=tk.W)

    global varResizePrint
    varResizePrint = tk.IntVar(root)
    varResizePrint.set(makeWallet.get_resizeForPrinting())
    chkResizePrint = tk.Checkbutton(root, text="resize for print", font=customFont, variable=varResizePrint)
    chkResizePrint.grid(row=7,column=0,columnspan=2,sticky=tk.W)

    global varSaveParameters
    varSaveParameters = tk.IntVar(root)
    varSaveParameters.set(0) #defaults 'OFF'
    chkResizePrint = tk.Checkbutton(root, text="save inputs", font=customFont, variable=varSaveParameters)
    chkResizePrint.grid(row=7,column=2,columnspan=2,sticky=tk.E)

    #section for output message display
    # http://www.tkdocs.com/tutorial/text.html
    global outputLog
    global outputLogMaxLines
    outputLogMaxLines = 4
    outputLog = tk.Text(root, font=customFont, height=outputLogMaxLines, wrap='none', pady=5)
    outputLog.grid(row=8,column=0,columnspan=6)

    #section to display preview image
    original = Image.open( os.path.join(paramDir() ,'preview.jpg') )
    global previewRes
    previewRes = 450,300 #w,h
    original.thumbnail(previewRes, Image.ANTIALIAS) #operates on original; maintains aspect ratio; only shrinks image

    global im
    im = ImageTk.PhotoImage(original) # Keep a reference, prevent garbage collector

    global display
    display = tk.Label(root, width=previewRes[0], height=previewRes[1], image=im)
    display.grid(row=0, column=4, columnspan=2, rowspan=6, pady=5, padx=5)

    #section for run / cancel buttons
    buttonGO = tk.Button(root, text="GO", width=10, font=customFont, command=lambda: runMakeWallets(makeWallet) ) #cannot pass arguments
    buttonGO.grid(row=7, column=4, sticky=tk.E, pady=5)

    buttonCancel = tk.Button(root, text="close", width=10, font=customFont, command=quit ) #cannot pass arguments
    buttonCancel.grid(row=7, column=5, sticky=tk.W)

    buttonPreview = tk.Button(root, text="preview", width=10, font=customFont, command=lambda: preview(makeWallet) ) #cannot pass arguments
    buttonPreview.grid(row=6, column=4, columnspan=2)


def paramDir():
    # name of directory holding gui parameters / inputs / preview image
    return 'inp'


def runGUI(makeWallet):
    buildGUI(makeWallet)
    preview(makeWallet) #initialize preview screen
    root.mainloop() # Start the event loop


if __name__ == "__main__":
    print('launch this from makeWallets.py')

