#!/usr/bin/env python3

__author__           = "Dilawar Singh"
__copyright__        = "Copyright 2019-, Dilawar Singh"
__maintainer__       = "Dilawar Singh"
__email__            = "dilawars@ncbs.res.in"

from pathlib import Path
import PySimpleGUI as sg
import methods as M
import canvas as C
import itertools
import subprocess
import time
import sys
import serial.tools.list_ports

ports_ = [x.device for x in
        serial.tools.list_ports.comports(include_links=False)]
defaultPort_ = ports_[0] if ports_ else None

# Default size.
W_, H_ = 800, 600

if not (sys.version_info.major > 2 and sys.version_info.minor > 5):
    print( f"[ERROR] Requires python 3.6+" )
    quit(1)

# Globals.
class Args: pass
args_ = Args()
args_.build_dir = (Path(__file__).parent / '_build')
args_.build_dir.mkdir(exist_ok=True)


# Build and Run tab.
sizeInput = (W_//50, 1)
tab1 = [ 
        [ 
            sg.T('AnimalName'), sg.In(key='ANIMAL_NAME', size=sizeInput)
            , sg.T('ProtoCode'), sg.In(key='PROTO_CODE', size=sizeInput)
            , sg.T('SessionNum'), sg.In(key='SESSION_NUM', size=sizeInput)
            , sg.T('SerialPort'), sg.Combo(ports_, default_value=defaultPort_, key='SERIAL_PORT', size=sizeInput)
            , sg.Button('Build')
        ]
    ]

status_ = sg.Text( "STATUS", size=(100,1), key="__STATUS__")

def updateStatus(what):
    global status_
    status_.Update(what)

# canvas tabs.
canvasTabs = sg.TabGroup([[
    sg.Tab("TIFF", [[sg.Canvas(key='__CANVAS1__', size=(W_, H_))]],
        key="__TABTIFF__")
    , sg.Tab("Results", [[sg.Canvas(key='__CANVAS2__', size=(W_, H_))]],
        key="__TABRESULT__")
    ]], key="__CANVASES__"
    )

# Analysis tab.
tab2 = [ 
        [sg.In(key='session_dir', do_not_clear=True)
            , sg.FolderBrowse("Browse DataDir", target='session_dir')
            , sg.Button("Find TIFF")]
        , [sg.In(key='data_dir', do_not_clear=True)
            , sg.FolderBrowse("Select ResultDir", target='data_dir'),  sg.OK()
            ]
        , [ sg.Button('Analyze All', key='Analyze')
            ,  sg.ProgressBar(1000, orientation='h', size=(20,20), key='__PROGRESS__'), ]
        , [ sg.Listbox(values=[], size=(30, H_//20), enable_events=True
            , key="__FILELIST__"
            , tooltip="Select a file to analyze"
            ), canvasTabs
            ]
        ]

layout_ = [
        [ sg.TabGroup([[sg.Tab('Build&Run', tab1), sg.Tab('Analyze', tab2)]]
            , key="__TABS__", enable_events = True)]
        , [ sg.Exit(), status_ ]
        ]

win_ = sg.Window('MouseBehaviour', layout_).Finalize()

class TiffFile:
    def __init__(self, path):
        self.path = Path(path)
        self.name = self.path.name

    def __str__(self):
        return self.name

    def readFrames(self):
        return M.readTiff(self.path)

    def plotData(self, data, outfile):
        outfile.parent.mkdir(parents=True, exist_ok=True)
        return M.plotAndSaveData(data, outfile=outfile, obj=self)

def findTiffFiles(datadir, ext="tif"):
    print( f"[INFO ] Analysing data in {datadir}" )
    datadir = Path(datadir)
    tiffs = []
    for x in itertools.chain(datadir.glob(f"*.{ext}"), datadir.glob(f"*.{ext}f")):
        tiffs.append(TiffFile(x))
    return tiffs

def updateTiffFileList(datadir):
    global win_
    tiffs = findTiffFiles(datadir)
    win_.FindElement("__FILELIST__").Update(tiffs)
    return tiffs

def analyzeTiffDir(sessiondir, datadir):
    global win_
    global status_
    tiffs = updateTiffFileList(sessiondir)
    pgbar = win_.FindElement("__PROGRESS__")
    for i, tiff in enumerate(tiffs):
        pgbar.UpdateBar(int((i+1)*1000.0/len(tiffs)))
        status_.Update(f"Analysing {tiff}")
        analyzeTiffFile(tiff)

    # Now analyze the dir.
    summaryPlotPath = datadir / 'summary.png'
    M.plotSessionDir(datadir, summaryPlotPath)
    # Focus on results tab.
    win_.FindElement("__CANVASES__").SelectTab(1)
    canvas2 = win_.FindElement("__CANVAS2__").TKCanvas
    C.showImageFileOnCanvas(canvas2, summaryPlotPath) 
    status_.Update("ALL DONE")

def analyzeTiffFile(tiff):
    global args_
    print( f"[INFO ] Analyzing {tiff}" )
    outfile = args_.data_dir / f"{tiff}.png"
    if not outfile.exists():
        win_.FindElement("__CANVASES__").SelectTab(0)
        canvas1 = win_.FindElement("__CANVAS1__").TKCanvas
        frames, data = tiff.readFrames()
        C.drawNumpyOnCanvas(canvas1, frames)
        tiff.plotData(data, outfile)

    # Focus this tab.
    win_.FindElement("__CANVASES__").SelectTab(1)
    canvas2 = win_.FindElement("__CANVAS2__").TKCanvas
    C.showImageFileOnCanvas(canvas2, outfile) 
    time.sleep(0.2)

def initBuildEnvironment():
    global win_
    global args_
    # Find CMakeCache 
    buildDir = args_.build_dir
    params = {}
    cmakeCache = buildDir / 'CMakeCache.txt'
    if cmakeCache.exists():
        print( f"[INFO ] Found CMakeCache " )
        with open(cmakeCache, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                if r'//' == line[:2] or '#' == line[0]:
                    continue
                key, val = line.split('=')
                params[key.split(':')[0]] = val

    # update window params
    for x in ['ANIMAL_NAME', 'SESSION_NUM', 'PROTO_CODE']:
        win_.FindElement(x).Update(params.get(x, ''))
    return params


def build():
    global win_, args_
    buildDir = args_.build_dir
    animalName = win_.FindElement("ANIMAL_NAME").Get()
    protoCode = win_.FindElement("PROTO_CODE").Get()
    sessionNum = win_.FindElement("SESSION_NUM").Get()
    if not animalName:
        raise RuntimeError( "'Animal Name' is not specified")
    if not protoCode:
        raise RuntimeError( "'Proto Code' is not specified")
    if not sessionNum:
        raise RuntimeError( "'Session Num' is not specified")

    sourceDir = Path(__file__).parent.absolute()
    
    p = subprocess.run( [ "cmake", f"-DANIMAL_NAME={animalName}"
        , f"-DPROTO_CODE={protoCode}", f"-DSESSION_NUM={sessionNum}"
        , f"{sourceDir}"
        ], cwd = buildDir, universal_newlines=True)
    p = subprocess.run( [ "make"], cwd = buildDir, universal_newlines=True)
        

def updateDataDirs():
    global args_
    if args_.session_dir:
        win_.FindElement("session_dir").Update(args_.session_dir)
        updateTiffFileList(args_.session_dir)
        if args_.data_dir is None:
            args_.data_dir = Path(args_.session_dir) / 'analysis'
        else:
            args_.data_dir = Path(args_.data_dir)
    if args_.data_dir:
        win_.FindElement("data_dir").Update(args_.data_dir)

def main():
    global win_
    updateDataDirs()
    initBuildEnvironment()
    win_.FindElement("__TABS__").SelectTab(args_.tab)
    while True:
        event, values = win_.Read()
        if event is None or event == 'Exit':
            break
        elif event.lower() == 'find tiff':
            updateTiffFileList(values['session_dir'])
            args_.session_dir = Path(values['session_dir'])
            updateDataDirs()
        elif event.lower() == 'ok':
            args_.data_dir = Path(values['data_dir'])
            updateDataDirs()
        elif event == 'Analyze':
            analyzeTiffDir(args_.session_dir, args_.data_dir)
        elif event == "__FILELIST__":
            analyzeTiffFile( values['__FILELIST__'][0] )
        elif event.lower() == 'build':
            updateStatus("Building ...")
            build()
            updateStatus("Build Over")
        else:
            print( f"[WARN ] Unsupported event {event}" )
    win_.Close()

if __name__ == '__main__':
    import argparse
    # Argument parser.
    description = '''GUI.'''
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('--session-dir', '-s'
            , required = False, type=Path
            , help = 'Data directory.'
            )
    parser.add_argument('--tab', '-t'
             , required = False, default = 0, type=int
             , help = 'Which tab to focus at launch. Useful during development.'
             )
    parser.add_argument('--data-dir', '-d'
             , required = False, default = None
             , help = 'Where to save the data? Default is session-dir/analysis'
             )
    parser.parse_args(namespace=args_)
    main()
