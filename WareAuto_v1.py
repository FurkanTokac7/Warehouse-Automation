from collections import ChainMap
from email import message
from logging import WARNING, warning
from multiprocessing.sharedctypes import Value
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
# import Tkinter as tk  # if using python 2
import sys,os
import sqlite3
from tkinter.filedialog import askopenfilename
import webbrowser

from numpy import delete

class MenuBar(tk.Menu):
    def __init__(self, parent):
        tk.Menu.__init__(self, parent)
        #Menu
        ##Options
        fileMenu = tk.Menu(self, tearoff=False)
        self.add_cascade(label="File",underline=0, menu=fileMenu)
        fileMenu.add_command(label="Exit", underline=2, command=self.quit)
        ##About
        aboutMenu = tk.Menu(self,tearoff=False)
        self.add_cascade(label="About",underline=0,menu=aboutMenu)
        aboutMenu.add_command(label="Contact & Shortcuts",underline=2,command=self.About)
        ##Database
        databaseMenu = tk.Menu(self,tearoff=False)
        self.add_cascade(label="Database",underline=1,menu=databaseMenu)
        databaseMenu.add_command(label="Create Database",underline=0,command=self.Database)


    #About
    def About(self):
        about_page = tk.Toplevel(self)
        about_page.geometry("600x500")
        about_page.resizable(0,0)
        about_page.title("About")

        programmer_labelframe = tk.LabelFrame(about_page,text="- Programmer -",font=('Helvetica 15 bold'))
        programmer_labelframe.pack(padx=10, pady=10)
        programmer_label = tk.Label(programmer_labelframe,text = "Furkan Tokaç",font=('Helvetica 12'))
        mail_label = tk.Label(programmer_labelframe,text = "furkantokac7@gmail.com",font=('Helvetica 12'))
        programmer_label.pack()
        mail_label.pack()

        shortcuts_labelframe = tk.LabelFrame(about_page,text="- Shortcuts -",font=('Helvetica 15 bold'))
        shortcuts_labelframe.pack(padx=10, pady=10)
        shortcut_1 = tk.Label(shortcuts_labelframe,text = "ctrl + i :\nIt shows the information of the selected product clearly.",font=('Helvetica 12'))
        shortcut_1.pack()
        shortcut_2 = tk.Label(shortcuts_labelframe,text = " \nctrl + d :\nDeletes the information of the selected product.",font=('Helvetica 12'))
        shortcut_2.pack()
        shortcut_3 = tk.Label(shortcuts_labelframe,text = "\nctrl + e :\nIt sends the information of the product whose\n information is desired to be changed,\n directly to the relevant box..",font=('Helvetica 12'))
        shortcut_3.pack()
        shortcut_4 = tk.Label(shortcuts_labelframe,text = "\nDouble - Left Click :\nIt directs you to the relevant link of the products.",font=('Helvetica 12'))
        shortcut_4.pack()
        shortcut_5 = tk.Label(shortcuts_labelframe,text = "\nDouble - Left Click :\nIt serves to make the shelves full or not full.",font=('Helvetica 12'))
        shortcut_5.pack()

    #Database
    def Database(self):
        #Page Object
        createDatabase_page = tk.Toplevel(self)
        #Geometry and Title
        createDatabase_page.geometry("300x100")
        createDatabase_page.resizable(0,0)
        createDatabase_page.title("Create Database")
        #Other Widgets
        ##Variables
        self.databaseName_var = tk.StringVar()
        ## Database
        database_LabelFrame = tk.LabelFrame(createDatabase_page,text="Create Database",font=('Helvetica 12 bold'))
        databaseName_label = tk.Label(database_LabelFrame,text = "Database Name:")
        databaseName_entry = tk.Entry(database_LabelFrame,textvariable=self.databaseName_var)
        database_addButton = tk.Button(database_LabelFrame,text = "Create",command=self.create_database,
                                       background="seagreen",height="1",width="16",font=('Helvetica 9 bold'))
 
        database_LabelFrame.pack(padx=10, pady=10)
        databaseName_label.pack()
        databaseName_entry.pack()

        database_addButton.pack()


    #Menu - Options - Exit functions
    def quit(self):
        sys.exit(0)


    # --------- Database Create Page ---------
    def create_database(self):
        database_name = self.databaseName_var.get()
        database_dbName= database_name+".db"
        current_dir = os.getcwd()
        dirs = os.listdir(current_dir)

        if not database_dbName in dirs:
            if database_name.isalnum():
                sqlite3.connect(database_dbName)
                conn = sqlite3.connect(database_dbName)
                curr= conn.cursor()
                query_shelf = """
                        CREATE TABLE IF NOT EXISTS ShelfTable
                        ([shelf_id] INTEGER PRIMARY KEY NOT NULL, [shelf_code] TEXT UNIQUE NOT NULL, [is_full] INTEGER NOT NULL)
                        """
                query_product = """
                        CREATE TABLE IF NOT EXISTS ProductTable
                        ([product_id] INTEGER PRIMARY KEY, [product_name] TEXT UNIQUE NOT NULL, [shelf_loc] TEXT,
                        [product_info] TEXT,[link] TEXT)
                        """
                curr.execute(query_shelf)
                curr.execute(query_product)
                messagebox.showinfo("Information","The database was created successfully.")
                self.databaseName_var.set("")

                ## Add 'No Loc.'value (Shelf Table)
                no_loc_query = "Insert Into ShelfTable(shelf_code,is_full) Values('No Loc.','Not Full')"
                curr.execute(no_loc_query)
                conn.commit()
            else:
                messagebox.showerror("Warning","Please enter a valid name.")

        else:
            messagebox.showerror("Warning","Such a database exists.")

#---------------------- App.---------------------- 
class App(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        
        #Title and Geometry
        self.title("Active Database: None")
        self.geometry("1400x750")
        self.resizable(0,0)

        s = ttk.Style()
        s.theme_use("clam")

        menubar = MenuBar(self)
        self.config(menu=menubar)
        #Main Interface

        loadDatabase_button = tk.Button(self,text="Load Database",
                                        command=self.openDatabase,background="lightblue",font=('Helvetica 9 bold')).grid(column = 0,row = 0)
        
        
        #---------------------------- Treeview for Products ----------------------------

        # Configure the style of Heading in Treeview widget
        s.configure('Treeview.Heading', background="seagreen")
        columns_product = ["product_name","shelf_loc","product_info","link"]
        self.tree_product = ttk.Treeview(self, columns=columns_product, show='headings')
        ##define columns
        #self.tree_product.heading("product_id", text="Id")
        self.tree_product.heading("product_name", text="Product Name")
        self.tree_product.heading("shelf_loc",text="Location")
        self.tree_product.heading("product_info",text="Info")
        self.tree_product.heading("link",text="Link")
        self.tree_product.bind("<Double-1>", self.link_tree)
        self.tree_product.bind("<Control-Key-i>",self.show_info)
        self.tree_product.bind("<Control-Key-e>",self.copyData_for_edit)
        self.tree_product.bind("<Control-Key-d>",self.delete_shortcut)
        self.tree_product.grid(row=1, column=0, sticky='nsew',padx=(50,50),pady=(25,25))
        #---------------------------- Treeview for all Shelf ----------------------------
        columns = ["shelf_code","is_full"]
        self.tree_shelf = ttk.Treeview(self, columns=columns, show='headings')
        ##define columns
        #self.tree_shelf.heading("shelf_id",text="Id")
        self.tree_shelf.heading("shelf_code", text="Location")
        self.tree_shelf.heading("is_full",text="Situation")
        self.tree_shelf.bind("<Double-1>", self.full_notFull)
        self.tree_shelf.grid(row=1, column=2, sticky='nsew',padx=(20,20),pady=(25,25))

        #--------------------------- Search & Filter ------------------------------------
        ## Variables
        self.searchKey_var = tk.StringVar()
        self.filterKey_var = tk.StringVar()
        searchAndFilter_LabelFrame = tk.LabelFrame(self,text="Search & Filter",font=('Helvetica 12 bold'))
        searchName_label = tk.Label(searchAndFilter_LabelFrame,text = "Key Word: ")
        search_entry = tk.Entry(searchAndFilter_LabelFrame,textvariable=self.searchKey_var)
        search_Button = tk.Button(searchAndFilter_LabelFrame,text = "Search",command=self.search,background="lightblue",
                                  height="1",width="10",font=('Helvetica 9 bold'))

        filterName_label = tk.Label(searchAndFilter_LabelFrame,text = "Location: ")
        filter_entry = tk.Entry(searchAndFilter_LabelFrame,textvariable=self.filterKey_var)
        filter_Button = tk.Button(searchAndFilter_LabelFrame,text = "Filter",command=self.filter,background="lightblue",
                                  height="1",width="10",font=('Helvetica 9 bold'))

        searchAndFilter_LabelFrame.grid(row=2,column=0,padx=10, pady=10)

        searchName_label.grid(row=0,column=0)
        search_entry.grid(row=0,column=1)
        search_Button.grid(row=0,column=2)
        
        filterName_label.grid(row=1,column=0)
        filter_entry.grid(row=1,column=1)
        filter_Button.grid(row=1,column=2)


        ######## Refresh Button ########
        refresh_Button = tk.Button(searchAndFilter_LabelFrame,text = "Refresh",command=self.refresh,background="#F0E68C",
                                  height="1",width="10",font=('Helvetica 9 bold')).grid(row=2,column=2)
        # ============================== Shelf add, remove, change ==============================
        #Other Widgets
        ## Variables
        ###Shelf
        self.addShelfName_var = tk.StringVar()
        self.removeShelfName_var = tk.StringVar()
        self.changeShelfName_var = tk.StringVar() # Old name
        self.changeShelfNameNew_var = tk.StringVar() # New Shelf Name
        ###Add Product
        self.addProductName_var = tk.StringVar()
        self.addLoc_var = tk.StringVar()
        self.addInfo_var = tk.StringVar()
        self.addLink_var = tk.StringVar()
        ###Delete Product
        self.deleteProductName_var = tk.StringVar()
        ###Edit Product
        self.editProductName_var = tk.StringVar()
        self.editLoc_var = tk.StringVar()
        self.editInfo_var = tk.StringVar()
        self.editLink_var = tk.StringVar()

        # Base Shelf Config.
        shelfConfig_LabelFrame = tk.LabelFrame(self,text="Shelf Config.",font=('Helvetica 12 bold'))
        shelfConfig_LabelFrame.grid(row = 2,column = 2)
        ## Add Shelf Frame
        addShelf_LabelFrame = tk.LabelFrame(shelfConfig_LabelFrame,text="Add Shelf", font=('Helvetica 10 bold'))
        addshelfName_label = tk.Label(addShelf_LabelFrame,text = "Shelf Name:")
        addshelfName_entry = tk.Entry(addShelf_LabelFrame,textvariable=self.addShelfName_var)
        addshelfName_addButton = tk.Button(addShelf_LabelFrame,text = "Add",command=self.add_shelf,background="seagreen",
                                           height="1",width="10",font=('Helvetica 9 bold'))
        addShelf_LabelFrame.grid(row=0,column=0)
        addshelfName_label.pack()
        addshelfName_entry.pack()
        addshelfName_addButton.pack()

        ## Remove Shelf Frame 
        removeShelf_LabelFrame = tk.LabelFrame(shelfConfig_LabelFrame,text="Remove Shelf", font=('Helvetica 10 bold'))
        removeshelfName_label = tk.Label(removeShelf_LabelFrame,text = "Shelf Name:")
        removeshelfName_entry = tk.Entry(removeShelf_LabelFrame,textvariable=self.removeShelfName_var)
        removeshelfName_addButton = tk.Button(removeShelf_LabelFrame,text = "Remove",command=self.remove_shelf,background="#EE6A50",
                                              height="1",width="10",font=('Helvetica 9 bold'))
        removeShelf_LabelFrame.grid(row=0,column=2)
        removeshelfName_label.pack()
        removeshelfName_entry.pack()
        removeshelfName_addButton.pack()


        ## Change Shelf Frame 
        changeShelf_LabelFrame = tk.LabelFrame(shelfConfig_LabelFrame,text="Change Shelf Name", font=('Helvetica 10 bold'))
        changeshelfName_label = tk.Label(changeShelf_LabelFrame,text = "Shelf Name:")
        changeshelfName_entry = tk.Entry(changeShelf_LabelFrame,textvariable=self.changeShelfName_var)
        changeshelfName_label_new = tk.Label(changeShelf_LabelFrame,text = "New Shelf Name:")
        changeshelfName_entry_new = tk.Entry(changeShelf_LabelFrame,textvariable=self.changeShelfNameNew_var)
        changeshelfName_addButton = tk.Button(changeShelf_LabelFrame,text = "Change",command=self.change_shelf,background="lightpink",
                                              height="1",width="10",font=('Helvetica 9 bold'))
        changeShelf_LabelFrame.grid(row=0,column=1)
        changeshelfName_label.pack()
        changeshelfName_entry.pack()
        changeshelfName_label_new.pack()
        changeshelfName_entry_new.pack()
        changeshelfName_addButton.pack()
        # ============================== Product Add, Delete, Edit ==============================
        add_delete_edit_LabelFrame = tk.LabelFrame(self,text="Add, Edit & Delete", font=('Helvetica 12 bold'))
        ##### =============== Add Product ===============
        addProduct_LabelFrame =  tk.LabelFrame(add_delete_edit_LabelFrame,text="Add", font=('Helvetica 10 bold'))
        addProductName_label = tk.Label(addProduct_LabelFrame,text = "Product Name:")
        addProductName_entry = tk.Entry(addProduct_LabelFrame,textvariable=self.addProductName_var)

        addShelf_loc_label = tk.Label(addProduct_LabelFrame ,text = "Shelf Location:")
        #addShelf_loc_entry = tk.Entry(addProduct_LabelFrame ,textvariable=self.addLoc_var)
        self.addProduct_ShelfListCombo = ttk.Combobox(addProduct_LabelFrame,width=17,textvariable=self.addLoc_var,state = "readonly")

        addProductInfo_label = tk.Label(addProduct_LabelFrame,text = "Info:")
        addProductInfo_entry = tk.Entry(addProduct_LabelFrame,textvariable=self.addInfo_var)

        addProduct_link_label = tk.Label(addProduct_LabelFrame ,text = "Link:")
        addProduct_link_entry = tk.Entry(addProduct_LabelFrame ,textvariable=self.addLink_var)

        product_addButton = tk.Button(addProduct_LabelFrame,text = "Add",command=self.add_product,background="lightpink",
                                              height="1",width="16",font=('Helvetica 9 bold'))

        add_delete_edit_LabelFrame.grid(row=3,column=0)
        addProduct_LabelFrame.grid(row = 0,column = 0)
        addProductName_label.grid(row=0,column=0)
        addProductName_entry.grid(row=0,column=1)
        addShelf_loc_label.grid(row=1,column=0)
        self.addProduct_ShelfListCombo.grid(row=1,column=1)
        addProductInfo_label.grid(row=2,column=0)
        addProductInfo_entry.grid(row=2,column=1)
        addProduct_link_label.grid(row=3,column=0)
        addProduct_link_entry.grid(row=3,column=1)
        product_addButton.grid(row=4,column=1)

        ### =============== Delete Product ======================
        deleteProduct_LabelFrame =  tk.LabelFrame(add_delete_edit_LabelFrame,text="Delete", font=('Helvetica 10 bold'))
        deleteProductName_label = tk.Label(deleteProduct_LabelFrame,text = "Product Name:")
        self.deleteProductName_entry = tk.Entry(deleteProduct_LabelFrame,textvariable=self.deleteProductName_var)
        product_deleteButton = tk.Button(deleteProduct_LabelFrame,text = "Delete",command=self.delete_product,background="#EE6A50",
                                              height="1",width="16",font=('Helvetica 9 bold'))
        deleteProduct_LabelFrame.grid(row=0,column=1)
        deleteProductName_label.grid(row=0, column=0)
        self.deleteProductName_entry.grid(row=0,column=1)
        product_deleteButton.grid(row=1,column=1)

        ### ========== Edit Product ================
        editProduct_LabelFrame =  tk.LabelFrame(add_delete_edit_LabelFrame,text="Edit", font=('Helvetica 10 bold'))
        editProductName_label = tk.Label(editProduct_LabelFrame,text = "Product Name:")
        self.editProductName_entry = tk.Entry(editProduct_LabelFrame,textvariable=self.editProductName_var)

        editShelf_loc_label = tk.Label(editProduct_LabelFrame ,text = "Shelf Location:")
        #addShelf_loc_entry = tk.Entry(addProduct_LabelFrame ,textvariable=self.addLoc_var)
        self.editProduct_ShelfListCombo = ttk.Combobox(editProduct_LabelFrame,width=17,textvariable=self.editLoc_var,state = "readonly")

        editProductInfo_label = tk.Label(editProduct_LabelFrame,text = "Info:")
        self.editProductInfo_entry = tk.Entry(editProduct_LabelFrame,textvariable=self.editInfo_var)

        editProduct_link_label = tk.Label(editProduct_LabelFrame ,text = "Link:")
        self.editProduct_link_entry = tk.Entry(editProduct_LabelFrame ,textvariable=self.editLink_var)

        product_editButton = tk.Button(editProduct_LabelFrame,text = "Edit",command=self.edit_product,background="seagreen",
                                              height="1",width="16",font=('Helvetica 9 bold'))

        editProduct_LabelFrame.grid(row = 0,column = 2)
        editProductName_label.grid(row=0,column=0)
        self.editProductName_entry.grid(row=0,column=1)
        editShelf_loc_label.grid(row=1,column=0)
        self.editProduct_ShelfListCombo.grid(row=1,column=1)
        editProductInfo_label.grid(row=2,column=0)
        self.editProductInfo_entry.grid(row=2,column=1)
        editProduct_link_label.grid(row=3,column=0)
        self.editProduct_link_entry.grid(row=3,column=1)
        product_editButton.grid(row=4,column=1)
    # ================ Treewiev Link Function =======================
    # == Product ==
    def link_tree(self,event):
        try:
            input_id = self.tree_product.selection()
            currItem = self.tree_product.focus()
            link_ = self.tree_product.item(currItem)['values'][3]
            webbrowser.open(link_)
        except:
            messagebox.showerror(title="Warning",message="An incorrect action was taken.")

    def show_info(self,event):
        try:
            input_id = self.tree_product.selection()
            currItem = self.tree_product.focus()
            result = self.tree_product.item(currItem)['values']
            messagebox.showinfo(title="{0} Info".format(result[0]),message="{0}".format(result[2]))
        except:
            messagebox.showerror(title="Warning",message="An incorrect action was taken.")
    
    def copyData_for_edit(self,event):
        try:
            input_id = self.tree_product.selection()
            currItem = self.tree_product.focus()
            result = self.tree_product.item(currItem)['values']
            self.editProductName_entry.delete(0,"end");self.editProductName_entry.insert(0,result[0])
            conn = sqlite3.connect(self.filename)
            curr = conn.cursor()
            shelfLoc_data_query = "Select shelf_code From ShelfTable"
            curr.execute(shelfLoc_data_query)
            shelfLoc_data = curr.fetchall();shelfLoc_data = [i[0] for i in shelfLoc_data]
            query_forProductId = "Select product_id From ProductTable Where product_name='{0}'".format(result[0])
            curr.execute(query_forProductId)
            self.productId_forEdit = curr.fetchall()[0][0] #**
            try:
                self.editProduct_ShelfListCombo.current(shelfLoc_data.index(result[1]))
            except ValueError:
                self.editProduct_ShelfListCombo.current(shelfLoc_data.index("No Loc."))

            self.editProductInfo_entry.delete(0,"end");self.editProductInfo_entry.insert(0,result[2])
            self.editProduct_link_entry.delete(0,"end");self.editProduct_link_entry.insert(0,result[3])
        except SyntaxError:
            messagebox.showerror(title="Warning",message="An incorrect action was taken.")         
    
    def delete_shortcut(self,evet):

        try:
            input_id = self.tree_product.selection()
            currItem = self.tree_product.focus()
            result = self.tree_product.item(currItem)['values']
            self.deleteProductName_entry.delete(0,"end");self.deleteProductName_entry.insert(0,result[0])
            self.delete_product()
        except:
            messagebox.showerror(title="Warning",message="An incorrect action was taken.")         
       

    # == Shelf ==
    def full_notFull(self,event):
        try:
            input_id = self.tree_shelf.selection()
            currItem = self.tree_shelf.focus()
            result = self.tree_shelf.item(currItem)['values'] #0 -> shelf_code, 1 -> is_full
            conn = sqlite3.connect(self.filename)
            curr = conn.cursor()
            if result[0] != "No Loc." and result[1] == "Not Full":
                is_full_query = "Update ShelfTable Set is_full = 'Full' Where shelf_code = '{0}'".format(result[0])
            elif result[0] != "No Loc." and  result[1] == "Full":
                is_full_query = "Update ShelfTable Set is_full = 'Not Full' Where shelf_code = '{0}'".format(result[0])
            elif result[0] == "No Loc.":
                pass
            curr.execute(is_full_query)
            conn.commit()
            self.refresh()
        except:
            messagebox.showerror(title="Warning",message="An incorrect action was taken.")         
            
    # ================================== MAIN PAGE METHODS =============================================
    # ============ Shelf Conf. Page ==============
    #Add Shelf Name to Database
    def add_shelf(self):
        try:
            conn = sqlite3.connect(self.filename)
            curr = conn.cursor()
            addShelf_query = "Insert Into ShelfTable(shelf_code,is_full) Values('{0}','Not Full')".format(self.addShelfName_var.get())
            curr.execute(addShelf_query)
            conn.commit()
            messagebox.showinfo(title="Operation Successful",message="The shelf named {0} has been Successfully added.".format(self.addShelfName_var.get()))
            self.refresh()
        except:
            messagebox.showerror(title="Warning",message="An incorrect action was taken.")

    # ====== Remove Shelf Name to Database ========
    def remove_shelf(self):
        try:
            conn = sqlite3.connect(self.filename)
            curr = conn.cursor()
            dataControl_query = "Select shelf_id From ShelfTable Where shelf_code='{0}'".format(self.removeShelfName_var.get())
            curr.execute(dataControl_query)
            result = curr.fetchall()
            answer = messagebox.askokcancel(title="Confirmation",
                                            message="Are you sure you want to DELETE the shelf?")
            if answer == True and len(result) > 0:
                deleteShelf_query = "Delete From ShelfTable Where shelf_code = '{0}'".format(self.removeShelfName_var.get())
                curr.execute(deleteShelf_query)
                conn.commit()
                productEdit_query_forShelfRemove = "Update ProductTable Set shelf_loc='No Loc.' Where shelf_loc='{0}'".format(self.removeShelfName_var.get())
                curr.execute(productEdit_query_forShelfRemove)
                conn.commit()
                messagebox.showinfo(title="Operation Successful",message="The shelf named {0} has been successfully deleted.".format(self.removeShelfName_var.get()))
                self.refresh()
            else:
                messagebox.showwarning(title="Warning",message="No such shelf name was found in the system.")
        except:
            messagebox.showwarning(title="Warning",message="First, load the database into the system.")

    #Remove Shelf Name to Database
    def change_shelf(self):
        try:
            shelf_NameOld =self.changeShelfName_var.get()
            shelf_nameNew = self.changeShelfNameNew_var.get()

            conn = sqlite3.connect(self.filename)
            curr = conn.cursor()

            change_shelfName_query = "Select product_name From ProductTable Where shelf_loc='{0}'".format(shelf_NameOld)
            curr.execute(change_shelfName_query)
            result_ForChangeShelf_ = curr.fetchall()

            change_shelfCode_query = "Select shelf_id From ShelfTable Where shelf_code = '{0}'".format(shelf_NameOld)
            curr.execute(change_shelfCode_query)
            result_shelfId = curr.fetchall()[0][0]
            
            if len(result_ForChangeShelf_) > 0:
                result_ForChangeShelf = [i[0] for i in result_ForChangeShelf_]
                for pro_name in result_ForChangeShelf:
                    query_product = "Update ProductTable Set shelf_loc = '{0}' Where product_name = '{1}'".format(shelf_nameNew,pro_name)
                    curr.execute(query_product)
                    conn.commit()
                
                query_shelf = "Update ShelfTable Set shelf_code = '{0}' Where shelf_id = '{1}'".format(shelf_nameNew,result_shelfId)
                curr.execute(query_shelf)
                conn.commit()
                messagebox.showinfo(title="Operation Successful",message="The shelf named {0} has been successfully changed to the name {1}..".format(shelf_NameOld,shelf_nameNew))

                self.refresh()
            
            else:
                messagebox.showwarning(title="Warning",message="No such shelf name was found in the system.")
            
        except:
            messagebox.showerror(title="Warning",message="An incorrect action was taken.")


        

    # =================== Product Conf. Page ===================

    def search(self):
        try:
            conn = sqlite3.connect(self.filename)
            curr = conn.cursor()
            search_query = "Select product_id,product_name,shelf_loc,product_info,link From ProductTable Where product_name Like '{0}%'".format(self.searchKey_var.get())
            curr.execute(search_query)
            search_result_ = curr.fetchall()
            search_result = sorted(search_result_, key=lambda e: e[2], reverse=False)
            if len(search_result) > 0:
                #First delete all product data.
                for i in self.tree_product.get_children():
                    self.tree_product.delete(i)
                # next add all searching result.
                for contact in search_result:
                    self.tree_product.insert('', tk.END, values=contact[1:])
            else:
                messagebox.showinfo(title="Warning",message = "There is no such product.")
        except:
            messagebox.showwarning(title="Warning",message="First, load the database into the system.")

    def filter(self):
        try:
            conn = sqlite3.connect(self.filename)
            curr = conn.cursor()
            if self.filterKey_var.get().isalnum():
                filter_query = "Select product_id,product_name,shelf_loc,product_info,link From ProductTable Where shelf_loc='{0}'".format(self.filterKey_var.get())
            else:
                filter_query = "Select product_id,product_name,shelf_loc,product_info,link From ProductTable Where shelf_loc='No Loc.'"

            curr.execute(filter_query)
            filter_result = curr.fetchall()
            #First delete all product data.
            for i in self.tree_product.get_children():
                self.tree_product.delete(i)
            # next add all searching result.
            for contact in filter_result:
                self.tree_product.insert('', tk.END, values=contact[1:])
        except:
            messagebox.showwarning(title="Warning",message="First, load the database into the system.")
            
    def refresh(self):
        try:
            #Next Refill data again...
            conn = sqlite3.connect(self.filename)
        except:
            messagebox.showwarning(title="Warning",message="First, load the database into the system.")
        else:
            #First delete all data from two treeview.
            for i in self.tree_product.get_children():
                self.tree_product.delete(i)
            for i in self.tree_shelf.get_children():
                self.tree_shelf.delete(i)
                
            curr = conn.cursor() #c is false
            query_get_product = "Select product_id,product_name,shelf_loc,product_info,link From ProductTable"
            curr.execute(query_get_product)
            data_product = curr.fetchall()

            query_get_shelf = "Select shelf_id,shelf_code,is_full From ShelfTable"
            curr.execute(query_get_shelf)
            data_shelf = curr.fetchall()
            data_shelf_ = sorted(data_shelf, key=lambda e: e[1], reverse=False)
            data_product_ = sorted(data_product, key=lambda e: e[2], reverse=False)

            # add data to the product treeview
            for contact in data_product_:
                self.tree_product.insert('', tk.END, values=contact[1:])
            # add data to the product treeview
            for contact in data_shelf_:
                self.tree_shelf.insert('', tk.END, values=contact[1:])

            #First load, combobox
            if self.filename:
                self.addProduct_ShelfListCombo.grid(row=1,column=1)
                conn = sqlite3.connect(self.filename)
                curr = conn.cursor()
                shelfCode_listCombo_data_query = "Select shelf_code From ShelfTable"
                curr.execute(shelfCode_listCombo_data_query)
                shelfCode_listCombo_data = curr.fetchall()
                self.addProduct_ShelfListCombo["values"] = shelfCode_listCombo_data
                self.editProduct_ShelfListCombo["values"] = shelfCode_listCombo_data
            else:
                self.addProduct_ShelfListCombo["values"] = []

    def add_product(self):
        try:
            conn = sqlite3.connect(self.filename)
            curr = conn.cursor()
            is_fullControl_query = "Select is_full From ShelfTable Where shelf_code = '{0}'".format(self.addLoc_var.get())
            curr.execute(is_fullControl_query)
            result_is_full = curr.fetchall()
            if result_is_full[0][0] == "Not Full":
                add_product_query = "Insert Into ProductTable(product_name,shelf_loc,product_info,link) Values('{0}','{1}','{2}','{3}')".format(self.addProductName_var.get(),
                                                                                                                                            self.addLoc_var.get(),
                                                                                                                                            self.addInfo_var.get(),
                                                                                                                                                self.addLink_var.get())
                curr.execute(add_product_query)
                conn.commit()
                messagebox.showinfo(title="Operation Successful",message="The product named {0} has been Successfully added.".format(self.addProductName_var.get()))
                self.refresh()
            else:
                messagebox.showwarning(title="Shelf Full",message="The shelf (code: {0}) is completely full.".format(self.addLoc_var.get()))
        except:
            messagebox.showerror(title="Warning",message="An incorrect action was taken.")


    def delete_product(self):
        try:
            conn = sqlite3.connect(self.filename)
            curr = conn.cursor()
            dataControl_query = "Select product_id,shelf_loc From ProductTable Where product_name='{0}'".format(self.deleteProductName_var.get())
            curr.execute(dataControl_query)
            result_dataControl = curr.fetchall()            
            if len(result_dataControl) == 0:
                messagebox.showwarning(title="Warning",message="No such product name was found in the system.")
            else:

                is_full_query = "Select is_full From ShelfTable Where shelf_code = '{0}'".format(result_dataControl[0][1])
                curr.execute(is_full_query)
                result_is_full = curr.fetchall()
                answer = messagebox.askokcancel(title="Confirmation",
                                                message="Are you sure you want to DELETE the {0}".format(self.deleteProductName_var.get()))
                if answer == True and len(result_dataControl[0]):

                    deleteProduct_query = "Delete From ProductTable Where product_name = '{0}'".format(self.deleteProductName_var.get())
                    curr.execute(deleteProduct_query)

                    if result_is_full[0][0] == "Full":
                        update_isFull_query = "Update ShelfTable Set is_full = 'Not Full' where shelf_code = '{0}'".format(result_dataControl[0][1])
                        curr.execute(update_isFull_query)

                    conn.commit()
                    messagebox.showinfo(title="Operation Successful",message="The product named {0} has been successfully deleted.".format(self.deleteProductName_var.get()))
                    self.refresh()

                elif answer == False:
                    pass

        except:
            messagebox.showwarning(title="Warning",message="First, load the database into the system.")

    def edit_product(self):
        try:
            conn = sqlite3.connect(self.filename)
            curr = conn.cursor()
            product_id = self.productId_forEdit #**
            editProduct_data = (self.editProductName_var.get(),self.editLoc_var.get(),self.editInfo_var.get(),self.editLink_var.get(),product_id,)
            productEdit_query = "Update ProductTable Set product_name='{0}',shelf_loc='{1}',product_info='{2}',link='{3}' Where product_id='{4}'".format(*editProduct_data)

            is_full_query = "Select is_full From ShelfTable Where shelf_code = '{0}'".format(self.editLoc_var.get())
            curr.execute(is_full_query)
            result_is_full = curr.fetchall()
            answer = messagebox.askokcancel(title="Confirmation",
                                                message="Are you sure you want to EDITING the {0}".format(self.editProductName_var.get()))
            
            if answer == True and result_is_full[0][0] == "Not Full":
                curr.execute(productEdit_query)
                conn.commit()
                messagebox.showinfo(title="Information",message="The product information has been successfully changed.")
                self.refresh()

            elif answer == True and result_is_full[0][0] == "Full":
                messagebox.showwarning(title="Shelf Full",message="The shelf (code: {0}) is completely full.".format(self.editLoc_var.get()))
            
            else:pass
            
        except:
            messagebox.showerror(title="Warning",message="An incorrect action was taken.")           


    def openDatabase(self):
        file_types = (("database file","*.db"),)
        file_path = askopenfilename(title="Open a db",initialdir=os.getcwd(),filetypes=file_types).split("/")
        self.filename = file_path[-1]
        if self.filename == "":
            #First delete all data from two treeview.
            for i in self.tree_product.get_children():
                self.tree_product.delete(i)
            for i in self.tree_shelf.get_children():
                self.tree_shelf.delete(i)
                self.title("Active Database: None")
            messagebox.showwarning(title="Warning",message="Please enter a database or create a new one.")
        else:   
            self.title("Active Database: {0}".format(self.filename))
            #Connections..
            conn = sqlite3.connect(self.filename)
            curr = conn.cursor() #c is false
            query_get_product = "Select product_id,product_name,shelf_loc,product_info,link From ProductTable"
            curr.execute(query_get_product)
            self.data_product = curr.fetchall()

            query_get_shelf = "Select shelf_id,shelf_code,is_full From ShelfTable"
            curr.execute(query_get_shelf)
            self.data_shelf = curr.fetchall()
            data_shelf_ = sorted(self.data_shelf, key=lambda e: e[1], reverse=False)
            data_product_ = sorted(self.data_product, key=lambda e: e[2], reverse=False)

            #First delete all data from two treeview.
            for i in self.tree_product.get_children():
                self.tree_product.delete(i)
            for i in self.tree_shelf.get_children():
                self.tree_shelf.delete(i)

            # add data to the product treeview
            for contact in data_product_:
                self.tree_product.insert('', tk.END, values=contact[1:])
            # add data to the product treeview
            for contact in data_shelf_:
                self.tree_shelf.insert('', tk.END, values=contact[1:])
    
        if self.filename:
            self.addProduct_ShelfListCombo.grid(row=1,column=1)
            conn = sqlite3.connect(self.filename)
            curr = conn.cursor()
            shelfCode_listCombo_data_query = "Select shelf_code From ShelfTable"
            curr.execute(shelfCode_listCombo_data_query)
            shelfCode_listCombo_data = curr.fetchall()
            self.addProduct_ShelfListCombo["values"] = shelfCode_listCombo_data
            self.editProduct_ShelfListCombo["values"] = shelfCode_listCombo_data
        else:
            self.addProduct_ShelfListCombo["values"] = []


if __name__ == "__main__":
    app=App()
    app.mainloop()
