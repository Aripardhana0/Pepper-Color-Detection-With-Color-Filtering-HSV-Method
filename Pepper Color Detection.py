import cv2
import numpy as np
import tkinter as tk
from tkinter.font import Font
from tkinter import ttk
from PIL import Image, ImageTk


# Membuat jendela utama
root = tk.Tk()
root.title("Skrip Sweet")
root.geometry ("1366x768")
root.resizable(False, False)
cap = cv2.VideoCapture(0)

# Membuat Tab lain
notebook = ttk.Notebook(root)
tab1 = tk.Frame(notebook)
tab2 = tk.Frame(notebook)
tab3 = tk.Frame(notebook)
notebook.add(tab1, text="Home")
notebook.add(tab2, text="Intruction")
notebook.add(tab3, text="About")
notebook.place(x=-1, y=-1, width=1366, height=768)

# Atur Font
fontinframe=Font( family="coolvetica", size=11, weight="bold")
fontframe=Font( family="coolvetica", size=13, weight="bold")
fonttitle=Font( family="coolvetica", size=19, weight="bold")

#Variable
color=tk.StringVar()
upperhue=tk.IntVar()
uppersaturation=tk.IntVar()
uppervalue=tk.IntVar()
lowerhue=tk.IntVar()
lowersaturation=tk.IntVar()
lowervalue=tk.IntVar()
lenminvalue = tk.IntVar()
lenmaxvalue = tk.IntVar() 
button_cond = False

#Variable Upper Lower HSV White Pepper
upperhuewhite = 0
uppersaturationwhite = 0
uppervaluewhite = 0
lowerhuewhite = 0
lowersaturationwhite = 0
lowervaluewhite = 0

#Variable Upper Lower HSV Black Pepper
upperhueblack = 0
uppersaturationblack = 0
uppervalueblack = 0
lowerhueblack = 0
lowersaturationblack = 0
lowervalueblack = 0

# Fungsi HSV
def set_range (upperhue, uppersaturation, uppervalue, lowerhue, lowersaturation, lowervalue):
    upperhue_scale.set(upperhue)
    uppersaturation_scale.set(uppersaturation)
    uppervalue_scale.set(uppervalue)
    lowerhue_scale.set(lowerhue)
    lowersaturation_scale.set(lowersaturation)
    lowervalue_scale.set(lowervalue)

def setHsv():
    global button_cond
    if buttonselect.config("text")[-1] == "Select":
        button_cond = True
        color_set = color.get()
        if color_set == "White Pepper":
            set_range(179, 158, 255, 0, 0,122 )
        elif color_set == "Black Pepper" :
            set_range(37, 168, 98, 0,0,0)
        buttonselect.config(text="Deselect")
    elif buttonselect.config("text")[-1] == "Deselect":
        button_cond = False
        buttonselect.config(text="Select")
                  
# buttonSelect
def update():
    global upperhuewhite, uppersaturationwhite, uppervaluewhite, lowerhuewhite, lowersaturationwhite, lowervaluewhite
    global upperhueblack, uppersaturationblack, uppervalueblack, lowerhueblack, lowersaturationblack, lowervalueblack
    
    ret, frame = cap.read()
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame = cv2.flip(frame, 1)
    frame = cv2.resize(frame, (393, 293))
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    if color.get() == "White Pepper" and button_cond == True:
        upperhuewhite = upperhue.get()
        uppersaturationwhite = uppersaturation.get()
        uppervaluewhite = uppervalue.get()
        lowerhuewhite = lowerhue.get()
        lowersaturationwhite = lowersaturation.get()
        lowervaluewhite = lowervalue.get()
        

    elif color.get() == "Black Pepper" and button_cond == True:
        upperhueblack = upperhue.get()
        uppersaturationblack = uppersaturation.get()
        uppervalueblack = uppervalue.get()
        lowerhueblack = lowerhue.get()
        lowersaturationblack = lowersaturation.get()
        lowervalueblack = lowervalue.get()

    lowerwhite = np.array([lowerhuewhite,lowersaturationwhite,lowervaluewhite])
    upperwhite = np.array([upperhuewhite,uppersaturationwhite,uppervaluewhite])
    lowerblack = np.array([lowerhueblack,lowersaturationblack,lowervalueblack])
    upperblack = np.array([upperhueblack,uppersaturationblack,uppervalueblack])

    maskwhite = cv2.inRange(hsv, lowerwhite, upperwhite)
    maskblack = cv2.inRange(hsv, lowerblack, upperblack)
    # Gabungkan semua mask menjadi satu mask dengan bitwise OR
    combined_mask = cv2.bitwise_or(maskwhite, maskblack)

    # Lakukan dilasi pada mask dengan kernel elips
    kernel_elipse = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    dilatedmaskblack = cv2.dilate(maskblack, kernel_elipse, iterations=3)
    dilatedmaskwhite = cv2.dilate(maskwhite, kernel_elipse, iterations=1)
    edgewhite = cv2.Canny(dilatedmaskwhite,240,255)
    edgeblack = cv2.Canny(dilatedmaskblack,240,255)

    # Membuat Edge
    edge_combined = cv2.Canny(combined_mask, 240, 255)
    edge_combined = cv2.cvtColor(edge_combined, cv2.COLOR_BGR2RGB)

    #Membuat kontur
    contourswhite , hierarchywhite = cv2.findContours(edgewhite,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    contoursblack , hierarchyblack = cv2.findContours(edgeblack,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)

    lenmax = contourmax_scale.get()
    lenmin= contourmin_scale.get()
    validcontourswhite = [contourwhite for contourwhite in contourswhite if lenmin <= len(contourwhite) <= lenmax]
    validcontoursblack = [contourblack for contourblack in contoursblack if lenmin <= len(contourblack) <= lenmax]
   
   # Hitung jumlah kontur putih
    numwhite= len(validcontourswhite)
    numblack= len(validcontoursblack)
    totalnum = numwhite + numblack
    
    # # Update nilai pepper
    label_qw.config(text=str(numwhite))
    label_qb.config(text=str(numblack))
    label_qt.config(text= str(totalnum))

    if ret:
        imagecam = Image.fromarray(frame)
        photocam = ImageTk.PhotoImage(image=imagecam)
        labelcam.config(image=photocam)
        labelcam.image = photocam

        #Result
        resultwhite = cv2.drawContours(frame.copy(), validcontourswhite, -1, (255, 255, 255), 2)
        resultblack = cv2.drawContours(frame.copy(), validcontoursblack, -1, (0, 0, 0), 2)
        alpha = 0.5  # Bobot untuk gambar pertama
        beta = 0.5   # Bobot untuk gambar kedua
        gamma = 1    # Peningkatan konstan
        result = cv2.addWeighted(resultwhite, alpha, resultblack, beta, gamma)
        
        imageresult = Image.fromarray(result)
        photoresult = ImageTk.PhotoImage(image = imageresult)
        labelresult.config (image = photoresult)
        labelresult.image = photoresult

        # Gabungkan keempat maska menjadi satu gambar
        combined_mask = cv2.add(maskwhite, maskblack)

        # Konversi gambar maska ke format RGB agar dapat ditampilkan di Tkinter
        combined_mask_rgb = cv2.cvtColor(combined_mask, cv2.COLOR_BGR2RGB)
        combined_mask_image = Image.fromarray(combined_mask_rgb)

        # Tampilkan gambar maska yang telah digabungkan di label yang sesuai
        combined_mask_photo = ImageTk.PhotoImage(image=combined_mask_image)
        labelmask.config(image=combined_mask_photo)
        labelmask.image = combined_mask_photo
    tab1.after(10, update)

# Membuat label Judul
label = tk.Label(tab1, text="Pepper Color Detection", font=fonttitle)
label.place(x=590, y=22,height=32,width=300)  

# Membuat Frame Result
frame_result = tk.Frame(tab1, relief="solid", borderwidth=3 )
frame_result.place(x=435,y=80,height=296,width=396)
labelresult= tk.Label(tab1)
labelresult.place(x=438, y=83, height=290, width=390)
labelr= tk.Label(tab1, text="Result", font=fontframe)
labelr.place(x=608, y=381, height=29,width=70) 

# Membuat Frame Calibration Size
frame_cs = tk.Frame(tab1, relief="solid", borderwidth=3 )
frame_cs.place(x=845,y=80,height=296,width=182)
#Tambahkan batasan minimum kontur
contourmin_scale = tk.Scale (tab1, variable=lenminvalue, from_= 230, to = 0, orient= "vertical")
contourmin_scale.set(45) 
contourmin_scale.place(x=852, y=134, width=80, height=213)
#Tambahkan batasan miksimal kontur
contourmax_scale = tk.Scale (tab1,  variable=lenmaxvalue, from_= 230, to = 0, orient= "vertical")
contourmax_scale.set(200) 
contourmax_scale.place(x=932, y=134, width=80, height=213)
labeltmin= tk.Label(tab1, text="Minimal", font=fontinframe)
labeltmin.place(x=857, y=90, height=40,width=68)
labeltmax= tk.Label(tab1, text="Maximal", font=fontinframe)
labeltmax.place(x=937, y=90, height=40,width=68)
labelr= tk.Label(tab1, text="Calibration Size", font=fontframe)
labelr.place(x=877, y=381, height=29,width=130) 

# Frame Quantity
frame_quantity = tk.Frame(tab1, relief="solid", borderwidth=3 )
frame_quantity.place(x=1046,y=80,height=296,width=295)
labeltextwp = tk.Label(tab1, text="White Pepper", font=fontinframe)
labeltextwp.place(x=1068, y=130, height=26,width=125) 
label_qw = tk.Label(tab1, text= "0", font=fontinframe)
label_qw.place(x=1251, y=130, height=26,width=50) 
labeltextbp = tk.Label(tab1, text="Black Pepper", font=fontinframe)
labeltextbp.place(x=1068, y=202, height=26,width=115) 
label_qb = tk.Label(tab1, text="0", font=fontinframe)
label_qb.place(x=1261, y=202, height=26,width=27) 
labeltextqt = tk.Label(tab1, text="Total Pepper", font=fontinframe)
labeltextqt.place(x=1072, y=278, height=26,width=115) 
label_qt = tk.Label(tab1, text="0", font=fontinframe)
label_qt.place(x=1261, y=278, height=26,width=27) 
labelq = tk.Label(tab1, text="Quantity", font=fontframe)
labelq.place(x=1150, y=381, height=26,width=83) 

# Membuat Frame Camera
frame_cam = tk.Frame(tab1,  relief="solid", borderwidth=3 )
frame_cam.place(x=23,y=80,height=296,width=396)
labelcam = tk.Label(tab1)
labelcam.place(x=26, y=83,height=290,width=390)
labelc= tk.Label (tab1, text="Camera", font=fontframe)
labelc.place(x=185, y=381, height=29,width=70) 

#Frame Mask
frame_mask = tk.Frame(tab1, relief="solid", borderwidth=3 )
frame_mask.place(x=26,y=423,height=296,width=396)
labelmask =tk.Label(tab1)
labelmask.place(x=29, y=426,height=290, width=390)
labelm= tk.Label(tab1, text="Masking", font=fontframe)
labelm.place(x=185, y=721, height=29,width=70)   

# Frame Calibration
frame_calibration = tk.Frame(tab1, relief="solid", borderwidth=3 )
frame_calibration.place(x=435,y=423,height=296,width=905)
intial_option = "Select Color"
index_combobox = ttk.Combobox(tab1,text = "Select a Color",textvariable=color, font=fontinframe,state="readonly")
index_combobox.place(x=800, y=449, width=180, height=31)
index_combobox.set(intial_option)
index_list = ["White Pepper", "Black Pepper"]  #isi combobox dengan daftar port yang tersedia
index_combobox["values"] = index_list
buttonselect = tk.Button(tab1, text="Select", command=setHsv, bg="#BABABA")
buttonselect.place(x=990,y=449,height=31,width=75) 

#Upper Scale
upperhue_scale = tk.Scale(tab1, variable=upperhue, from_=0,  to=179, orient="horizontal")
upperhue_scale.place(x=471, y=520, width=380, height=40)
uppersaturation_scale = tk.Scale(tab1, variable=uppersaturation, from_=0,  to=255, orient="horizontal")
uppersaturation_scale.place(x=471, y=588, width=380, height=40)
uppervalue_scale = tk.Scale(tab1, variable=uppervalue, from_=0,  to=255, orient="horizontal")
uppervalue_scale.place(x=471, y=657, width=380, height=40)

#Lower Scale
lowerhue_scale = tk.Scale(tab1, variable=lowerhue, from_=0,  to=179, orient="horizontal")
lowerhue_scale.place(x=935, y=520, width=380, height=40)
lowersaturation_scale = tk.Scale(tab1, variable=lowersaturation, from_=0,  to=255, orient="horizontal")
lowersaturation_scale.place(x=935, y=588, width=380, height=40)
lowervalue_scale = tk.Scale(tab1, variable=lowervalue, from_=0,  to=255, orient="horizontal")
lowervalue_scale.place(x=935, y=657, width=380, height=40)

#Label Scale
labelsetupper = tk.Label(tab1, text="Set Upper", font=fontinframe,)
labelsetupper.place(x=600, y=500, height=26,width=85) 
labelsetlower = tk.Label(tab1, text="Set Lower", font=fontinframe)
labelsetlower.place(x=1078, y=500, height=26,width=85) 
labelhue = tk.Label(tab1, text="Hue", font=fontinframe)
labelhue.place(x=875, y=535, height=26,width=40) 
labelsaturation = tk.Label(tab1, text="Saturation", font=fontinframe)
labelsaturation.place(x=845, y=608, height=26,width=90) 
labelvalue = tk.Label(tab1, text="Value", font=fontinframe)
labelvalue.place(x=870, y=676, height=26,width=50)
labelcalibration = tk.Label(tab1, text="Calibration Color", font=fontframe)
labelcalibration.place(x=848, y=721, height=26,width=140) 

#Tampilan Tab Bantuan dan Tentang
image2 = Image.open("Intruction.png")
help_image = ImageTk.PhotoImage(image2)
help_label = tk.Label(tab2, image=help_image)
help_label.place(x=0, y=0)
image3 = Image.open("About.png")
about_image = ImageTk.PhotoImage(image3)
about_label = tk.Label(tab3, image=about_image)
about_label.place(x=0,y=0)

update() # Memanggil fungsi update untuk menampilkan video secara terus-menerus
# Memulai main loop
tab1.mainloop()
