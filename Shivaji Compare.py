import PySimpleGUI as sg
from tkinter import *
import os.path
import filecmp
from PIL import Image
import io
import sys
import fitz
from sys import exit





css={}
file_types = [("JPEG (*.jpg)", "*.jpg"),
              ("All files (*.*)", "*.*")]

def PdfViewer():
    sg.theme('GreenTan')

    if len(sys.argv) == 1:
        fname = sg.popup_get_file(
            'PDF Browser', 'PDF file to open', file_types=(("PDF Files", "*.pdf"),))
    if fname is None:
        sg.popup_cancel('Cancelling')
        exit(0)
    else:
        fname = sys.argv[1]

    doc = fitz.open(fname)
    page_count = len(doc)

    # storage for page display lists
    dlist_tab = [None] * page_count

    title = "PyMuPDF display of '%s', pages: %i" % (fname, page_count)


    def get_page(pno, zoom=0):
        """Return a PNG image for a document page number. If zoom is other than 0, one of the 4 page quadrants are zoomed-in instead and the corresponding clip returned.
        """
        dlist = dlist_tab[pno]  # get display list
        if not dlist:  # create if not yet there
            dlist_tab[pno] = doc[pno].getDisplayList()
            dlist = dlist_tab[pno]
        r = dlist.rect  # page rectangle
        mp = r.tl + (r.br - r.tl) * 0.5  # rect middle point
        mt = r.tl + (r.tr - r.tl) * 0.5  # middle of top edge
        ml = r.tl + (r.bl - r.tl) * 0.5  # middle of left edge
        mr = r.tr + (r.br - r.tr) * 0.5  # middle of right egde
        mb = r.bl + (r.br - r.bl) * 0.5  # middle of bottom edge
        mat = fitz.Matrix(2, 2)  # zoom matrix
        if zoom == 1:  # top-left quadrant
            clip = fitz.Rect(r.tl, mp)
        elif zoom == 4:  # bot-right quadrant
            clip = fitz.Rect(mp, r.br)
        elif zoom == 2:  # top-right
            clip = fitz.Rect(mt, mr)
        elif zoom == 3:  # bot-left
            clip = fitz.Rect(ml, mb)
        if zoom == 0:  # total page
            pix = dlist.getPixmap(alpha=False)
        else:
            pix = dlist.getPixmap(alpha=False, matrix=mat, clip=clip)
        return pix.getPNGData()  # return the PNG image



    cur_page = 0
    data = get_page(cur_page)  # show page 1 for start
    image_elem = sg.Image(data=data)
    goto = sg.InputText(str(cur_page + 1), size=(5, 1))
    
    layout = [[sg.Button('Prev'),
               sg.Button('Next'),
               sg.Text('Page:'),
               goto,],
                [sg.Text("Zoom:"),
                 sg.Button('Top-L'),
                 sg.Button('Top-R'),
                 sg.Button('Bot-L'),
                 sg.Button('Bot-R'),],
                 [image_elem],]
    my_keys = ("Next", "Next:34", "Prev", "Prior:33", "Top-L", "Top-R",
           "Bot-L", "Bot-R", "MouseWheel:Down", "MouseWheel:Up")
    zoom_buttons = ("Top-L", "Top-R", "Bot-L", "Bot-R")



    window = sg.Window(title, layout,
                   return_keyboard_events=True, use_default_focus=False)

    old_page = 0
    old_zoom = 0  # used for zoom on/off
    # the zoom buttons work in on/off mode.
    
    while True:
        event, values = window.read(timeout=100)
        zoom = 0
        force_page = False
        if event == sg.WIN_CLOSED:
            break

        if event in ("Escape:27",):  # this spares me a 'Quit' button!
            break
        if event[0] == chr(13):  # surprise: this is 'Enter'!
            try:
                cur_page = int(values[0]) - 1  # check if valid
                while cur_page < 0:
                    cur_page += page_count
            except:
                cur_page = 0  # this guy's trying to fool me
                goto.update(str(cur_page + 1))
                # goto.TKStringVar.set(str(cur_page + 1))
                
        elif event in ("Next", "Next:34", "MouseWheel:Down"):
            cur_page += 1
        elif event in ("Prev", "Prior:33", "MouseWheel:Up"):
            cur_page -= 1
        elif event == "Top-L":
            zoom = 1
        elif event == "Top-R":
            zoom = 2
        elif event == "Bot-L":
            zoom = 3
        elif event == "Bot-R":
            zoom = 4

        # sanitize page number
        if cur_page >= page_count:  # wrap around
            cur_page = 0
        while cur_page < 0:  # we show conventional page numbers
            cur_page += page_count

        # prevent creating same data again
        if cur_page != old_page:
            zoom = old_zoom = 0
            force_page = True
            
        if event in zoom_buttons:
            if 0 < zoom == old_zoom:
                zoom = 0
                force_page = True
                
                if zoom != old_zoom:
                    force_page = True
                    
        if force_page:
            data = get_page(cur_page, zoom)
            image_elem.update(data=data)
            old_page = cur_page
            old_zoom = zoom
            
            # update page number field
        if event in my_keys or not values[0]:
            goto.update(str(cur_page + 1))
            # goto.TKStringVar.set(str(cur_page + 1))


def ImageViewer1():
    layout = [
        [sg.Image(key="-IMAGE-")],
        [
            sg.Text("Image File"),
            sg.Input(size=(25, 1), key="-FILE-"),
            sg.FileBrowse(file_types=file_types),
            sg.Button("Load Image"),
        ],
    ]
    window = sg.Window("Image Viewer", layout,resizable=False)
    while True:
        event, values = window.read()
        if event == "Exit" or event == sg.WIN_CLOSED:
            break
        if event == "Load Image":
            filename = values["-FILE-"]
            if os.path.exists(filename):
                image = Image.open(values["-FILE-"])
                image.thumbnail((2500,1900))
                bio = io.BytesIO()
                image.save(bio, format="PNG")
                window["-IMAGE-"].update(data=bio.getvalue())
    window.close()

def ImageViewer():
    file_list_column = [[sg.Text("Image Folder"),
                         sg.In(size=(25, 1), enable_events=True, key="-FOLDER-"),
                         sg.FolderBrowse(),],
                        [sg.Listbox(values=[], enable_events=True, size=(40, 20), key="-FILE LIST-")]]
    image_viewer_column = [[sg.Text("Choose an image from list on left:")],
                           [sg.Text(size=(40, 1), key="-TOUT-")],
                           [sg.Image(key="-IMAGE-",size=(200,150))]]
    layout = [[sg.Column(file_list_column),
               sg.VSeperator(),
               sg.Column(image_viewer_column),]]
    window = sg.Window("Image Viewer", layout,resizable=True,size=(1500,740))
    while True:
        event, values = window.read()
        if event == "Exit" or event == sg.WIN_CLOSED:
            break
        if event == "-FOLDER-":
            folder = values["-FOLDER-"]
            try:
                # Get list of files in folder
                file_list = os.listdir(folder)
            except:
                file_list = []

        fnames = [
                f
                for f in file_list
                if os.path.isfile(os.path.join(folder, f))
                and f.lower().endswith((".jpg",".png", ".gif"))
                ]
        window["-FILE LIST-"].update(fnames)
        
        if event == "-FILE LIST-":  # A file was chosen from the listbox
            
            try:
                filename = os.path.join(values["-FOLDER-"], values["-FILE LIST-"][0])
                #window["-TOUT-"].update(filename)
                #window["-IMAGE-"].update(filename)
                if os.path.exists(filename):
                    image = Image.open(values["filename"])
                    image.thumbnail((400, 400))
                    bio = io.BytesIO()
                    image.save(bio, format="PNG")
                    window["-IMAGE-"].update(data=bio.getvalue())
            except:
                pass
    window.close()
    

def compare(file1,file2):
    x = filecmp.cmp(file1,file2,shallow=True)
    return x
def comparision():
    sg.theme('Black')
    menu_def = [['File', ['Open', 'Save', 'Exit',]],
                ['Edit', ['Paste', ['Special', 'Normal',], 'Undo'],],
                ['Help', 'About...'],]
    
    Leftdisplay=[ [sg.Text("File 1",font=("Helvetica", 35,'bold')),sg.T("")],
                  [sg.T("")],
                  [sg.T("")],
                  [sg.Text("Choose a File :-"),sg.Input(size=(50,30),key='-file1-'),sg.FileBrowse()]]
    Rightdisplay=[[sg.Text("File 2",font=("Helvetica", 35,'bold'))],
                  [sg.T("")],
                  [sg.T("")],
                  [sg.Text("Choose a File :-"),sg.Input(key='-file2-'),sg.FileBrowse()]]
    
    
    layout = [  [ sg.Menu(menu_def,font='15'),
                  sg.Column(Leftdisplay,pad=(100,0)),
                  sg.VSeparator(),
                  sg.Column(Rightdisplay,pad=(40,0))],
                [sg.Button('Compare',key='compare',pad=(660,50),size=(8,2))],
                [sg.Output(key='-output-',font=("Helvetica",22,'italic'),size=(60,10),pad=(300,0))],
                [sg.B('Exit',key='exit', size=(30,1),mouseover_colors='red',pad=(660,10))]]
    window = sg.Window('Shivaji Comparator',layout,resizable=True,size=(1500,740))
    
    while True:
        event,values = window.read()
        if event == sg.WIN_CLOSED or event== 'exit':
            break
        if event == "compare":
            x1=values['-file1-']
            x2=values['-file2-']
            x = filecmp.cmp(x1,x2,shallow=True)
            if x == True:
                print("Files are equal")
            else:
                print("Files are not equal")
    window.close()

def main():
    
    sg.theme('Black')   # Add a touch of color
    menu_def = [['File', ['Open', 'Save', 'Exit',]],
                ['Edit', ['Paste', ['Special', 'Normal',], 'Undo'],],
                ['Help', 'About...'],]
    # All the stuff inside your window.

    #layout1= [sg.BUTTON_TYPE_BROWSE_FILE]
    Leftdisplay=[[sg.Text("Session",font=("Helvetica", 35,'bold'),size=(15,1))]]
    
    Rightdisplay=[[sg.Text("Function Selection",font=("Helvetica", 35,'bold'),size=(15,1))],
                   [sg.T(""),sg.Button('File Comparision',size=(20,1),key="file Comparision")],
                   [sg.T(""),sg.Button('Folder Comparision',size=(20,1),key="folder Comparision")],
                   [sg.T(""),sg.Button('Folder Merge',size=(20,1),key="folder merge")],
                   [sg.T(""),sg.Button('Text Merge',size=(20,1),key="text merge")],
                   [sg.T(""),sg.Button('Image Viewer',size=(20,1),key="imageviewer")],
                   [sg.T(""),sg.Button('Image Viewer1',size=(20,1),key="imageviewer1")],
                   [sg.T(""),sg.Button('Pdf Viewer',size=(20,1),key="pdfviewer")]]


    layout = [  [sg.Menu(menu_def,font=("Helvetica",19,'bold')),
                 sg.Column(Leftdisplay,pad=(80,0)),
                 sg.VSeparator(),
                 sg.Column(Rightdisplay,pad=(40,0))],
                [sg.B('Exit',key='exit',font=("Helvetica", 22,'bold'),mouseover_colors=('red','#00b3b3'),focus=True,tooltip="EXIT")]]



    # Create the Window
    window = sg.Window('Shivaji Comaparator', layout,resizable=True)
    # Event Loop to process "events" and get the "values" of the inputs
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == 'exit': # if user closes window or clicks cancel
            break
        if event == "Comparision":
            comparision()
        if event == "imageviewer":
            ImageViewer()
        if event == "imageviewer1":
            ImageViewer1()
        if event == "pdfviewer":
            PdfViewer()
        
    

    window.close()
if __name__ == "__main__":
    main()