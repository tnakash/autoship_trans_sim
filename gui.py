import tkinter.ttk as ttk
import tkinter as tk
import tkinter.scrolledtext as st
import PIL.ImageTk as itk
import tkinter.filedialog as dlg
from main import *

root = tk.Tk()
root.title("Autonomous Ship Transition Simulator")
# root.iconbitmap(c:/gui)
root.geometry("1200x800")

label = tk.Label(text='Casename')
label.grid(row=0,column=0)

# Create Menu
mymenu = tk.Menu(root)
filemenu = tk.Menu(mymenu, tearoff=0)
filemenu.add_command(label='Select Folder', command=lambda : dlg.askdirectory(initialdir='P:/'))
filemenu.add_command(label='Select File', command=lambda : dlg.askopenfilename(filetypes=[("", "*")], initialdir='P:/'))
filemenu.add_command(label='Save File', command=lambda :dlg.asksaveasfilename(filetypes=[("", "*")], initialdir='P:/'))
filemenu.add_separator()
filemenu.add_command(label='Quit', command=quit)
mymenu.add_cascade(label='File', menu=filemenu)
root.config(menu=mymenu)

# Input and get Casename
entry_case = tk.Entry()
entry_case.place(x=80, y=0)
entry_case.insert(tk.END,"test_0331")

def label_casename():
    casename = entry_case.get()
    entry_case.delete(0, tk.END)
    label = tk.Label(text=casename)
    label.place(x=20, y=20)
    main(casename)

button_case = tk.Button(text="Simulation Start")
button_case.place(x=300, y=0)

button_case["command"]=lambda: label_casename()

def set_investment(cost,i,delay):
    invest = entry_inv.get()
    entry_inv.delete(0, tk.END)
    label = tk.Label(text=invest)
    label.place(x=20, y=60)
    investment(cost, i, delay, invest)

entry_inv = tk.Entry()
entry_inv.place(x=80, y=40)
entry_inv.insert(tk.END,"Comm/Situ/Plan/Exec")

button_inv = tk.Button(text="Investment")
button_inv.place(x=300, y=40)

button_inv["command"] = lambda: set_investment(cost,i)

# scale = tk.Scale(from_=0,to=100,variable=tk.DoubleVar(),orient=tk.HORIZONTAL,command=lambda e : myfunc(e,scale.get()),width=10,length=160)
# scale.grid(row=10,column=100,columnspan=1)
# print(scale)

root.mainloop()

# #コンボボックスの生成
# combobox = ttk.Combobox(textvariable=tk.StringVar(),values=['check1','check2','check3'], width=18)
# combobox.set('check1')
# combobox.bind("<<ComboboxSelected>>",lambda e : myfunc(e,combobox.get()))
# combobox.grid(row=0,column=5,padx=5)

# #スライダーの生成
# scale = tk.Scale(from_=0,to=1,variable=tk.DoubleVar(),orient=tk.HORIZONTAL,command=lambda e : myfunc(e,scale.get()),width=10,length=160)
# scale.grid(row=1,column=0,columnspan=1)

# #プログレスバーの生成
# pval = tk.IntVar(value=0)
# progress = ttk.Progressbar(orient=tk.HORIZONTAL,variable=pval,maximum=10,length=160, mode='determinate')
# progress.grid(row=1, column=2,columnspan=2)

# #スピンボックスの生成
# spinbox = ttk.Spinbox(from_=0.0, to=9.0, textvariable=tk.StringVar(),width=10,command=lambda :pval.set(pval.get() + 1))
# spinbox.set(0)
# spinbox.grid(row=0,column=6)

# #リストボックスの生成
# listbox = tk.Listbox(listvariable=tk.StringVar(value=['list1','list2','list3']), selectmode='browse',width=20,height=8)
# listbox.bind('<<ListboxSelect>>', lambda e : myfunc(e,listbox.curselection()))
# listbox.grid(row=2,column=4,columnspan=2)

# #キャンバスの生成
# img = itk.PhotoImage(file = '/Users/nakashima/Pictures/test.jpg')
# canvas = tk.Canvas(width=100,height=180,background='red')
# canvas.create_image(0,0,image=img,anchor=tk.NW)
# canvas.create_rectangle(10, 80, 90, 150, fill = 'red', stipple = 'gray25')
# canvas.grid(row=1,column=6,rowspan=2)

# おそらく正しい書き方はこれ
# app = Application(master=root)

# class Application(tk.Frame):
#     def __init__(self, master=None)
#         super().__init__(master)
#         self.master.geometry("Autonomous Ship Transition Simulator")

#         self.menu_bar = tk.Menu(self.master)
#         self.create_widgets()
    
#     def input(self, action):
#         self.entry.insert(tk.END, action)
    
#     def create_widgets(self):
#         tk.Button(self.master, text='Comm', width=3,
#                   command=lambda: self.input("Comm")).grid(row=1,column=0)
#         tk.Button(self.master, text='Situ', width=3,
#                   command=lambda: self.input("Situ")).grid(row=2,column=0)
#         tk.Button(self.master, text='Plan', width=3,
#                   command=lambda: self.input("Plan")).grid(row=3,column=0)
#         tk.Button(self.master, text='Exec', width=3,
#                   command=lambda: self.input("Exec")).grid(row=4,column=0)

# app.mainloop()

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master.title("Autonomous Ship Transition Simulator")
        self.master.geometry("1200x800")

        # self.menu_bar = tk.Menu(self.master)
        self.menu_bar = create_menu(self.master)
        self.create_widgets()
            
    def create_widgets():
        A_ALTCHARSET
    
    # Create Menu
    def create_menu(self, root):
        self.mymenu = tk.Menu(root)
        filemenu = tk.Menu(self.mymenu, tearoff=0)
        filemenu.add_command(label='Select Folder', command=lambda : dlg.askdirectory(initialdir='P:/'))
        filemenu.add_command(label='Select File', command=lambda : dlg.askopenfilename(filetypes=[("", "*")], initialdir='P:/'))
        filemenu.add_command(label='Save File', command=lambda :dlg.asksaveasfilename(filetypes=[("", "*")], initialdir='P:/'))
        filemenu.add_separator()
        filemenu.add_command(label='Quit', command=quit)
        self.mymenu.add_cascade(label='File', menu=filemenu)
        root.config(menu=self.mymenu)


root = tk.Tk()
root.title("Autonomous Ship Transition Simulator")
# root.iconbitmap(c:/gui)
root.geometry("1200x800")

label = tk.Label(text='Casename')
label.grid(row=0,column=0)


# Input and get Casename
entry_case = tk.Entry()
entry_case.place(x=80, y=0)
entry_case.insert(tk.END,"test_0331")

def label_casename():
    casename = entry_case.get()
    entry_case.delete(0, tk.END)
    label = tk.Label(text=casename)
    label.place(x=20, y=20)
    main(casename)

button_case = tk.Button(text="Simulation Start")
button_case.place(x=300, y=0)

button_case["command"]=lambda: label_casename()

def set_investment(cost,i,delay):
    invest = entry_inv.get()
    entry_inv.delete(0, tk.END)
    label = tk.Label(text=invest)
    label.place(x=20, y=60)
    investment(cost, i, delay, invest)
    

entry_inv = tk.Entry()
entry_inv.place(x=80, y=40)
entry_inv.insert(tk.END,"Comm/Situ/Plan/Exec")

button_inv = tk.Button(text="Investment")
button_inv.place(x=300, y=40)

# scale = tk.Scale(from_=0,to=100,variable=tk.DoubleVar(),orient=tk.HORIZONTAL,command=lambda e : myfunc(e,scale.get()),width=10,length=160)
# scale.grid(row=10,column=100,columnspan=1)
# print(scale)

root.mainloop()