import tkinter
import os
import pickle

from tkinter import ttk,scrolledtext
from datetime import datetime

class TodoData(object):
    def __init__(self):
        self.database_name="pytodo_1.tdb"
        self.data_path=os.getcwd()+"/"+self.database_name
        self.__check_database()
        
    def __check_database(self):
        """it will check if "pytodo_1.tdb" exists or not if not then
it will create it"""
        if not os.path.exists(self.data_path):
            with open(self.data_path,"wb") as tdb:
                pickle.dump([],tdb)
    def load_tdb(self):
        """method to load data from database"""
        with open(self.data_path,"rb") as tdb:
            return pickle.load(tdb)
    def write_tdb(self, tdbList:"list"):
        """writing on database"""
        with open(self.data_path,"wb") as tdb:
            pickle.dump(tdbList,tdb)        
    

class Main_UI(tkinter.Frame):
    def __init__(self,root=tkinter.Tk):
        tkinter.Frame.__init__(self,root)
        self.root=root
        self.root.title("PyTodo")
        self.root.resizable(1,0)
        self.root.minsize(580,352)
        self.root.bind("<Return>",self.root_bind)
        self.root.bind("<Delete>",self.root_bind_del)
        self.root.protocol("WM_DELETE_WINDOW",self.__exit_handle) #exit button handler
        
        self.column=["SN","Date","Task","Duration","Progress%","Status","Message"]
        self.column_size=[7,55,100,38,50,60,10]
        self.date=datetime.now().strftime("%d/%m-%H:%M")
        self.total_item=0

        
        self.entryVar=[tkinter.StringVar() for x in range(3)]
        self.entryVar[1].trace('w',self.type_handle)
        self.entryVar[2].trace('w',self.progress_handle)
        
        self.clear_switch=0
        
        #---database---
        self.database=TodoData()
        self.tdb=self.database.load_tdb()
        
        #--frame------
        self.todo_frame=tkinter.LabelFrame(self.root,text="To Do")
        self.todo_frame.pack(side="left",padx=2,pady=2,fill="x",expand=True)
        
        self.message_frame=tkinter.LabelFrame(self.root,text="Message")
        self.message_frame.pack(side="left")
        
        self.input_frame=tkinter.Frame(self.todo_frame)
        
        self.button_frame=tkinter.Frame(self.todo_frame)
        
        #---treeview---
        self.tree=ttk.Treeview(self.todo_frame,height=11)
        self.tree.pack(padx=2,pady=3,fill="x")
        
        self.tree["columns"]=self.column
        self.tree["show"]="headings"
        self.tree["displaycolumns"]=self.column[:-1]
        self.tree.bind("<<TreeviewSelect>>",self.treeview_bind)
        
        #---treeview tag------
        self.tree.tag_configure("green",foreground="green")
        self.tree.tag_configure("gray",foreground="light gray")
        self.tree.tag_configure("red",foreground="red")
        self.tree.tag_configure("orange",foreground="orange")
        
        for index,col in enumerate(self.column):
            self.tree.column(col,width=self.column_size[index])
            self.tree.heading(col,text=col,command=lambda identity=col: self.heading_bind(identity))
        self.input_frame.pack(anchor="se")
        self.button_frame.pack(anchor="se")
        
        #---scrolled textbox----
        self.stext=scrolledtext.ScrolledText(self.message_frame,width=27,height=23,font="consolas 9")
        self.stext.pack(padx=2,pady=2)
        
        #----input entry-----
        self.task_label=tkinter.Label(self.input_frame,text="Task")
        self.task_label.grid(row=0,column=0)
        self.task_entry=tkinter.Entry(self.input_frame,width=45,textvariable=self.entryVar[0])
        self.task_entry.grid(row=1,column=0,pady=2)
        
        self.dur_label=tkinter.Label(self.input_frame,text="Duration in day")
        self.dur_label.grid(row=0,column=1)
        self.dur_entry=tkinter.Entry(self.input_frame,width=15,textvariable=self.entryVar[1])
        self.dur_entry.grid(row=1,column=1,pady=2)        
        
        self.prog_label=tkinter.Label(self.input_frame,text="Progress %")
        self.prog_label.grid(row=0,column=2)
        self.prog_entry=tkinter.Entry(self.input_frame,width=10,textvariable=self.entryVar[2])
        self.prog_entry.grid(row=1,column=2,pady=2)         
            
        #---button-------
        self.insert_button=tkinter.Button(self.button_frame,text="Insert",width=10,command=self.insert_command)
        self.Update_button=tkinter.Button(self.button_frame,text="Update",width=10,command=self.update_command)
        self.Delete_button=tkinter.Button(self.button_frame,text="Delete",width=10,command=self.delete_command)
        self.Clear_button=tkinter.Button(self.button_frame,text="Clear",width=10,command=self.clear_command)
        
        self.Clear_button.pack(side="left",padx=3,pady=3)
        self.insert_button.pack(side="left",padx=3,pady=3)
        self.Update_button.pack(side="left",padx=3,pady=3)
        self.Delete_button.pack(side="left",padx=3,pady=3)
        
        self.__starting()
    
    def __make_list(self) -> [[]]:
        """this method collect data from treeview and then create multidimentional list
        it will also sort the data in a defined order. (need to polish it more)"""
        incomplete=[]
        complete=[]
        failed=[]
        note=[]
        invalid=[]
        all_item=self.tree.get_children()
        for item in all_item:
            values=self.tree.item(item)["values"]
            if "Done" in values:
                complete.append(values)
            elif "Failed" in values:
                failed.append(values)
            elif "Invalid" in values:
                invalid.append(values)
            elif "Note" in values:
                note.append(values)            
            else:
                incomplete.append(values)
        temp=[]
        temp2={}
        for task in incomplete:
            duration=task[-2]
            duration=float(duration[:duration.index("d")-1])
            if duration not in temp:
                temp.append(duration)
            if duration not in temp2:
                temp2[duration]=[task]
            else:
                temp2[duration].append(task)
        temp.sort()
        incomplete=[]
        for f in temp:
            extract=(temp2[f]) #[[],[]..]
            for item in extract:
                incomplete.append(item)
        
        all_item=incomplete+failed+complete+note+invalid #changing this order will affect how item will listed in next time.
        return all_item                                  #if we restart the program first incomplete task will be shown
    
    def __starting(self):
        """this method will call at starting point, it will read data from database then insert in treeview"""
        message=""
        me="welcome to PyTodo\nOrganize your task easily\n\n"
        for num,task in enumerate(self.tdb):
            date=task[1]
            duration=task[3]
            progress=task[-3]
            task_name=task[2]
            
            progress,status,tag=self.__status(duration, progress, date, task_name) #generating status and color tag
            if tag=="orange":
                message+=task_name+", "
            task.pop(-2)
            task.insert(-1,status)
            task.pop(0)
            task.insert(0,num+1)            
            self.tree.insert("",num,values=task,tag=tag)            
            self.total_item+=1
        if message:
            message+="\nFocus on this task before you failed to complete"
        elif self.total_item==0:
            message="1. press \"clear\", Then insert your task name in task entry, you can make necessary note in this messagebox\n\n2. Type how long it will take to complete in day/s, no duration means it is a note\n\n3. Type a estimate value of your progress and press update to update the data\n\n4. select task from treeview then press delete to delete it"
        self.stext.insert("end",me+message)    
    
    def __elapsed_time(self,date,current_date):
        """every item has its own assigned date, we can get elapsed time by subtracting from current date"""
        
        day_old=datetime.strptime(date,"%d/%m-%H:%M")
        day_Current=datetime.strptime(current_date,"%d/%m-%H:%M")
        day_passed=day_Current-day_old
        day_passed=(abs(day_passed.days)*86400)+day_passed.seconds
        return day_passed/86400 #days. ex: <float> 3.5 days
    
    def __time_update(self):
        self.date=datetime.now().strftime("%d/%m-%H:%M")
        
    def __status(self,duration,progress,date,task):
        """this method generate status data and define treeview color tag"""
        status=""
        tag=""
        if duration:
            x=self.__elapsed_time(date, self.date)
            time_left=round(int(duration)-self.__elapsed_time(date, self.date),2)
            if not progress:
                progress=0
            if time_left>1:
                status=str(time_left)+" days left"
            elif time_left<=1 and time_left>0:
                status=str(time_left)+" day left"
                tag="orange"
            elif time_left<=0:
                status="Failed"
                tag="red"
        elif task:
            status="Note"
        else:
            status="Invalid"
            tag="gray"
        
        if status!="Invalid" and status!="Note" and int(progress)==100:
            tag="green"
            status="Done"
        return (progress,status,tag)
    
    #------------------------------button commands-----------------------     
    def insert_command(self):
        """collect data from all input and then insert in treeview"""
        self.__time_update()
        self.total_item+=1
        serial=self.total_item
        task=self.entryVar[0].get()
        duration=self.entryVar[1].get()
        progress=self.entryVar[2].get()
        date=self.date
        message=self.stext.get("1.0","end-1c")
        if "welcome to" in message:
            message=""
        progress,status,tag=self.__status(duration, progress, date, task)
        
        item=self.tree.insert('',serial,values=(serial,date,task,duration,progress,status,message),tag=tag)
        self.tree.see(item)    
                  
    def update_command(self):
        """only work if clear switch is not pressed and item in treeview is in focus"""
        if not self.clear_switch and self.tree.focus():
            task=self.entryVar[0].get()
            duration=self.entryVar[1].get()
            progress=self.entryVar[2].get()
            message=self.stext.get("1.0","end-1c")
            focused_item=self.tree.focus()
            values=self.tree.item(focused_item)["values"]
            serial=values[0]
            date=values[1]
            
            progress,status,tag=self.__status(duration, progress, date, task)
            
            self.tree.item(focused_item,values=(serial,date,task,duration,progress,status,message),tag=tag)            
            

    def delete_command(self):
        """method for del key event and delete button press"""
        focused_item=self.tree.focus()
        allitem=self.tree.get_children()
        begin=0
        for num,item in enumerate(allitem):
            if item==focused_item: 
                begin=1
            if begin:
                cur_val=self.tree.item(item)["values"]
                cur_val.pop(0)
                cur_val.insert(0,num)
                self.tree.item(item,values=cur_val)
        if focused_item:
            self.tree.delete(focused_item)
            self.total_item-=1
        
    def clear_command(self):
        """clear entrys and scrolledtext"""
        self.clear_switch=1
        for var in self.entryVar:
            var.set("")
        self.stext.delete("1.0","end")
        self.task_entry.focus()
    
    
    
    #--------------event handling functions---------------
    def progress_handle(self,*args):
        """entry type handler to prevent user to input illeagal data and force them to keep number between 0 and 100"""
        temp=self.entryVar[2].get()
        if temp.isdigit():
            if int(temp)>100:
                self.entryVar[2].set("100")
        else:
            self.entryVar[2].set("")
            
    def type_handle(self,*args):
        """entry type handler to prevent user to input illeagal data"""
        temp=self.entryVar[1].get()
        if not temp.isdigit():
            self.entryVar[1].set("")
    
    def root_bind(self,arg):
        """enter key binding, whether enter key call update function or insert function"""
        if not self.clear_switch and self.tree.focus():
            self.update_command()
        else:
            self.insert_command()
    def root_bind_del(self,arg):
        """root del key binding, little trick to avoid item deletion in treeview """
        if not type(self.root.focus_get())==tkinter.scrolledtext.ScrolledText:
            self.delete_command()
            
    def heading_bind(self,identity:'id of heading'):
        """it will sort data accordingly"""
        print(identity,"Not yet implemented")
    
    def treeview_bind(self,arg):
        """treeview item click bind, if any item is in focus, editable data will be in entry and scrolltext box"""
        self.clear_command()
        self.clear_switch=0
        focused_item=self.tree.focus()
        values=self.tree.item(focused_item)["values"]
        for num,var in enumerate(self.entryVar):
            var.set(values[num+2])
        self.stext.insert("end",values[-1])    
    
    def __exit_handle(self):
        """this method calls necessary to save/update entire data in database before closing"""
        tdb=self.__make_list()
        self.database.write_tdb(tdb)
        root.destroy()
    
            
        
            
if __name__=="__main__":
    root=tkinter.Tk()
    ui=Main_UI(root)
    ui.mainloop()
