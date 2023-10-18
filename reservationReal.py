import requests
import cv2
import numpy as np
from io import BytesIO # Import BytesIO from the io module
from tkinter import *
from tkinter import messagebox  
from tkinter import ttk       
from PIL import Image, ImageTk
from time import strftime
import sqlite3
from matplotlib.figure import Figure                                # for Graph
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt  # Added this import
import smtplib
import random
import string
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Create table database
conn = sqlite3.connect("MyRestaurant.db")
c = conn.cursor ()

# สร้าง Database
try :
    # Database เก็บข้อมูลคิวจองโต๊ะ
    c.execute('''CREATE TABLE queueTable(id integer PRIMARY KEY AUTOINCREMENT,
            tableNO varchar(5) NOT NULL,
            name varchar(30) NOT NULL,
            phoneNum varchar(30) NOT NULL)''')

    # Database เก็บข้อมูลเช็คบิลโต๊ะ
    c.execute('''CREATE TABLE billTable(id integer PRIMARY KEY AUTOINCREMENT,
            tableNO varchar(5) NOT NULL,
            idFood varchar(5) NOT NULL,
            food varchar(30) NOT NULL,
            price varchar(30) NOT NULL,
            amount varchar(30) NOT NULL)''')
    
    # Database เก็บสมาชิกร้านค้า
    c.execute('''CREATE TABLE customerMember(id integer PRIMARY KEY AUTOINCREMENT,
            name varchar(30) NOT NULL,
            phoneNum varchar(30) NOT NULL)''')
    
    # Database เมนูอาหาร
    c.execute('''CREATE TABLE foodLists(id integer PRIMARY KEY AUTOINCREMENT,
            food varchar(30) NOT NULL,
            price varchar(10) NOT NULL)''')
    
    # Database เก็บประวัติการคิดเงิน
    c.execute('''CREATE TABLE historyBill(id integer PRIMARY KEY AUTOINCREMENT,
            dmy varchar(20) NOT NULL,
            day varchar(2) NOT NULL,
            month varchar(20) NOT NULL,
            year varchar(4) NOT NULL,
            hm varchar(6) NOT NULL,  
            food varchar(30) NOT NULL,
            amount varchar(2) NOT NULL
            price varchar(10) NOT NULL,
            summary varchar(5) NOT NULL)''')
except :
    pass

""" DATABASE LIST

 queueTable = tableNO, name, phoneNum
 billTable = tableNO, food, price, amount
 customerMember = name, phoneNum
 foodLists = food, price
 historyBill = dmy,day,month,year,hm,food,price

 """
# Global variable to keep track of the current window
current_window = None
foodList_window = None
clock = None

# Setting For Clock
def runTime () :
        timeString = strftime("%d %B %Y\n%H:%M:%S %p")
        if clock :
            clock.config(text = timeString)
        current_window.after(1000, runTime)

'''         WINDOWS         '''

'''         Customer Side       '''
def foodListShow () :
    global foodList_window

    # Setting Window
    foodList_window = Toplevel (current_window)
    foodList_window.title("Restaurant")
    foodList_window.geometry("1000x600+300+100")
    foodList_window.resizable(False,False)
    foodList_window.title("My restaurant")  

    # Background
    menuFoodBG = Image.open("menuFood_BG.png")
    BG_menuFood = ImageTk.PhotoImage(menuFoodBG)
    BG = Label(foodList_window, image = BG_menuFood)
    BG.pack()
    BG.image = BG_menuFood

def customerShowTable():
    global current_window
    if current_window:
        current_window.destroy()

    queueAllTable = [0,0,0,0,0,0]

    # Setting Window
    current_window = Tk ()
    current_window.title("Restaurant")
    current_window.geometry("1000x600+300+100")
    current_window.resizable(False,False)
    current_window.title("My restaurant") 

    # Background
    reservation_BG = Image.open("reservation_BG1.png")
    BG_Reservation = ImageTk.PhotoImage(reservation_BG)
    BG = Label(current_window, image = BG_Reservation)
    BG.pack()
    BG.image = BG_Reservation

    # Go back button
    backPic = Image.open("backBttn.png")
    backBttn = ImageTk.PhotoImage(backPic)
    back_button = Button(current_window, image = backBttn, activebackground = "#e8dfab", cursor = "hand2",
                         borderwidth = 0, justify = CENTER, bg = "#e8dfab", command = homeFunc)
    back_button.config(borderwidth = 0)
    back_button.place(x = 68, y = 35)
    back_button.image = backBttn
    
    # Reservation Windows

    def reservationTable (tableNO) :

        global current_window
        if current_window:
            current_window.destroy ()

        # Setting Window
        current_window = Tk ()
        current_window.title("Restaurant")
        current_window.geometry("1000x600+300+100")
        current_window.resizable(False,False)
        current_window.title("My restaurant")
        

        reservation_BG = Image.open("reservation_customerShow.png")
        BG_Reservation = ImageTk.PhotoImage(reservation_BG)
        BG = Label(current_window, image = BG_Reservation)
        BG.pack()
        BG.image = BG_Reservation
        
        # To home button
        homePic = Image.open("homeBttn.png")
        homePic = homePic.resize((int(homePic.width * 1.1), int(homePic.height * 1.1)))
        homeBttn = ImageTk.PhotoImage(homePic)
        home_Button = Button(current_window, image = homeBttn, borderwidth = 0, justify = CENTER, bg = "#e8dfab", command = customerShowTable)
        home_Button.config(borderwidth = 0)
        home_Button.place(x = 68, y = 35)
        home_Button.image = homeBttn

        # Title
        Table = Label(current_window, text = ("Table no." + str(tableNO)), font = ("Bebas Neue Regular", 35 ))
        Table.configure(fg = "#ff7048", bg = "#e8dfab", bd = 0, relief = "solid")
        Table.place (x = 280, y = 130)

        # QUEUE TABLE #
        def queueInTable(tableNO):
            queueTable = Frame(current_window, height=350, width=620, bg="#e8dfab")
            queueTable.place(x=310, y=215)

            # Setting TABLE
            tree = ttk.Treeview(queueTable, columns=("Queue","Name",))
            tree.heading("Queue", text="ลำดับคิวที่")
            tree.heading("Name", text="ชื่อ")
            tree.column("Queue", anchor="center", width = 200)
            tree.column("Name", anchor="center", width = 200)
            tree.column("#0", width=0, stretch= NO)
            style = ttk.Style()
            style.configure("Treeview.Heading", font = ("DB HELVETHAICA X BD EXT", 25))
            
            c.execute('''SELECT id, tableNO, name FROM queueTable''')
            showData = c.fetchall()  
            count = 1
            for row in showData:
                if int(tableNO) == int(row[1]):
                    tree.insert("","end", values=(count,row[2]))
                    count += 1
            tree.pack()
        queueInTable(tableNO)
            
    # Update Queue Real-time
    def updateQueueRealtime (table) :
        queueAllTable[table-1] = 0
        c.execute('''SELECT id,tableNO FROM queueTable''')
        allQueue = c.fetchall()
        for x,y in allQueue :
            if int(y) == int(table) :
                queueAllTable[table-1] += 1
        current_window.after(100,lambda: updateQueueRealtime(table))

    # Table 1
        # Table 1 Button!
    table1_import = Image.open("bttn_Table1.png")
    table1_import = table1_import.resize((int(table1_import.width*0.85),int(table1_import.height*0.85)))
    table1 = ImageTk.PhotoImage(table1_import)
    table1_Button = Button(current_window, image = table1, justify = CENTER,  activebackground = "#e8dfab", cursor = "hand2",
                           borderwidth = 0, bg = "#e8dfab", command=lambda: reservationTable(1))
    table1_Button.place(x = 205, y = 115)
    table1_Button.image = table1

    table1_status = Label(current_window, text = "", justify = CENTER, bg = "#e8dfab")
        # Table 1 status!
    def updateStatusTable1 () :
        
        if queueAllTable[0] == 0 :
                table1_status.config(text = "ว่าง", font = ("DB HELVETHAICA X BD EXT",30), fg = "green")
                table1_status.place(x = 258, y = 280)
        elif queueAllTable[0] > 0 :
            table1_status.config(text = ("มี " + str(queueAllTable[0]) + " คิวก่อนหน้า"),font = ("DB HELVETHAICA X BD EXT",25), fg = "red")
            table1_status.place(x = 200, y = 284)
        current_window.after(100,updateStatusTable1)
    
    updateQueueRealtime (1)
    updateStatusTable1 ()

    # Table 2
        # Table 2 Button!
    table2_import = Image.open("bttn_Table2.png")
    table2_import = table2_import.resize((int(table2_import.width*0.85),int(table2_import.height*0.85)))
    table2 = ImageTk.PhotoImage(table2_import)
    table2_Button = Button(current_window, image = table2, justify = CENTER,
                           borderwidth = 0, bg = "#e8dfab", activebackground = "#e8dfab", cursor = "hand2",
                           command=lambda: reservationTable(2))
    table2_Button.place(x = 410, y = 115)
    table2_Button.image = table2

    table2_status = Label(current_window, text = "", justify = CENTER, bg = "#e8dfab")
        # Table 2 status!
    def updateStatusTable2 () :
        
        if queueAllTable[1] == 0 :
            table2_status.config(text = "ว่าง", font = ("DB HELVETHAICA X BD EXT",30), fg = "green")
            table2_status.place(x = 462, y = 280)
        elif queueAllTable[1] > 0 :
            table2_status.config(text = ("มี " + str(queueAllTable[1]) + " คิวก่อนหน้า"),font = ("DB HELVETHAICA X BD EXT",25), fg = "red")
            table2_status.place(x = 410, y = 284)
        current_window.after(100,updateStatusTable2)
    
    updateQueueRealtime (2)
    updateStatusTable2 ()

    # Table 3

        # Table 3 Button!
    table3_import = Image.open("bttn_Table3.png")
    table3_import = table3_import.resize((int(table3_import.width*0.85),int(table3_import.height*0.85)))
    table3 = ImageTk.PhotoImage(table3_import)
    table3_button = Button(current_window, image = table3, justify = CENTER,
                           activebackground = "#e8dfab", cursor = "hand2",
                           borderwidth = 0, bg = "#e8dfab", command=lambda: reservationTable(3))
    table3_button.place(x = 615, y = 115)
    table3_button.image = table3

    table3_status = Label(current_window, text = "", justify = CENTER, bg = "#e8dfab")
        # Table 3 status!
    def updateStatusTable3 () :
        
        if queueAllTable[2] == 0 :
            table3_status.config(text = "ว่าง", font = ("DB HELVETHAICA X BD EXT",30), fg = "green")
            table3_status.place(x = 666, y = 280)
        elif queueAllTable[2] > 0 :
            table3_status.config(text = ("มี " + str(queueAllTable[2]) + " คิวก่อนหน้า"),font = ("DB HELVETHAICA X BD EXT",25), fg = "red")
            table3_status.place(x = 620, y = 284)
        current_window.after(100,updateStatusTable2)
    
    updateQueueRealtime (3)
    updateStatusTable3 ()

    # Table 4

        # Table 4 Button!
    table4_import = Image.open("bttn_Table4.png")
    table4_import = table4_import.resize((int(table4_import.width*0.85),int(table4_import.height*0.85)))
    table4 = ImageTk.PhotoImage(table4_import)
    table4_button = Button(current_window, image = table4, justify = CENTER,
                           activebackground = "#e8dfab", cursor = "hand2",
                           borderwidth = 0, bg = "#e8dfab", command=lambda: reservationTable(4))
    table4_button.place(x = 205, y = 350)
    table4_button.image = table4

    table4_status = Label(current_window, text = "", justify = CENTER, bg = "#e8dfab")
        # Table 4 status!
    def updateStatusTable4 () :
        
        if queueAllTable[3] == 0 :
            table4_status.config(text = "ว่าง", font = ("DB HELVETHAICA X BD EXT",30), fg = "green")
            table4_status.place(x = 258, y = 515)
        elif queueAllTable[3] > 0 :
            table4_status.config(text = ("มี " + str(queueAllTable[3]) + " คิวก่อนหน้า"),font = ("DB HELVETHAICA X BD EXT",25), fg = "red")
            table4_status.place(x = 200, y = 519)
        current_window.after(100,updateStatusTable2)
    
    updateQueueRealtime (4)
    updateStatusTable4 ()

    # Table 5
        # Table 5 Button!
    table5_import = Image.open("bttn_Table5.png")
    table5_import = table5_import.resize((int(table5_import.width*0.85),int(table5_import.height*0.85)))
    table5 = ImageTk.PhotoImage(table5_import)
    table5_Button = Button(current_window, image = table5, justify = CENTER,
                           activebackground = "#e8dfab", cursor = "hand2",
                           borderwidth = 0, bg = "#e8dfab", command=lambda: reservationTable(5))
    table5_Button.place(x = 410, y = 350)
    table5_Button.image = table5

    table5_status = Label(current_window, text = "", justify = CENTER, bg = "#e8dfab")
        # Table 5 status!
    def updateStatusTable5 () :
        
        if queueAllTable[4] == 0 :
            table5_status.config(text = "ว่าง", font = ("DB HELVETHAICA X BD EXT",30), fg = "green")
            table5_status.place(x = 462, y = 515)
        elif queueAllTable[4] > 0 :
            table5_status.config(text = ("มี " + str(queueAllTable[4]) + " คิวก่อนหน้า"),font = ("DB HELVETHAICA X BD EXT",25), fg = "red")
            table5_status.place(x = 410, y = 519)
        current_window.after(100,updateStatusTable2)
    
    updateQueueRealtime (5)
    updateStatusTable5 ()
    
    # Table 6

        # Table 6 Button!
    table6_import = Image.open("bttn_Table6.png")
    table6_import = table6_import.resize((int(table6_import.width*0.85),int(table6_import.height*0.85)))
    table6 = ImageTk.PhotoImage(table6_import)
    table6_button = Button(current_window, image = table6, justify = CENTER,
                           activebackground = "#e8dfab", cursor = "hand2",
                           borderwidth = 0, bg = "#e8dfab", command=lambda: reservationTable(6))
    table6_button.place(x = 615, y = 350)
    table6_button.image = table6

    table6_status = Label(current_window, text = "", justify = CENTER, bg = "#e8dfab")
        # Table 3 status!
    def updateStatusTable6 () :
        
        if queueAllTable[5] == 0 :
            table6_status.config(text = "ว่าง", font = ("DB HELVETHAICA X BD EXT",30), fg = "green")
            table6_status.place(x = 666, y = 515)
        elif queueAllTable[5] > 0 :
            table6_status.config(text = ("มี " + str(queueAllTable[5]) + " คิวก่อนหน้า"),font = ("DB HELVETHAICA X BD EXT",25), fg = "red")
            table6_status.place(x = 620, y = 519)
        current_window.after(100,updateStatusTable2)
    
    updateQueueRealtime (6)
    updateStatusTable6 ()

'''         Staff Side          '''
def homeFunc ():
    global current_window, clock
    if current_window:
        current_window.destroy()

    # Setting Window
    current_window = Tk ()
    current_window.title("Restaurant")
    current_window.geometry("1000x600+300+100")
    current_window.resizable(False,False)
    current_window.title("My restaurant")  

    # Background
    homepageBG = Image.open("Homepage_BG.png")
    BG_homepage = ImageTk.PhotoImage(homepageBG)
    BG = Label(current_window, image = BG_homepage)
    BG.pack()
    BG.image = BG_homepage

    # Clock
    clock = Label(current_window, font = ("DB HELVETHAICAMON X BD", 20), justify = CENTER, fg = "#009e5f", bg = "#e8dfab")
    clock.place(x = 700, y = 10)
    runTime ()

    # To Staff Login Button
    nextPageClick = Image.open("HomeMenu_Bttn.png")
    toStaffLoginButton = ImageTk.PhotoImage(nextPageClick)
    bttn1 = Button(current_window, image = toStaffLoginButton, borderwidth = 0, activebackground = "#2ea06f", cursor = "hand2", 
                   justify = CENTER, bg = "#2ea06f", command = staffLoginFunc)
    bttn1.place(x = 718, y = 450)
    bttn1.image = toStaffLoginButton

    # TO Reservation Page Button
    reservationButton = ImageTk.PhotoImage(nextPageClick)
    bttn2 = Button(current_window, image = reservationButton, borderwidth = 0, activebackground = "#ff7048", cursor = "hand2", 
                   justify = CENTER, bg = "#ff7048", command = customerShowTable)
    bttn2.place(x = 470, y = 450)
    bttn2.image = reservationButton

    # TO Food List Button
    moreClick = Image.open("HomeMenu_MoreBttn.png")
    moreClick_bttn = ImageTk.PhotoImage(moreClick)
    bttn2 = Button(current_window, image = moreClick_bttn, borderwidth = 0, activebackground = "#307d9b", cursor = "hand2",
                   justify = CENTER, bg = "#307d9b", command = foodListShow)
    bttn2.place(x = 490, y = 210)
    bttn2.image = moreClick_bttn

def staffLoginFunc():
    global current_window, clock
    if current_window:
        current_window.destroy()
    
    # Setting Window
    current_window = Tk ()
    current_window.title("Restaurant")
    current_window.geometry("1000x600+300+100")
    current_window.resizable(False,False)
    current_window.title("My restaurant")

    # Background
    staffLoginBG = Image.open("StaffLogin_BG.png")
    BG_staffLogin = ImageTk.PhotoImage(staffLoginBG)
    BG = Label(current_window, image = BG_staffLogin)
    BG.pack()
    BG.image = BG_staffLogin 

    # To home button
    homePic = Image.open("homeBttn.png")
    homePic = homePic.resize((int(homePic.width * 1.1), int(homePic.height * 1.1)))
    homeBttn = ImageTk.PhotoImage(homePic)
    home_Button = Button(current_window, image = homeBttn, borderwidth = 0, activebackground = "#e8dfab", cursor = "hand2",
                         justify = CENTER, bg = "#e8dfab", command = homeFunc)
    home_Button.config(borderwidth = 0)
    home_Button.place(x = 68, y = 35)
    home_Button.image = homeBttn
    
    # Clock
    clock = Label(current_window, font = ("DB HELVETHAICAMON X BD", 25), justify = CENTER, fg = "#009e5f", bg = "#e8dfab")
    clock.place(x = 730, y = 100)
    runTime ()

    # Password entry box
    key_input = StringVar()
    password = Entry(current_window, textvariable = key_input, width = 15, cursor = "ibeam",
                     bg = "#e8dfab", justify = CENTER, fg = "#ff7048" )
    password.config(font = ("DB HELVETHAICA X BD EXT", 30))
    password.config(borderwidth = 0)
    password.place(x = 365, y = 430)

    # Function for checking password
    def correct () :
        entered_password = key_input.get ()
        if (entered_password == "abc") :
            messagebox.showinfo(title = "รหัสผ่าน", message = "รหัสผ่านถูกต้อง")
            staffMenu ()
        else :
            messagebox.showerror(title = "รหัสผ่านไม่ถูกต้อง", message = "! รหัสผ่านไม่ถูกต้อง กรุณาลองอีกครั้ง !")
            password.delete(0,END)

    # To next page button
    nextPic = Image.open("nextButton.png")
    # nextPic = nextPic.resize((int(nextPic.width * 0.65), int(nextPic.height * 0.65)))
    nextBttn = ImageTk.PhotoImage(nextPic)
    bttn = Button(current_window, image = nextBttn, borderwidth = 0, activebackground = "#e8dfab", cursor = "hand2",
                  justify = CENTER, bg = "#e8dfab", command = correct)
    bttn.config(borderwidth = 0)
    bttn.place(x = 735, y = 410)
    bttn.image = nextBttn
    
def staffMenu():
    global current_window
    if current_window:
        current_window.destroy()
    
    # Setting Window
    current_window = Tk ()
    current_window.title("Restaurant")
    current_window.geometry("1000x600+300+100")
    current_window.resizable(False,False)
    current_window.title("My restaurant") 
    
    # Background
    staffMenuBG = Image.open("StaffMenu_BG.png")
    BG_staffMenu = ImageTk.PhotoImage(staffMenuBG)
    BG = Label(current_window, image = BG_staffMenu)
    BG.pack()
    BG.image = BG_staffMenu 

    # To home button
    homePic = Image.open("homeBttn.png")
    homePic = homePic.resize((int(homePic.width * 1.1), int(homePic.height * 1.1)))
    homeBttn = ImageTk.PhotoImage(homePic)
    home_Button = Button(current_window, image = homeBttn, activebackground = "#e8dfab", cursor = "hand2",
                         borderwidth = 0, justify = CENTER, bg = "#e8dfab", command = homeFunc)
    home_Button.config(borderwidth = 0)
    home_Button.place(x = 68, y = 35)
    home_Button.image = homeBttn

    # To Reservation page button
    reservePic = Image.open("1 reservation.png")
    picReserve = ImageTk.PhotoImage(reservePic)
    reserve_Button = Button(current_window, image = picReserve, command = reservationFunc)
    reserve_Button.place(x = 80, y = 120)
    reserve_Button.config(justify = CENTER, bg = "#e8dfab", borderwidth = 0, 
                          activebackground = "#e8dfab", cursor = "hand2")
    reserve_Button.image = picReserve

    # To Order/Bill page button
    orderPic = Image.open("2 order_and_bill.png")
    picOrder = ImageTk.PhotoImage(orderPic)
    order_button = Button(current_window, image = picOrder, command = orderFoodFunc)
    order_button.place(x = 80, y = 270)
    order_button.config(justify = CENTER, bg = "#e8dfab", borderwidth = 0,
                        activebackground = "#e8dfab", cursor = "hand2")
    order_button.image = picOrder

    # To Member Register page button
    memRegisterPic = Image.open("3 memberRegister.png")
    picMemRegister = ImageTk.PhotoImage(memRegisterPic)
    register_button = Button(current_window, image = picMemRegister, command = memberRegister)
    register_button.place(x = 80, y = 420)
    register_button.config(justify = CENTER, bg = "#e8dfab", borderwidth = 0,
                           activebackground = "#e8dfab", cursor = "hand2")
    register_button.image = picMemRegister

    # To income Statistics page button
    incomeStatsPic = Image.open("4 incomeStats.png")
    picIncomeStats = ImageTk.PhotoImage(incomeStatsPic)
    incomeStats_button = Button(current_window, image = picIncomeStats, command = incomeStatistic)
    incomeStats_button.place(x = 500, y = 120)
    incomeStats_button.config(justify = CENTER, bg = "#e8dfab", borderwidth = 0,
                              activebackground = "#e8dfab", cursor = "hand2")
    incomeStats_button.image = picIncomeStats

def reservationFunc ():
    global current_window
    if current_window:
        current_window.destroy()

    queueAllTable = [0,0,0,0,0,0]

    # Setting Window
    current_window = Tk ()
    current_window.title("Restaurant")
    current_window.geometry("1000x600+300+100")
    current_window.resizable(False,False)
    current_window.title("My restaurant") 

    # Background
    reservation_BG = Image.open("reservation_BG1.png")
    BG_Reservation = ImageTk.PhotoImage(reservation_BG)
    BG = Label(current_window, image = BG_Reservation)
    BG.pack()
    BG.image = BG_Reservation

    # Go back button
    backPic = Image.open("backBttn.png")
    backBttn = ImageTk.PhotoImage(backPic)
    back_button = Button(current_window, image = backBttn, activebackground = "#e8dfab", cursor = "hand2",
                         borderwidth = 0, justify = CENTER, bg = "#e8dfab", command = staffMenu)
    back_button.config(borderwidth = 0)
    back_button.place(x = 68, y = 35)
    back_button.image = backBttn

    # To Order MENU
    toOrderPic = Image.open("toOrderPage.png")
    picToOrder = ImageTk.PhotoImage(toOrderPic)
    toOrder_button = Button(current_window, image = picToOrder, activebackground = "#e8dfab", cursor = "hand2",
                            borderwidth = 0, justify = CENTER, bg = "#e8dfab", command = orderFoodFunc)
    toOrder_button.config(borderwidth = 0)
    toOrder_button.place(x = 750, y = 35)
    toOrder_button.image = picToOrder
    
    # Reservation Windows

    def reservationTable (tableNO) :
        global current_window
        if current_window:
            current_window.destroy ()
        # Setting Window
        current_window = Tk ()
        current_window.title("Restaurant")
        current_window.geometry("1000x600+300+100")
        current_window.resizable(False,False)
        current_window.title("My restaurant") 
        

        reservation_BG = Image.open("reservation_BG2.png")
        BG_Reservation = ImageTk.PhotoImage(reservation_BG)
        BG = Label(current_window, image = BG_Reservation)
        BG.pack()
        BG.image = BG_Reservation
        
        # Go back button
        backPic = Image.open("backBttn.png")
        backBttn = ImageTk.PhotoImage(backPic)
        back_button = Button(current_window, image = backBttn, activebackground = "#e8dfab", cursor = "hand2",
                            borderwidth = 0, justify = CENTER, bg = "#e8dfab", command = reservationFunc)
        back_button.config(borderwidth = 0)
        back_button.place(x = 68, y = 35)
        back_button.image = backBttn

        # Title
        Table = Label(current_window, text = ("Table no." + str(tableNO)), font = ("Bebas Neue Regular", 35 ))
        Table.configure(fg = "#ff7048", bg = "#e8dfab", bd = 0, relief = "solid")
        Table.place (x = 280, y = 130)
        
        # Entry & Button

            # Name Entry
        name_input = StringVar()
        nameEntry = Entry(current_window, textvariable = name_input, width = 20, bg = "#ff7048", justify = LEFT, fg = "white", highlightbackground = "black")
        nameEntry.config(font = ("DB HELVETHAICA X BD EXT", 20))
        nameEntry.config(borderwidth = 0, cursor = "ibeam")
        nameEntry.place(x = 50, y = 265)

            # Phone number Entry
        phoneNum_input = StringVar()
        phoneNumEntry = Entry(current_window, textvariable = phoneNum_input, width = 20, bg = "#ff7048", justify = LEFT, fg = "white", highlightbackground = "black")
        phoneNumEntry.config(font = ("DB HELVETHAICA X BD EXT", 20))
        phoneNumEntry.config(borderwidth = 0, cursor = "ibeam")
        phoneNumEntry.place(x = 50, y = 355)

            # Queue-Deleted Entry
        queueDelete_input = IntVar ()
        queueDeleteEntry = Entry(current_window, textvariable = queueDelete_input, width = 4, bg = "#ff7048", justify = LEFT, fg = "white", highlightbackground = "black")
        queueDeleteEntry.config(font = ("DB HELVETHAICA X BD EXT", 25))
        queueDeleteEntry.config(borderwidth = 0, cursor = "ibeam")
        queueDeleteEntry.place(x = 45, y = 513)

            # Command for Save Button
        def saveData () :
            try:
                toDatabase_name = name_input.get ()
                toDatabase_phoneNum = phoneNum_input.get()
                if toDatabase_name and toDatabase_phoneNum:
                    if (len(str(toDatabase_phoneNum)) == 10 and toDatabase_phoneNum[0] == "0") or (toDatabase_phoneNum == "-"):
                        data = (tableNO, toDatabase_name, toDatabase_phoneNum)
                        c.execute('INSERT INTO queueTable (tableNO,name,phoneNum) VALUES (?,?,?)' ,data )
                        messagebox.showinfo(title = "บันทึกข้อมูล", message = "บันทึกข้อมูลเสร็จสิ้น")
                        conn.commit()
                        reservationFunc ()
                    else:
                        messagebox.showerror("บันทึกข้อมูล","! เบอร์โทรศัพท์ไม่ถูกต้อง กรุณาลองใหม่ !")
                else :
                    messagebox.showerror(title = "บันทึกข้อมูล", message = "ไม่มีข้อมูลบันทึกหรือคุณใส่ข้อมูลไม่ครบ, กรุณาลองใหม่")
                    pass
            except:
                messagebox.showerror(title = "บันทึกข้อมูล", message = "ป้อนข้อมูลผิดพลาด, กรุณาลองใหม่")

            try:                              
                updateStatusTable1 ()
                updateStatusTable2 ()
                updateStatusTable3 () 
                updateStatusTable4 ()
                updateStatusTable5 ()                         
                updateStatusTable6 () 
                updateQueueRealtime (tableNO)
            except:
                pass                                    
            
        
            # Command for Delete Button
        
        def deleteData () :
            toDeleteDatabase_queue = queueDelete_input.get()
            if toDeleteDatabase_queue:
                confirm = messagebox.askquestion("ลบข้อมูล","ต้องการลบข้อมูลนี้หรือไม่ ?")
                if confirm == "yes" :
                    c.execute('''SELECT id,tableNO FROM queueTable''')
                    queueInTable = c.fetchall()
                    deleteQueue = 1
                    for x,y in queueInTable :
                        if int(tableNO) == int(y) :
                            if toDeleteDatabase_queue == deleteQueue:
                                # Delete From Queue
                                c.execute('''DELETE FROM queueTable WHERE id = %d''' %x)
                                conn.commit ()                       

                                c.execute("DELETE FROM sqlite_sequence WHERE name = 'queueTable'")
                                c.execute("INSERT INTO sqlite_sequence (name, seq) VALUES ('queueTable', 0)")

                                # Update ID
                                count = 1
                                c.execute("SELECT id FROM queueTABLE")
                                reID = c.fetchall()
                                for x in reID:
                                    old_id = x[0]
                                    data = (count,old_id)
                                    c.execute('''UPDATE queueTable SET id = ? WHERE id = ?''' ,data)
                                    conn.commit ()
                                    count += 1
                                        
                            deleteQueue += 1
                    messagebox.showinfo(title = "ลบข้อมูล", message = "ลบข้อมูลเสร็จสิ้น")
                    reservationFunc ()                
                else:
                    pass
            else:
                messagebox.showerror(title = "ลบข้อมูล", message = "ไม่สามารถลบข้อมูลได้") 

            try:
                updateStatusTable1 ()
                updateStatusTable2 ()
                updateStatusTable3 () 
                updateStatusTable4 ()
                updateStatusTable5 () 
                updateStatusTable6 ()   
                updateQueueRealtime (tableNO)
            except:
                pass
        
        # QUEUE TABLE #
        def queueInTable(tableNO):
            queueTable = Frame(current_window, height=350, width=620, bg="#e8dfab")
            queueTable.place(x=325, y=215)

            # Setting TABLE
            tree = ttk.Treeview(queueTable, columns=("Queue","Name","Phone"))
            tree.heading("Queue", text="ลำดับคิวที่")
            tree.heading("Name", text="ชื่อ")
            tree.heading("Phone", text="เบอร์โทรศัพท์")
            tree.column("Queue", anchor="center", width = 200)
            tree.column("Name", anchor="center", width = 200)
            tree.column("Phone", anchor="center", width = 200)
            tree.column("#0", width=0, stretch= NO)
            style = ttk.Style()
            style.configure("Treeview.Heading", font = ("DB HELVETHAICA X BD EXT", 25))
            
            c.execute('''SELECT id, tableNO, name, phoneNum FROM queueTable''')
            showData = c.fetchall()  
            count = 1
            for row in showData:
                if int(tableNO) == int(row[1]):
                    tree.insert("","end", values=(count,row[2],row[3]))
                    count += 1
            tree.pack()
            
        queueInTable(tableNO)
        
    # Save Button
        savePic = Image.open("save.png")
        savePicture = ImageTk.PhotoImage(savePic)
        saveBttn = Button(current_window, image = savePicture, 
                          justify = CENTER, activebackground = "#e8dfab", cursor = "hand2",
                          borderwidth = 0, bg = "#e8dfab", command = saveData)
        saveBttn.place(x = 105, y = 405)
        saveBttn.image = savePicture

            # Delete Button
        deletePic = Image.open("delete.png")
        deletePicture = ImageTk.PhotoImage(deletePic)
        deleteBttn = Button(current_window, image = deletePicture, 
                            justify = CENTER, activebackground = "#e8dfab", cursor = "hand2",
                            borderwidth = 0, bg = "#e8dfab", command = deleteData)
        deleteBttn.place(x = 145, y = 510)
        deleteBttn.image = deletePicture

            
    # Update Queue Real-time
    def updateQueueRealtime (table) :
        queueAllTable[table-1] = 0
        c.execute('''SELECT id,tableNO FROM queueTable''')
        allQueue = c.fetchall()
        for row in allQueue :
            if int(row[1]) == int(table) :
                queueAllTable[table-1] += 1
        # current_window.after(100, lambda: updateQueueRealtime(table))

    # Table 1
        # Table 1 Button!
    table1_import = Image.open("bttn_Table1.png")
    table1_import = table1_import.resize((int(table1_import.width*0.85),int(table1_import.height*0.85)))
    table1 = ImageTk.PhotoImage(table1_import)
    table1_Button = Button(current_window, image = table1, activebackground = "#e8dfab", cursor = "hand2",
                           justify = CENTER, borderwidth = 0, bg = "#e8dfab", command=lambda: reservationTable(1))
    table1_Button.place(x = 205, y = 115)
    table1_Button.image = table1

    table1_status = Label(current_window, text = "", justify = CENTER, bg = "#e8dfab")
        # Table 1 status!
    def updateStatusTable1 () :
        
        if queueAllTable[0] == 0 :
                table1_status.config(text = "ว่าง", font = ("DB HELVETHAICA X BD EXT",30), fg = "green")
                table1_status.place(x = 258, y = 280)
        elif queueAllTable[0] > 0 :
            table1_status.config(text = ("มี " + str(queueAllTable[0]) + " คิวก่อนหน้า"),font = ("DB HELVETHAICA X BD EXT",25), fg = "red")
            table1_status.place(x = 200, y = 284)
        current_window.after(100,updateStatusTable1)
    
    updateQueueRealtime (1)
    updateStatusTable1 ()

    # Table 2
        # Table 2 Button!
    table2_import = Image.open("bttn_Table2.png")
    table2_import = table2_import.resize((int(table2_import.width*0.85),int(table2_import.height*0.85)))
    table2 = ImageTk.PhotoImage(table2_import)
    table2_Button = Button(current_window, image = table2, activebackground = "#e8dfab", cursor = "hand2",
                           justify = CENTER, borderwidth = 0, bg = "#e8dfab", command=lambda: reservationTable(2))
    table2_Button.place(x = 410, y = 115)
    table2_Button.image = table2

    table2_status = Label(current_window, text = "", justify = CENTER, bg = "#e8dfab")
        # Table 2 status!
    def updateStatusTable2 () :
        
        if queueAllTable[1] == 0 :
            table2_status.config(text = "ว่าง", font = ("DB HELVETHAICA X BD EXT",30), fg = "green")
            table2_status.place(x = 462, y = 280)
        elif queueAllTable[1] > 0 :
            table2_status.config(text = ("มี " + str(queueAllTable[1]) + " คิวก่อนหน้า"),font = ("DB HELVETHAICA X BD EXT",25), fg = "red")
            table2_status.place(x = 410, y = 284)

        current_window.after(100,updateStatusTable2)
    
    updateQueueRealtime (2)
    updateStatusTable2 ()

    # Table 3

        # Table 3 Button!
    table3_import = Image.open("bttn_Table3.png")
    table3_import = table3_import.resize((int(table3_import.width*0.85),int(table3_import.height*0.85)))
    table3 = ImageTk.PhotoImage(table3_import)
    table3_button = Button(current_window, image = table3, activebackground = "#e8dfab", cursor = "hand2",
                           justify = CENTER, borderwidth = 0, bg = "#e8dfab", command=lambda: reservationTable(3))
    table3_button.place(x = 615, y = 115)
    table3_button.image = table3

    table3_status = Label(current_window, text = "", justify = CENTER, bg = "#e8dfab")
        # Table 3 status!
    def updateStatusTable3 () :
        
        if queueAllTable[2] == 0 :
            table3_status.config(text = "ว่าง", font = ("DB HELVETHAICA X BD EXT",30), fg = "green")
            table3_status.place(x = 666, y = 280)
        elif queueAllTable[2] > 0 :
            table3_status.config(text = ("มี " + str(queueAllTable[2]) + " คิวก่อนหน้า"),font = ("DB HELVETHAICA X BD EXT",25), fg = "red")
            table3_status.place(x = 620, y = 284)
        current_window.after(100,updateStatusTable3)
    
    updateQueueRealtime (3)
    updateStatusTable3 ()

    # Table 4

        # Table 4 Button!
    table4_import = Image.open("bttn_Table4.png")
    table4_import = table4_import.resize((int(table4_import.width*0.85),int(table4_import.height*0.85)))
    table4 = ImageTk.PhotoImage(table4_import)
    table4_button = Button(current_window, image = table4, activebackground = "#e8dfab", cursor = "hand2",
                           justify = CENTER, borderwidth = 0, bg = "#e8dfab", command=lambda: reservationTable(4))
    table4_button.place(x = 205, y = 350)
    table4_button.image = table4

    table4_status = Label(current_window, text = "", justify = CENTER, bg = "#e8dfab")
        # Table 4 status!
    def updateStatusTable4 () :
        
        if queueAllTable[3] == 0 :
            table4_status.config(text = "ว่าง", font = ("DB HELVETHAICA X BD EXT",30), fg = "green")
            table4_status.place(x = 258, y = 515)
        elif queueAllTable[3] > 0 :
            table4_status.config(text = ("มี " + str(queueAllTable[3]) + " คิวก่อนหน้า"),font = ("DB HELVETHAICA X BD EXT",25), fg = "red")
            table4_status.place(x = 200, y = 519)
        current_window.after(100,updateStatusTable4)
    
    updateQueueRealtime (4)
    updateStatusTable4 ()

    # Table 5
        # Table 5 Button!
    table5_import = Image.open("bttn_Table5.png")
    table5_import = table5_import.resize((int(table5_import.width*0.85),int(table5_import.height*0.85)))
    table5 = ImageTk.PhotoImage(table5_import)
    table5_Button = Button(current_window, image = table5, activebackground = "#e8dfab", cursor = "hand2",
                           justify = CENTER, borderwidth = 0, bg = "#e8dfab", command=lambda: reservationTable(5))
    table5_Button.place(x = 410, y = 350)
    table5_Button.image = table5

    table5_status = Label(current_window, text = "", justify = CENTER, bg = "#e8dfab")
        # Table 5 status!
    def updateStatusTable5 () :
        
        if queueAllTable[4] == 0 :
            table5_status.config(text = "ว่าง", font = ("DB HELVETHAICA X BD EXT",30), fg = "green")
            table5_status.place(x = 462, y = 515)
        elif queueAllTable[4] > 0 :
            table5_status.config(text = ("มี " + str(queueAllTable[4]) + " คิวก่อนหน้า"),font = ("DB HELVETHAICA X BD EXT",25), fg = "red")
            table5_status.place(x = 410, y = 519)
        current_window.after(100,updateStatusTable5)
    
    updateQueueRealtime (5)
    updateStatusTable5 ()
    
    # Table 6

        # Table 6 Button!
    table6_import = Image.open("bttn_Table6.png")
    table6_import = table6_import.resize((int(table6_import.width*0.85),int(table6_import.height*0.85)))
    table6 = ImageTk.PhotoImage(table6_import)
    table6_button = Button(current_window, image = table6, activebackground = "#e8dfab", cursor = "hand2",
                           justify = CENTER, borderwidth = 0, bg = "#e8dfab", command=lambda: reservationTable(6))
    table6_button.place(x = 615, y = 350)
    table6_button.image = table6

    table6_status = Label(current_window, text = "", justify = CENTER, bg = "#e8dfab")
        # Table 3 status!
    def updateStatusTable6 () :
        
        if queueAllTable[5] == 0 :
            table6_status.config(text = "ว่าง", font = ("DB HELVETHAICA X BD EXT",30), fg = "green")
            table6_status.place(x = 666, y = 515)
        elif queueAllTable[5] > 0 :
            table6_status.config(text = ("มี " + str(queueAllTable[5]) + " คิวก่อนหน้า"),font = ("DB HELVETHAICA X BD EXT",25), fg = "red")
            table6_status.place(x = 620, y = 519)
        current_window.after(100,updateStatusTable6)
    
    updateQueueRealtime (6)
    updateStatusTable6 ()

def orderFoodFunc ():
    global current_window
    if current_window:
        current_window.destroy()

    # Setting Window
    current_window = Tk ()
    current_window.title("Restaurant")
    current_window.geometry("1000x600+300+100")
    current_window.resizable(False,False)
    current_window.title("My restaurant") 

    # Background
    order_BG = Image.open("Order_BG.png")
    BG_order = ImageTk.PhotoImage(order_BG)
    BG = Label(current_window, image = BG_order)
    BG.pack()
    BG.image = BG_order

    # Go back button
    backPic = Image.open("backBttn.png")
    backBttn = ImageTk.PhotoImage(backPic)
    back_button = Button(current_window, image = backBttn, borderwidth = 0, activebackground = "#e8dfab", cursor = "hand2",
                         justify = CENTER, bg = "#e8dfab", command = staffMenu)
    back_button.config(borderwidth = 0)
    back_button.place(x = 68, y = 35)
    back_button.image = backBttn
    
    label = Label(current_window, text="Order food", justify = CENTER, font = 100 )
    label.pack()

    # Drop Down Table MENU 
    tableChooser = ttk.Combobox(current_window, values = ["1", "2", "3","4","5","6"], 
                                font = ("DB HELVETHAICA X BD EXT", 24), width = 5, justify = CENTER, cursor = "hand2" )
    tableChooser.place(x = 157, y = 147)

    # Menu ID Chooser Entry Box
    menuChoose_input = ttk.Combobox(current_window, values = list(range(1,12)), cursor = "ibeam",
                                    width = 8, justify = CENTER)
    menuChoose_input.config(font = ("DB HELVETHAICA X BD EXT", 20))
    menuChoose_input.place(x = 133, y = 327)

    # Amount Chooser Entry Box
    amount_input = StringVar()
    amount_entryBox = Entry(current_window, textvariable = amount_input, cursor = "ibeam",
                            width = 6, bg = "#e8dfab", justify = CENTER, fg = "#ff7048" )
    amount_entryBox.config(font = ("DB HELVETHAICA X BD EXT", 25))
    amount_entryBox.config(borderwidth = 0)
    amount_entryBox.place(x = 180, y = 386)
    
    # Setting Frame
    def chooseTable() :
        chooseTableFromComboBox = tableChooser.get()
        messagebox.showinfo(title = "เลือกโต๊ะ", message = ("เลือกโต๊ที่ " + str(chooseTableFromComboBox) + " แล้ว" ))
        ListUpdate(chooseTableFromComboBox)
        

    def ListUpdate (tableNO):

        def foodTableList (tableNO):
            orderList = Frame(current_window, height=800, width=620, bg="#e8dfab")
            orderList.place(x=440, y=130)
        
            # Setting TABLE
            tree = ttk.Treeview(orderList, columns=("MenuID","Menu","Amount","Price"))
            tree.heading("MenuID", text="ID")
            tree.heading("Menu", text="เมนู")
            tree.heading("Amount", text="จำนวน")
            tree.heading("Price", text="ราคา")
            tree.column("MenuID", anchor="center", width = 50)
            tree.column("Menu", anchor="center", width = 200)
            tree.column("Amount", anchor="center", width = 120)
            tree.column("Price", anchor="center", width = 120)
            tree.column("#0", width=0, stretch= NO)
            
                
            c.execute('''SELECT * FROM billTable''')
            showData = c.fetchall()  
            for row in showData:
                if int(tableNO) == int(row[1]):
                    tree.insert("","end", values=(row[2],row[3],row[5],row[4]))
            
            # Configure vertical scrollbar
            vsb = ttk.Scrollbar(orderList, orient="vertical", command=tree.yview)
            tree.configure(yscrollcommand=vsb.set)
            vsb.pack(fill="y", side="right")

            # ปรับ Text
            tree.configure(style="Custom.Treeview")
            custom_style = ttk.Style()
            custom_style.configure("Custom.Treeview.heading", font = ("DB HELVETHAICA X BD EXT", 25))
            custom_style.configure("Custom.Treeview", font = ("DB HELVETHAICA X BD EXT", 16), rowheight = 30)          
            tree.pack()
            
        tableNO_queue = []
        c.execute("SELECT * FROM queueTable")
        queueTableCollect =  c.fetchall()
        for x in queueTableCollect:
            tableNO_queue.append(x[1])

        if tableNO not in tableNO_queue:
            toReserve = messagebox.askquestion("คิวโต๊ะ","คุณยังไม่ได้เพิ่มคิวโต๊ะ, เข้าไปที่ 'หน้าคิวโต๊ะ' ก่อนหรือไม่?")
            if toReserve == "yes":
                reservationFunc ()
            else:
                messagebox.showerror("สั่งอาหาร","! ไม่สามารถสั่งอาหารได้, กรุณาเพิ่มคิวโต๊ะก่อน !")
        else:
            foodTableList (tableNO)


    def addOrderMenuTable () :
        tableNO_import = tableChooser.get()
        menu_import = menuChoose_input.get()
        amount_import = amount_input.get()

        def confirmAddOrder () :
            if tableNO_import:
                if menu_import and amount_import:
                    confirm = messagebox.askquestion(title  = "ยืนยันการเพิ่ม Order", message = "ต้องการเพิ่มเมนูนี้ ใช่หรือไม่?")
                    if confirm == "yes" :
                        
                        # ค้นหาข้อมูลจากรายการอาหาร foodLists
                        c.execute('''SELECT * FROM foodLists''')
                        allFoodLists = c.fetchall()
                        for idFoodList,food,priceList in allFoodLists:
                            if int(menu_import) == int(idFoodList):
                                foodName = food
                                priceAll = int(priceList)

                        # ถ้ามีข้อมูลใน BillTable อยู่แล้ว
                        c.execute('''SELECT id,tableNO,idFood,price,amount FROM billTable''')  
                        bill = c.fetchall()
                        idListExist = []
                        amountSum = 0
                        for id,table,id_food,price,amount in bill:
                            if int(table) == int(tableNO_import):
                                if int(menu_import) == int(id_food):
                                    amountSum = int(amount) + int(amount_import)
                                    priceDefault = int(price) / int(amount) 
                                    priceUpdate = int(amountSum) * int(priceDefault)
                                    c.execute('''UPDATE billTable SET amount = ?,price = ? WHERE id = ?''' ,(int(amountSum),int(priceUpdate),int(id),))
                                    conn.commit()
                                idListExist.append(id_food)
                                

                        # ในกรณีที่ import เข้า ไม่มี id ตรงกับ ใน Bill
                        if int(menu_import) not in idListExist:  
                            try :      
                                priceSum = int(priceAll) * int(amount_import)
                                data = (tableNO_import,menu_import,foodName,priceSum,amount_import)
                                c.execute('INSERT INTO billTable (tableNO,idFood,food,price,amount) VALUES (?,?,?,?,?)' ,data )
                                conn.commit ()
                            except :
                                messagebox.showerror("! สั่งอาหาร","คุณกรอกไม่ตรงกับที่มีในเมนู, กรุณากรอกใหม่ !")
                
                    else:
                        pass
                else:
                    messagebox.showerror(title = "กรอกข้อมูล", message = "กรอกข้อมูลไม่ครบถ้วน, กรุณากรอกใหม่")

                ListUpdate(tableNO_import)
                        
            else:
                messagebox.showerror(title = "เพิ่มข้อมูล", message = "! กรุณากรอกเลขโต๊ะให้เรียบร้อย !")
            
            # ลบข้อมูลหลังจากดำเนินการเสร็จสิ้น
            menuChoose_input.set("-")
            amount_entryBox.delete(0,END)
        
        tableNO_queue = []
        c.execute("SELECT * FROM queueTable")
        queueTableCollect =  c.fetchall()
        for x in queueTableCollect:
            tableNO_queue.append(x[1])

        if tableNO_import and tableNO_import not in tableNO_queue:
            toReserve = messagebox.askquestion("คิวโต๊ะ","คุณยังไม่ได้เพิ่มคิวโต๊ะ, เข้าไปที่ 'หน้าคิวโต๊ะ' ก่อนหรือไม่?")
            if toReserve == "yes":
                reservationFunc ()
            else:
                messagebox.showerror("สั่งอาหาร","! ไม่สามารถสั่งอาหารได้, กรุณาเพิ่มคิวโต๊ะก่อน !")
        elif not tableNO_import:
            messagebox.showerror("สั่งอาหาร","! กรุณากรอกเลขโต๊ะก่อนสั่งอาหาร !")
        else:
            confirmAddOrder ()

    def deleteOrderMenuTable () :
        tableNO_import = tableChooser.get()
        menu_import = menuChoose_input.get()
        amount_import = amount_input.get()

        def confirmDeleteOrder () :
            if tableNO_import:
                if menu_import and amount_import:
                    confirm = messagebox.askquestion(title  = "ยืนยันการลบ Order", message = "ต้องการลบตามคิวที่ ใช่หรือไม่?")
                    if confirm == "yes" :
                        c.execute('''SELECT * FROM billTable''')
                        bill = c.fetchall()
                        for id,tableNO,idFood,food,price,amount in bill:
                            # เมื่อเลขโต๊ะตรงกับที่ต้องการให้ลบ
                            if int(tableNO) == int(tableNO_import):
                                # เมื่อไอดีเมนูตรงกันกับที่ต้องการให้ลบ
                                if int(idFood) == int(menu_import):
                                        # เมื่อจำนวนคงเหลือมากกว่า 0 ให้ update ข้อมูล
                                    if (int(amount) - int(amount_import) > 0):
                                        priceDefault = int(price) / int(amount)
                                        balanceAmount = int(amount) - int(amount_import)
                                        priceUpdate = int(balanceAmount) * int(priceDefault)
                                        c.execute('''UPDATE billTable SET amount = ?,price = ? WHERE id = ?''' ,(balanceAmount,priceUpdate,int(id),))
                                        conn.commit()
                                        messagebox.showinfo(title = "ลบข้อมูล", message = "ลบข้อมูลเสร็จสิ้น")
                                    elif (int(amount) - int(amount_import) == 0):
                                            # Delete ข้อมูลทิ้งตามตำแหน่ง ID
                                        c.execute('''DELETE FROM billTable WHERE id = ?''' ,(int(id),))   
                                        conn.commit()
                                        messagebox.showinfo(title = "ลบข้อมูล", message = "ลบข้อมูลเสร็จสิ้น")
                                    else:
                                        messagebox.showerror(title = "ลบข้อมูล", message = "! คุณกรอกลบเกินจำนวนที่มีอยู่ กรุณาลองใหม่ !")
                                    c.execute("DELETE FROM sqlite_sequence WHERE name = 'billTable'")
                                    c.execute("INSERT INTO sqlite_sequence (name, seq) VALUES ('billTable', 0)")
                                    conn.commit()
                                    # Update ID
                                    count = 1
                                    c.execute("SELECT id FROM billTable")
                                    reID = c.fetchall()
                                    for x in reID:
                                        old_id = int(x[0])
                                        data = (count,old_id)
                                        c.execute('''UPDATE billTable SET id = ? WHERE id = ?''' ,data)
                                        count += 1
                                        conn.commit()
                        
                    else:
                        pass
                else:
                    messagebox.showerror(title = "กรอกข้อมูล", message = "กรอกข้อมูลไม่ครบถ้วน, กรุณากรอกใหม่")
            else:
                messagebox.showerror(title = "กรอกข้อมูล", message = "!กรุณาเลือกเลขโต๊ะให้เรียบร้อย!")

            ListUpdate(tableNO_import)
            menuChoose_input.set("-")
            amount_entryBox.delete(0,END)
        
        tableNO_queue = []
        c.execute("SELECT * FROM queueTable")
        queueTableCollect =  c.fetchall()
        for x in queueTableCollect:
            tableNO_queue.append(x[1])

        if tableNO_import not in tableNO_queue:
            toReserve = messagebox.askquestion("คิวโต๊ะ","คุณยังไม่ได้เพิ่มคิวโต๊ะ, เข้าไปที่ 'หน้าคิวโต๊ะ' ก่อนหรือไม่?")
            if toReserve == "yes":
                reservationFunc ()
            else:
                messagebox.showerror("สั่งอาหาร","! ไม่สามารถสั่งอาหารได้, กรุณาเพิ่มคิวโต๊ะก่อน !")
        elif not tableNO_import:
            messagebox.showerror("สั่งอาหาร","! กรุณากรอกเลขโต๊ะก่อนสั่งอาหาร !")
        else:
            confirmDeleteOrder ()


    def openCheckBill ():
        tableNO = tableChooser.get()
        if tableNO:
            global current_window
            if current_window:
                current_window.destroy()
             # Setting Window
            current_window = Tk ()
            current_window.title("Restaurant")
            current_window.geometry("1000x600+300+100")
            current_window.resizable(False,False)
            current_window.title("My restaurant") 

            # Background
            bill_pic = Image.open("bill_BG.png")
            picBill = ImageTk.PhotoImage(bill_pic)
            BG = Label(current_window, image = picBill)
            BG.pack()
            BG.image = picBill

            # Go back button
            backPic = Image.open("backBttn.png")
            backPic = backPic.resize((int(backPic.width*0.7),int(backPic.height*0.7)))
            backBttn = ImageTk.PhotoImage(backPic)
            back_button = Button(current_window, image = backBttn, activebackground = "#e8dfab", cursor = "hand2",
                                 borderwidth = 0, justify = CENTER, bg = "#e8dfab", command = orderFoodFunc)
            back_button.config(borderwidth = 0)
            back_button.place(x = 800, y = 33)
            back_button.image = backBttn

            # Frame for contain Table
            orderList = Frame(current_window, height=800, width=620, bg="#e8dfab")
            orderList.place(x=100, y=145)

            # Setting TABLE
            tree = ttk.Treeview(orderList, columns=("Menu","Amount","Price"))
            tree.heading("Menu", text="เมนู")
            tree.heading("Amount", text="จำนวน")
            tree.heading("Price", text="ราคา")
            tree.column("Menu", anchor="center", width = 200)
            tree.column("Amount", anchor="center", width = 120)
            tree.column("Price", anchor="center", width = 120)
            tree.column("#0", width=0, stretch= NO)
                
            c.execute('''SELECT * FROM billTable''')
            showData = c.fetchall()  
            for row in showData:
                if int(tableNO) == int(row[1]):
                    tree.insert("","end", values=(row[3],row[5],row[4]))
            
            # เปลี่ยนสี BACKGROUND
            tree.configure(style="Custom.Treeview")
            custom_style = ttk.Style()
            custom_style.configure("Custom.Treeview.heading", font = ("DB HELVETHAICA X BD EXT", 35))
            custom_style.configure("Custom.Treeview", font = ("DB HELVETHAICA X BD EXT", 20), rowheight = 30) 
            tree.pack()

            # CLOCK
            day = strftime("%d")
            month = strftime("%B")
            year = strftime("%Y")
            date = str(day + "/" + month + "/" + year)
            hour = strftime("%H")
            minute = strftime("%M")
            hm = str(hour + ":" + minute)
            Label(current_window, text = date, font = ("Bebas Neue Regular", 20), bg = "#e8dfab", fg = "#307d9b").place(x = 280, y = 72)
            
            # ราคาทั้งหมด
            c.execute("SELECT tableNO,price FROM billTable")
            payAll = c.fetchall()
            pay = float()
            for i in payAll:
                if int(i[0]) == int(tableNO):
                    pay = pay + int(i[1])
            sum = Label(current_window, text = ("รวม : " + "%.2f" %pay + " บาท"), bg = "#e8dfab")
            sum.place(x = 630, y = 142)
            sum.config(font = ("DB HELVETHAICA X BD EXT", 35))

            # Member Entry
            member_import = StringVar()
            member_entryBox = Entry(current_window, textvariable = member_import, 
                                    font = ("DB HELVETHAICA X BD EXT", 20), bg = "#e8dfab", 
                                    fg = "#3aa473",width = 12, borderwidth = 0)
            member_entryBox.place(x = 85, y = 517)

                # ใช้ส่วนลดสมาชิกร้านค้า
            def memberDiscount(pay):
                memberForDiscount = member_import.get()

                # เก็บค่าราคาทั้งหมด
                c.execute("SELECT tableNO,price FROM billTable")
                payAll = c.fetchall()
                for i in payAll:
                    if int(i[1]) == int(tableNO):
                        pay = pay + int(i[4])

                # ถ้ามีเลขสมาชิก
                if memberForDiscount:
                    c.execute("SELECT * FROM customerMember")
                    chooseMember = c.fetchall()
                    memberList = []
                    for data in chooseMember:
                        memberList.append(str(data[2]))

                    if str(memberForDiscount) in memberList:
                        pay = pay * 95 / 100
                        sumNew = Label(current_window, text = ("ราคาหลังหักส่วนลด :\n" + "%.2f" %(float(pay)) + " บาท"), bg = "#e8dfab",
                                        fg = "#3aa473",justify = LEFT)
                        sumNew.place(x = 630, y = 195)
                        sumNew.config(font = ("DB HELVETHAICA X BD EXT", 30))
                        messagebox.showinfo(title = "ใช้ส่วนลดสมาชิก", message = "ใช้ส่วนลดสมาชิกสำเร็จ")
                    elif str(memberForDiscount) not in memberList:
                
                        messagebox.showerror(title = "ใช้ส่วนลดสมาชิก", message = "! เลขสมาชิกไม่ถูกต้อง กรุณาลองอีกครั้ง !")
                        member_entryBox.delete(0,END)        
                else:
                    messagebox.showinfo(title = "ใช้ส่วนลดสมาชิก", message = "! กรุณากรอกเลขสมาชิกก่อน, โปรดลองอีกครั้ง !")
            
            # ปุ่มยืนยันการใส่เลขที่สมาชิก
            confirmMember = Image.open("Order_0memberConfirm.png")
            memberConfirm = ImageTk.PhotoImage(confirmMember)
            confirmMember_bttn = Button(current_window, bg = "#e8dfab", activebackground = "#e8dfab", cursor = "hand2",
                                        borderwidth = 0,image = memberConfirm, command = lambda: memberDiscount(pay))
            confirmMember_bttn.place(x = 282, y = 505)
            confirmMember_bttn.image = memberConfirm

            def showQRcode(pay) :
                try:
                    memberForDiscount = member_import.get()
                    if memberForDiscount:
                        c.execute("SELECT * FROM customerMember")
                        chooseMember = c.fetchall()
                        for data in chooseMember:
                            if str(data[2]) == str(memberForDiscount):
                                pay = pay * 95 / 100
                            else:
                                pass          
                    # URL of the QR code image
                    text = "https://promptpay.io/0928258383/" + str(pay) + ".png"
                    image_url = text

                    # Send a request to download the image
                    response = requests.get(image_url)

                    # Check if the request was successful (HTTP status code 200)
                    if response.status_code == 200:
                        # Open the image using PIL
                        image = Image.open(BytesIO(response.content))
                        
                        # Convert the image to grayscale if it's not already
                        if image.mode != 'L':
                            image = image.convert('L')
                        
                        # Convert the PIL image to a NumPy array
                        img_np = np.array(image)

                        # Initialize the QRCode detector
                        qr_decoder = cv2.QRCodeDetector()

                        # Detect and decode the QR code
                        val, pts, qr_code = qr_decoder.detectAndDecode(img_np)

                        # Print the decoded value from the QR code
                        print("Decoded value from the QR code:", val)

                        # Display the image in a Tkinter window
                        image = image.resize((int(image.width * 0.75), int(image.height * 0.75)))
                        img_tk = ImageTk.PhotoImage(image)
                        label = Label(current_window, image=img_tk)
                        label.image = img_tk  # Keep a reference to avoid garbage collection
                        label.place(x = 694, y = 300)
                    else:
                        print("Failed to download the image. HTTP status code:", response.status_code)

                        # Payment Successful Button
                    confirmPayPic = Image.open("Order_0paymentSuccessBttn.png")
                    picConfirmPay = ImageTk.PhotoImage(confirmPayPic)
                    confirmPaymentBttn = Button(current_window, activebackground = "#e8dfab", cursor = "hand2",
                                                image = picConfirmPay, bg = "#e8dfab", borderwidth = 0, command = lambda: confirm(pay))
                    confirmPaymentBttn.place(x = 653, y = 480)
                    confirmPaymentBttn.image = picConfirmPay
                except:
                    messagebox.showerror("สแกนจ่าย","! สแกนจ่ายไม่สำเร็จ, ไม่สามารถเชื่อมต่อได้ กรุณาเชื่อมต่ออินเทอร์เน็ต !")
                    pass

            def confirm (pay) :
                checkBillConfirm = messagebox.askquestion(title = "คิดเงิน", message = "ยืนยันการจ่ายเงินเรียบร้อยแล้วหรือไม่?")
                if checkBillConfirm == "yes" :

                    # ลบคิวที่ 1 ที่ถูกจองไว้
                    c.execute("SELECT id,tableNO FROM queueTABLE")
                    findFirstQueue = c.fetchall()
                    for row in  findFirstQueue:
                        if int(row[1]) == int(tableNO):
                            int(row[0])
                            c.execute('''DELETE FROM queueTable WHERE id = ?''',(int(row[0]),))                     
                        c.execute("DELETE FROM sqlite_sequence WHERE name = 'queueTable'")
                        c.execute("INSERT INTO sqlite_sequence (name, seq) VALUES ('queueTable', 0)")
                        conn.commit()

                    # Update ID in QueueTable
                    count = 1
                    c.execute("SELECT * FROM queueTABLE")
                    reID = c.fetchall()
                    for x in reID:
                        old_id = x[0]
                        c.execute('''UPDATE queueTable SET id = ? WHERE id = ?''' ,(int(count),int(old_id),))
                        count += 1
                        conn.commit ()

                    # เพิ่มข้อมูลเข้าเข้า historyBill
                    c.execute("SELECT * FROM billTable")
                    bill = c.fetchall() 

                    # Insert ข้อมูลเข้า
                    for i in bill:
                        if (int(tableNO)) == int(i[1]) :   
                            c.execute("INSERT INTO historyBill (dmy,day,month,year,hm,food,amount,price,summary) VALUES (?,?,?,?,?,?,?,?,?)"
                                      ,(str(date),int(day),str(month),int(year),str(hm),str(i[3]),int(i[5]),int(i[4]),int(pay),))
                            conn.commit()


                    # Clear bill in billTable
                    c.execute("SELECT id,tableNO FROM billTable")
                    clearBill = c.fetchall()
                    for a,b in clearBill:
                        if int(b) == int(tableNO):
                            c.execute('''DELETE FROM billTable WHERE id = ?''',(int(a),))
                    c.execute("DELETE FROM sqlite_sequence WHERE name = 'billTable'")
                    c.execute("INSERT INTO sqlite_sequence (name, seq) VALUES ('billTable', 0)")
                    conn.commit()

                    # Update ID in billTable
                    c.execute("SELECT * FROM billTable")
                    reID2 = c.fetchall ()
                    count = 1
                    for d in reID2:
                        old_id = d[0]
                        data = (count,old_id)
                        c.execute('''UPDATE billTable SET id = ? WHERE id = ?''' ,(int(count),int(old_id),))
                        count += 1
                        conn.commit()
                    messagebox.showinfo(title = "คิดเงิน", message = "คิดเงินเสร็จสิ้น")
                    orderFoodFunc ()


            # Show QR CODE Button
            checkBillPic = Image.open("Order_0checkBillBttn.png")
            picCheckBill = ImageTk.PhotoImage(checkBillPic)
            checkBillBttn = Button(current_window, image =picCheckBill, activebackground = "#e8dfab", cursor = "hand2",
                                   bg = "#e8dfab", borderwidth = 0, command = lambda: showQRcode(pay))
            checkBillBttn.place(x = 385, y = 500)
            checkBillBttn.image = picCheckBill

            
        else:
            messagebox.showerror(title = "เช็คบิล", message = "!เข้าหน้าไม่สำเร็จ, กรุณาเลือกเลขโต๊ะที่ต้องการก่อนให้เรียบร้อย!")
            pass

    # Choose Table Confirm button
    chooseTablePic = Image.open("Order_0chooseTable.png")
    picChooseTable = ImageTk.PhotoImage(chooseTablePic)
    chooseTableBttn = Button(current_window, image =picChooseTable, activebackground = "#e8dfab", cursor = "hand2",
                             bg = "#e8dfab", borderwidth = 0, command = chooseTable)
    chooseTableBttn.place(x = 292, y = 136)
    chooseTableBttn.image = picChooseTable

    # Check Bill Menu Button
    checkBillPic = Image.open("Order_0checkBillBttn.png")
    picCheckBill = ImageTk.PhotoImage(checkBillPic)
    checkBillBttn = Button(current_window, image =picCheckBill, activebackground = "#e8dfab", cursor = "hand2",
                           bg = "#e8dfab", borderwidth = 0, command = openCheckBill)
    checkBillBttn.place(x = 110, y = 500)
    checkBillBttn.image = picCheckBill

    # See Food-list Menu Button
    seeFoodListPic = Image.open("Order_0foodListMenu.png")
    picSeeFoodList = ImageTk.PhotoImage(seeFoodListPic)
    seeFoodListBttn = Button(current_window, image =picSeeFoodList, activebackground = "#e8dfab", cursor = "hand2",
                             bg = "#e8dfab", borderwidth = 0, command = foodListShow)
    seeFoodListBttn.place(x = 200, y = 250)
    seeFoodListBttn.image = picSeeFoodList

    # Choose menu and ADD Button
    chooseMenuPic = Image.open("Order_0chooseMenu.png")
    picChooseMenu = ImageTk.PhotoImage(chooseMenuPic)
    chooseMenuBttn = Button(current_window, image =picChooseMenu, activebackground = "#e8dfab", cursor = "hand2",
                            bg = "#e8dfab", borderwidth = 0, command = addOrderMenuTable)
    chooseMenuBttn.place(x = 110, y = 435)
    chooseMenuBttn.image = picChooseMenu

    # Choose menu and DELETE Button
    deleteMenuPic = Image.open("Order_0deleteMenu.png")
    picDeleteMenu = ImageTk.PhotoImage(deleteMenuPic)
    deleteBttn = Button(current_window, image =picDeleteMenu, activebackground = "#e8dfab", cursor = "hand2",
                        bg = "#e8dfab", borderwidth = 0, command = deleteOrderMenuTable)
    deleteBttn.place(x = 225, y = 436)
    deleteBttn.image = picDeleteMenu

def memberRegister ():
    global current_window
    if current_window:
        current_window.destroy()

    # Setting Window
    current_window = Tk ()
    current_window.title("Restaurant")
    current_window.geometry("1000x600+300+100")
    current_window.resizable(False,False)
    current_window.title("My restaurant") 

    # Background
    registerBG = Image.open("register_bg.png")
    BG_register = ImageTk.PhotoImage(registerBG)
    BG = Label(current_window, image = BG_register)
    BG.pack()
    BG.image = BG_register

    # To home button
    homePic = Image.open("homeBttn.png")
    homePic = homePic.resize((int(homePic.width * 1.1), int(homePic.height * 1.1)))
    homeBttn = ImageTk.PhotoImage(homePic)
    home_Button = Button(current_window, image = homeBttn, activebackground = "#e8dfab", cursor = "hand2",
                         borderwidth = 0, justify = CENTER, bg = "#e8dfab", command = staffMenu)
    home_Button.config(borderwidth = 0)
    home_Button.place(x = 68, y = 35)
    home_Button.image = homeBttn

    # Entry
        # Username
    username = StringVar()
    username_entry = Entry(current_window, textvariable = username, font = ("DB HELVETHAICAMON X BD", 25), 
                           bg = "#fff9d7", fg = "#ff7048", borderwidth = 0)
    username_entry.place(x = 320, y = 240) 
        # Phone Number
    phoneNum = StringVar()
    phoneNum_entry = Entry(current_window, textvariable = phoneNum, font = ("DB HELVETHAICAMON X BD", 25), 
                           bg = "#fff9d7", fg = "#ff7048", borderwidth = 0)
    phoneNum_entry.place(x = 320, y = 335) 
        # Email
    email = StringVar()
    email_entry = Entry(current_window, textvariable = email, font = ("DB HELVETHAICAMON X BD", 25), 
                           bg = "#fff9d7", fg = "#ff7048", borderwidth = 0, width = 25)
    email_entry.place(x = 320, y = 429) 
    
    # Check phoneNum exist
    def recheckData ():
        user_import = username.get()
        phoneNum_import = phoneNum.get()
        email_import = email.get()
        phoneNumExist = []
        if user_import and phoneNum_import and ".com" in email_import:
            if len(str(phoneNum_import)) == 10 and phoneNum_import[0] == "0":
                c.execute('''SELECT * FROM customerMember''')
                customerMemberExist = c.fetchall()
                for listMember in customerMemberExist:
                    if str(listMember[2]) == str(phoneNum_import):
                        messagebox.showerror(title = "ลงทะเบียนสมัครสมาชิก", message = "! มีเบอร์โทรศัพท์ซํ้ากัน,\nกรุณาเลือกเบอร์โทรศัพท์อื่น และป้อนใหม่อีกครั้ง !")
                    phoneNumExist.append(str(listMember[2]))
                if phoneNum_import not in phoneNumExist:
                    otpSenderPage ()

            else:
                messagebox.showerror("สมัครสมาชิก","! กรุณากรอกเบอร์โทรศัพท์ให้ถูกต้อง !")

        else:
            messagebox.showerror(title = "ลงทะเบียนสมัครสมาชิก", message = "! กรุณากรอก username เบอร์โทรศัพท์ให้ครบถ้วน \nและกรอกอีเมลให้ถูกต้อง!")

    # OTP send Page
    def otpSenderPage ():
        get_username = username.get()
        get_phoneNum = phoneNum.get()
        get_email = email.get()

        global current_window
        if current_window:
            current_window.destroy()
        
        # Setting Window
        current_window = Tk ()
        current_window.title("Restaurant")
        current_window.geometry("1000x600+300+100")
        current_window.resizable(False,False)
        current_window.title("My restaurant")

        # Background
        registerOTP_BG = Image.open("registerOTP_bg.png")
        BG_otp = ImageTk.PhotoImage(registerOTP_BG)
        BG = Label(current_window, image = BG_otp)
        BG.pack()
        BG.image = BG_otp

        # Go back button
        backPic = Image.open("backBttn.png")
        backBttn = ImageTk.PhotoImage(backPic)
        back_button = Button(current_window, image = backBttn, activebackground = "#e8dfab", cursor = "hand2",
                             borderwidth = 0, justify = CENTER, bg = "#e8dfab", command = memberRegister)
        back_button.config(borderwidth = 0)
        back_button.place(x = 68, y = 35)
        back_button.image = backBttn

        # OTP Confirm entry
        otpConfirmInput= StringVar()
        otp_entry = Entry(current_window, textvariable = otpConfirmInput, font = ("DB HELVETHAICAMON X BD", 25), 
                            justify = CENTER, bg = "#fff9d7", fg = "#ff7048", borderwidth = 0, width = 10)
        otp_entry.place(x = 435, y = 379) 

         # OTP Check
        def otpConfirmFunc ():
            if otp:
                get_otp = otp_entry.get ()
                if str(otp) == str(get_otp):
                    messagebox.showinfo("ยืนยันข้อมูล","OTP ถูกต้อง, ยืนยันเสร็จสิ้น")
                    confirmDataPage ()
                    
                else:
                    messagebox.showerror("ยืนยันข้อมูล","! OTP ไม่ถูกต้อง, กรุณาใส่รหัส OTP ใหม่อีกครั้ง !")
                    otp_entry.delete(0,END)

        # ปุ่มบันทึก
        otpConfirmPic = Image.open("Order_0memberConfirm.png")
        pic_otpConfirm = ImageTk.PhotoImage(otpConfirmPic)
        confirmOTP_bttn = Button(current_window, image = pic_otpConfirm, borderwidth = 0, justify = CENTER, bg = "#fff9d7", command = otpConfirmFunc)
        confirmOTP_bttn.config(borderwidth = 0)
        confirmOTP_bttn.place(x = 462, y = 439)
        confirmOTP_bttn.image = pic_otpConfirm
        
        # Function
        def send_otp_email(receiver_email):
            global otp
            sender_email = 'phurin2003@gmail.com'  # Your Gmail email
            sender_password = 'dgvgmraofnanbryx'  # Your Gmail password

            def generate_otp(length=6):
                characters = string.digits
                otp = ''.join(random.choice(characters) for _ in range(length))
                return otp

            otp = generate_otp()

            subject = 'OTP จากร้านค้าเบอร์เกอร์'
            body = f'รายละเอียดสมาชิก\n\nUsername: {get_username}\nเบอร์โทรศัพท์: {get_phoneNum}\n\nOTP ของคุณคือ: {otp}\nกรุณาอย่าให้รหัสนี้กับผู้อื่น\n'

            message = MIMEMultipart()
            message['From'] = "ร้านขายเบอร์เกอร์ของฉัน"
            message['To'] = receiver_email
            message['Subject'] = subject

            message.attach(MIMEText(body, 'plain'))

            try:
                with smtplib.SMTP('smtp.gmail.com', 587) as server:
                    server.starttls()
                    server.login(sender_email, sender_password)
                    server.sendmail(sender_email, receiver_email, message.as_string())
            except smtplib.SMTPAuthenticationError:
                messagebox.showerror("ส่ง OTP","! ส่ง OTP ไม่สำเร็จ, กรุณาตรวจสอบอีกครั้ง !")
                memberRegister ()
            except Exception as e:
                messagebox.showerror("ส่ง OTP","! Failed to send OTP via email: %s !" %receiver_email)
                memberRegister ()

        send_otp_email(str(get_email))
        
    # Member Data Confirm Page
    def confirmDataPage ():
        global current_window
        if current_window:
            current_window.destroy()

        # Define Value
        get_username = username.get()
        get_phoneNum = phoneNum.get()
        get_email = email.get()

        # Setting Window
        current_window = Tk ()
        current_window.title("Restaurant")
        current_window.geometry("1000x600+300+100")
        current_window.resizable(False,False)
        current_window.title("My restaurant")

        # Background
        confirm_BG = Image.open("registerConfirm_bg.png")
        BG_confirm = ImageTk.PhotoImage(confirm_BG)
        BG = Label(current_window, image = BG_confirm)
        BG.pack()
        BG.image = BG_confirm

        # Show DATA
        username_show = Label(current_window, text = get_username, font = ("DB HELVETHAICAMON X BD", 25),
                              bg = "#fff9d7", fg = "#ff7048", borderwidth = 0)
        username_show.place(x = 320, y = 240) 
        phoneNum_show = Label(current_window, text = get_phoneNum, font = ("DB HELVETHAICAMON X BD", 25),
                              bg = "#fff9d7", fg = "#ff7048", borderwidth = 0)
        phoneNum_show.place(x = 320, y = 335) 
        email_show = Label(current_window, text = get_email, font = ("DB HELVETHAICAMON X BD", 25),
                              bg = "#fff9d7", fg = "#ff7048", borderwidth = 0)
        email_show.place(x = 320, y = 430) 

        # Go back button
        backPic = Image.open("backBttn.png")
        backBttn = ImageTk.PhotoImage(backPic)
        back_button = Button(current_window, image = backBttn, activebackground = "#e8dfab", cursor = "hand2",
                             borderwidth = 0, justify = CENTER, bg = "#e8dfab", command = memberRegister)
        back_button.config(borderwidth = 0)
        back_button.place(x = 68, y = 35)
        back_button.image = backBttn

        # ปุ่มบันทึก
        lastConfirmPic = Image.open("register_button.png")
        picLastConfirm = ImageTk.PhotoImage(lastConfirmPic)
        lastConfirm_bttn = Button(current_window, image = picLastConfirm, activebackground = "#fff9d7", cursor = "hand2",
                                  borderwidth = 0, justify = CENTER, bg = "#fff9d7", command = submitRegister)
        lastConfirm_bttn.config(borderwidth = 0)
        lastConfirm_bttn.place(x = 360, y = 485)
        lastConfirm_bttn.image = picLastConfirm

    # ดำเนินการบันทึก
    def submitRegister() :
        user_import = username.get()
        phoneNum_import = phoneNum.get()
        email_import = email.get()
        phoneNumExist = []
        if user_import and phoneNum_import:
            if len(str(phoneNum_import)) == 10 and phoneNum_import[0] == "0":
                c.execute('''SELECT * FROM customerMember''')
                customerMemberExist = c.fetchall()
                for listMember in customerMemberExist:
                    if str(listMember[2]) == str(phoneNum_import):
                        messagebox.showerror(title = "ลงทะเบียนสมัครสมาชิก", message = "! มีเบอร์โทรศัพท์ซํ้ากัน,\nกรุณาเลือกเบอร์โทรศัพท์อื่น และป้อนใหม่อีกครั้ง !")
                    phoneNumExist.append(str(listMember[2]))
                if phoneNum_import not in phoneNumExist:
                    data = (str(user_import),str(phoneNum_import),str(email_import))
                    c.execute('INSERT INTO customerMember (name,phoneNum,email) VALUES (?,?,?)' ,data )
                    messagebox.showinfo(title = "ลงทะเบียนสมัครสมาชิก", message = "ลงทะเบียนเสร็จสิ้น")
                    conn.commit()
                    memberRegister ()
            else:
                messagebox.showerror("สมัครสมาชิก","! กรุณากรอกเบอร์โทรศัพท์ให้ถูกต้อง !")

        else:
            messagebox.showerror(title = "ลงทะเบียนสมัครสมาชิก", message = "! กรุณากรอก username และเบอร์โทรศัพท์ให้ครบถ้วน !")

    # ปุ่มบันทึก
    registerConfirmPic = Image.open("register_button.png")
    registerConfirmBttn = ImageTk.PhotoImage(registerConfirmPic)
    register_button = Button(current_window, image = registerConfirmBttn, activebackground = "#fff9d7", cursor = "hand2",
                             borderwidth = 0, justify = CENTER, bg = "#fff9d7", command = recheckData)
    register_button.config(borderwidth = 0)
    register_button.place(x = 360, y = 485)
    register_button.image = registerConfirmBttn

def incomeStatistic ():
    global current_window
    if current_window:
        current_window.destroy()

    # Setting Window
    current_window = Tk ()
    current_window.title("Restaurant")
    current_window.geometry("1000x600+300+100")
    current_window.resizable(False,False)
    current_window.title("My restaurant") 

    # Background
    statsBG = Image.open("IncomeStats_BG.png")
    BG_stats = ImageTk.PhotoImage(statsBG)
    BG = Label(current_window, image = BG_stats)
    BG.pack()
    BG.image = BG_stats
    
     # Go back button
    backPic = Image.open("backBttn.png")
    backBttn = ImageTk.PhotoImage(backPic)
    back_button = Button(current_window, image = backBttn, activebackground = "#e8dfab", cursor = "hand2",
                         borderwidth = 0, justify = CENTER, bg = "#e8dfab", command = staffMenu)
    back_button.config(borderwidth = 0)
    back_button.place(x = 68, y = 35)
    back_button.image = backBttn

    # To day statistics PAGE
    def toDayPage () :
        global current_window
        if current_window:
            current_window.destroy()
    
        # Setting Window
        current_window = Tk ()
        current_window.title("Restaurant")
        current_window.geometry("1000x600+300+100")
        current_window.resizable(False,False)
        current_window.title("My restaurant")

        # Background
        dayStatsBG = Image.open("IncomeStats_dayBG.png")
        BG_dayStats = ImageTk.PhotoImage(dayStatsBG)
        BG = Label(current_window, image = BG_dayStats)
        BG.pack()
        BG.image = BG_dayStats

        # Go back button
        backPic = Image.open("backBttn.png")
        backBttn = ImageTk.PhotoImage(backPic)
        back_button = Button(current_window, image = backBttn, activebackground = "#e8dfab", cursor = "hand2",
                             borderwidth = 0, justify = CENTER, bg = "#e8dfab", command = incomeStatistic)
        back_button.config(borderwidth = 0)
        back_button.place(x = 68, y = 35)
        back_button.image = backBttn

        # List for combobox
        hmExist = []
        dmyExist = []

        def historyTable () :
            dmyImport = dmyCombobox.get()
            hmImport = hmCombobox.get()
            table = Frame(current_window, height=800, width=620, bg="#e8dfab")
            table.place(x=80, y=130)
        
            # Setting TABLE
            tree = ttk.Treeview(table, columns=("ID","Menu","Amount","Price","Time"))
            tree.heading("ID", text="ที่")
            tree.heading("Menu", text="เมนู")
            tree.heading("Amount", text="จำนวน")
            tree.heading("Price", text="ราคา")
            tree.heading("Time", text="เวลา")
            tree.column("ID", anchor="center", width = 50)
            tree.column("Menu", anchor="center", width = 200)
            tree.column("Amount", anchor="center", width = 90)
            tree.column("Price", anchor="center", width = 90)
            tree.column("Time", anchor="center", width = 90)
            tree.column("#0", width=0, stretch= NO)
            
            space = "-" * 40
            # If only DMY
            if dmyImport and hmImport == "ทั้งหมด":
                c.execute('''SELECT * FROM historyBill''')
                showData = c.fetchall()  
                count = int(1)
                summaryExist = []
                incomeAll = int(0)
                for row in showData:
                    if str(row[1]) == str(dmyImport):
                        if int(count) == 1:
                            summaryExist.append(int(row[9]))
                        tree.insert("","end", values=(count,row[6],row[7],row[8],row[5]))
                        if int(row[9]) not in summaryExist:
                            summaryExist.append(int(row[9]))
                        count += 1
                for a in summaryExist:
                    incomeAll = incomeAll + int(a)
                tree.insert("","end", values=(space,space,"รวม",incomeAll,space))
                # Both DMY and hm
            elif dmyImport and hmImport != "ทั้งหมด":
                c.execute('''SELECT * FROM historyBill''')
                showData = c.fetchall()  
                count = int(1)
                incomeAll = int(0)
                summary = int()
                for row in showData:
                    if (str(row[1]) == str(dmyImport)) and (str(row[5]) == str(hmImport)) :
                        tree.insert("","end", values=(count,row[6],row[7],row[8]))
                        summary = row[9]
                        count += 1
                        incomeAll = incomeAll + int(row[8])
                if int(summary) == int(incomeAll):
                    tree.insert("","end", values=(space,space,"รวม",incomeAll,space))
                elif int(summary) < int(incomeAll):
                    tree.insert("","end", values=(space,"ยอดก่อนหักส่วนลด: %d" %int(incomeAll),"รวม",summary,space))
            
            # Configure vertical scrollbar
            vsb = ttk.Scrollbar(table, orient="vertical", command=tree.yview)
            tree.configure(yscrollcommand=vsb.set)
            vsb.pack(fill="y", side="right")

            # ปรับ Text
            tree.configure(style="Custom.Treeview")
            custom_style = ttk.Style()
            custom_style.configure("Custom.Treeview.heading", font = ("DB HELVETHAICA X BD EXT", 25))
            custom_style.configure("Custom.Treeview", font = ("DB HELVETHAICA X BD EXT", 16), rowheight = 30)
            
            tree.pack() 
        
        # Import HM from dmy
        def show_HM_toCombobox (event):
            if hmExist:
                hmExist.clear ()
            dmyImport = dmyCombobox.get()
            if dmyImport:
                c.execute('''SELECT id,dmy,hm FROM historyBill''')
                hmCollect = c.fetchall ()
                hmExist.append("ทั้งหมด")
                for j in hmCollect:
                    if str(j[1]) == str(dmyImport):
                        if int(j[0]) == 1:
                            hmExist.append(str(j[2]))
                        else:
                            if str(j[2]) not in hmExist:
                                hmExist.append(str(j[2]))
                            else:
                                pass

            hmCombobox.config(values = hmExist)

        # Confirm DMY & HM to see data table
        statsBttn = Image.open("IncomeStats_bttn.png")
        statsBttn = statsBttn.resize((int(statsBttn.width*0.6),int(statsBttn.height*0.6)))
        Bttn_stats = ImageTk.PhotoImage(statsBttn)
        Bttn_confirm = Button(current_window, image = Bttn_stats, bg = "#e8dfab", activebackground = "#e8dfab", cursor = "hand2",
                              borderwidth = 0, command = historyTable)
        Bttn_confirm.place(x = 680, y = 375)
        Bttn_confirm.image = Bttn_stats


        # Input dmy to combobox from historyBill
        c.execute('''SELECT id,dmy FROM historyBill''')
        dmyCollect = c.fetchall ()
        for i in dmyCollect:
            if i[0] == 1:
                dmyExist.append(str(i[1]))
            else:    
                if str(i[1]) not in dmyExist :
                    dmyExist.append(str(i[1]))
                else:
                    pass
        dmyCombobox = ttk.Combobox(current_window, values = dmyExist, cursor = "ibeam",
                                font = ("DB HELVETHAICA X BD EXT", 20), width = 15, justify = LEFT)
        dmyCombobox.place(x = 676, y = 207)
        dmyCombobox.bind('<<ComboboxSelected>>', show_HM_toCombobox)

        hmCombobox = ttk.Combobox(current_window,font = ("DB HELVETHAICA X BD EXT", 20), 
                                  cursor = "ibeam", width = 15, justify = LEFT)
        hmCombobox.place(x = 676, y = 325)

    def toMonthPage () :
        global current_window
        if current_window:
            current_window.destroy()
    
        # Setting Window
        current_window = Tk ()
        current_window.title("Restaurant")
        current_window.geometry("1000x600+300+100")
        current_window.resizable(False,False)
        current_window.title("My restaurant")

        # Background
        monthStatsBG = Image.open("IncomeStats_monthBG.png")
        BG_montStats = ImageTk.PhotoImage(monthStatsBG)
        BG = Label(current_window, image = BG_montStats)
        BG.pack()
        BG.image = BG_montStats

        # Go back button
        backPic = Image.open("backBttn.png")
        backBttn = ImageTk.PhotoImage(backPic)
        back_button = Button(current_window, image = backBttn, activebackground = "#e8dfab", cursor = "hand2", 
                             borderwidth = 0, justify = CENTER, bg = "#e8dfab", command = incomeStatistic)
        back_button.config(borderwidth = 0)
        back_button.place(x = 68, y = 35)
        back_button.image = backBttn

        # List for combobox
        monthExist = []  

        def plot_graph():
            monthImport = monthCombobox.get()
            if monthImport:
                dayExist = []
                summaryExist = []
                summaryAll = []

                c.execute('''SELECT day,month,summary FROM historyBill''')
                history = c.fetchall ()
                for x in history:
                    if  len(dayExist) == 0 and len(summaryExist) == 0:
                        dayExist.append(int(x[0]))
                        summaryExist.append(int(x[2]))
                        summaryAll.append(int(x[2]))
                    else:
                        if int(x[0]) not in dayExist:
                            dayExist.append(int(x[0]))
                            summaryAll.append(int(x[2]))
                        
                        else:
                            pos = len(summaryAll)
                            if int(x[2]) not in summaryExist:
                                summaryAll[pos-1] = summaryAll[pos-1] + int(x[2])
                                summaryExist.append(int(x[2]))
                print(summaryExist)
                                
                # Data for the line graph
                x_values = dayExist
                y_values = summaryAll

                # Create a figure and axis    
                font_style2 = {'fontname': 'DB HELVETHAICA X', 'fontsize': 18}
                fig, ax = plt.subplots()

                # Plot the line graph
                ax.plot(x_values, y_values, label='Income', marker='o')

                # Add data labels to the plot
                for i, (x, y) in enumerate(zip(x_values, y_values)):
                    ax.text(x, y, f'{y}', fontsize=8, ha='right', va='bottom')

                ax.set_xlabel('Date', **font_style2)
                ax.set_ylabel('Money in BAHT', **font_style2)
                ax.set_title('%s Income Graph' %monthImport ,**font_style2)
                ax.legend()

                # Save to IMAGE and SHOW
                image_filename = 'income_graph.png'
                fig.savefig(image_filename)
                
                graphPic = Image.open("income_graph.png")
                graphPic = graphPic.resize((int(graphPic.width*0.65),int(graphPic.height*0.65)))
                picGraph = ImageTk.PhotoImage(graphPic)
                graphShow = Label(current_window,image = picGraph)
                graphShow.place(x = 285, y = 135)
                graphShow.image = picGraph

            else:
                messagebox.showerror("ดูสถิติ","! โปรดกรอกเดือนให้ครบถ้วนก่อน !")
        
        # Import data to month Combobox
        c.execute('''SELECT id,month FROM historyBill''')
        monthCollect = c.fetchall()
        for i in monthCollect:
            if int(i[0]) == 1:
                monthExist.append(i[1])
            else:
                if i[1] not in monthExist:
                    monthExist.append(i[1])
                else:
                    pass
        
        # Month Combobox
        monthCombobox = ttk.Combobox(current_window, values = monthExist, font = ("DB HELVETHAICA X BD EXT", 20), 
                                     width = 10, justify = LEFT, cursor = "ibeam")
        monthCombobox.place(x = 420, y = 508)

        # Confirm month Combobox Button
        statsBttn = Image.open("IncomeStats_bttn.png")
        statsBttn = statsBttn.resize((int(statsBttn.width*0.6),int(statsBttn.height*0.6)))
        Bttn_stats = ImageTk.PhotoImage(statsBttn)
        Bttn_confirm = Button(current_window, image = Bttn_stats, bg = "#e8dfab", activebackground = "#e8dfab", cursor = "hand2",
                              borderwidth = 0, command = plot_graph)
        Bttn_confirm.place(x = 680, y = 500)
        Bttn_confirm.image = Bttn_stats


    # TO Day statistics Button
    dayPic = Image.open("statistics_dayBttn.png")
    picDay = ImageTk.PhotoImage(dayPic)
    toDay_button = Button(current_window, image = picDay, activebackground = "#e8dfab", cursor = "hand2",
                          borderwidth = 0, justify = CENTER, bg = "#e8dfab", command =toDayPage)
    toDay_button.config(borderwidth = 0)
    toDay_button.place(x = 325, y = 236)
    toDay_button.image = picDay

    # TO Month statistics Button
    monthPic = Image.open("statistics_monthBttn.png")
    picMonth = ImageTk.PhotoImage(monthPic)
    toMonth_button = Button(current_window, image = picMonth, activebackground = "#e8dfab", cursor = "hand2",
                            borderwidth = 0, justify = CENTER, bg = "#e8dfab", command = toMonthPage)
    toMonth_button.config(borderwidth = 0)
    toMonth_button.place(x = 325, y = 330)
    toMonth_button.image = picMonth

homeFunc()

current_window.mainloop()
