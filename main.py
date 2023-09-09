from tkinter import *  # importing all the modules and classes from tkinter
from tkinter import ttk as ttk  # importing the ttk modules from tkinter
# importing message box module from tkinter
from tkinter import messagebox as mb
import datetime  # importing the datetime module
# importing the sqlite3 module | SQLite is a lightweight, file-based database management system that is often used for small to medium-sized applications or embedded systems. It's popular because it's simple to set up and doesn't require a separate server process to run.
import sqlite3
# importing the DateEntry class from the tkcalander module
from tkcalendar import DateEntry


def listAllExpenses():
    global dbconnector, data_table
    data_table.delete(*data_table.get_children())
    all_data = dbconnector.execute('SELECT*FROM ExpenseTracker')
    data = all_data.fetchall()  # listing the data from the table

    for val in data:
        data_table.insert("", END, values=val)


def viewExpenseInfo():
    global data_table
    global dateField, payee, description, amount, modeOfPayment

    if not data_table.selection():
        mb.showerror("No expense selected",
                     "Please select an expense from the table to view its details")

    # collecting the data from the selected row in dictionary format
    currentSelectedExpense = data_table.item(data_table.focus())

    val = currentSelectedExpense['values']

    expenditureDate = datetime.date(int(val[1][:4]), int(val[1][5:7]), int(
        val[1][8:]))  # retreiving the date from expenditure from the list

    dateField.set_date(expenditureDate)
    payee.set(val[2])
    description.set(val[3])
    amount.set(val[4])
    modeOfPayment.set(val[5])


def clearFields():
    global description, payee, amount, modeOfPayment, dateField, data_table

    todayDate = datetime.datetime.now().date()

    description.set("")
    payee.set("")
    amount.set(0.0)
    modeOfPayment.set("cash"), dateField.set_date(todayDate)

    # removing the specific item from the selection
    data_table.selection_remove(*data_table.selection())


def removeExpense():
    if not data_table.selection():
        mb.showerror("No record selected!",
                     "Please select a record to delete!")
        return

    # collecting the data fom the selected row in dictionary format
    currentSelectedExpense = data_table.item(data_table.focus())

    valuesSelected = currentSelectedExpense["values"]

    confirmation = mb.askyesno(
        "Are you sure?", "Are you sure that you want to delete the record of {valueSelected[2]}")

    if confirmation:
        dbconnector.execute(
            "DELETE FROM ExpenseTracker WHERE ID = %d" % valuesSelected[0])
        dbconnector.commit()

        listAllExpenses()

        mb.showinfo("Record deleted successfully!",
                    "The record you wanted to delete the been deleted successfully")


def removeAllExpenses():
    confirmation = mb.askyesno(
        "Are you sure?", "Are you sure that you want to delete all the expense item from the database?", icon="warning")

    if confirmation:
        data_table.delete(*data_table.get_children())

        dbconnector.execute("DELETE FROM ExpenseTracker")
        dbconnector.commit()

        clearFields()

        listAllExpenses()

        mb.showinfo("All Expenses deleted",
                    "All the expenses were successfully deleted")

    else:
        mb.showinfo(
            "OK then", "The task was aborted and no expense was deleted!")


def addAnotherExpense():
    global dateField, payee, description, amount, modeOfPayment
    global connector

    if not dateField.get() or not payee.get() or not description.get() or not amount.get() or not modeOfPayment.get():
        mb.showerror(
            "Fields empty!", "Please fill all the missing fields before pressing the add button!")
    else:
        dbconnector.execute("INSERT INTO ExpenseTracker(Date,Payee,Description,Amount,ModeOfPayement) VALUES(?,?,?,?,?)",
                            (dateField.get_date(), payee.get(), description.get(), amount.get(), modeOfPayment()))

        dbconnector.commit()

        clearFields()
        listAllExpenses()
        mb.showinfo(
            "Expense added", "The expense whose details you just entered has been added to the database")


def editExpense():  # this one allow user to edit the details of the selected expense
    global data_table

    def editExistingExpense():  # this one will update the details of the selected expenses in the database and table

        global dateField, amount, description, payee, modeOfPayement
        global dbconnector, data_table

        currentSelectedExpense = data_table.item(data_table.focus())

        content = currentSelectedExpense["values"]

        dbconnector.execute("UPDATE ExpenseTracker SET Date = ?, Payee = ?, Description = ?, Amount = ?,ModeOfPayment = ?, WHERE ID = ?",
                            (dateField.get_date(), payee.get(), description.get(), amount.get(), modeOfPayment.get(), content[0]))

        dbconnector.commit()

        clearFields()
        listAllExpenses()

        mb.showinfo(
            "Date edited", "We have updated the data and stored in the database as you wanted")
        editSelectedButton.destroy()

        if not data_table.selection():
            mb.showerror("No expenses selected!",
                         "You have not selected any expense in the table for us to edit; please do that!")

            return
        viewExpenseInfo()

        editSelectedButton = Button(frameL3, text="Edit Expense", font=("Bahnschrift Condensed", "13"), width=30, bg="#90EE90",
                                    fg="#000000", relief=GROOVE, activebackground="#008000", activeforeground="#98FB98", command=editExistingExpense)

        editSelectedButton.grid(row=0, column=0, sticky=W, padx=50, pady=10)


def selectedExpenseToWords():
    global data_table
    if not data_table.selection():
        mb.showerror("No expense selected!",
                     "Please select an expense from the table for us to read")
        return

    currentSelectedExpense = data_table.item(data_table.focus())

    val = currentSelectedExpense["values"]

    msg = f'Your expense can be read like: \n"You paid {val[4]} to {val[2]} for {val[3]} on {val[1]} via {val[5]}"'

    mb.showinfo("Here is how to read your expense", msg)


def expenseToWordsBeforeAdding():
    global dateField, description, amount, payee, modeOfPayment

    if not dateField.get() or not payee.get() or not amount.get() or not description.get() or not modeOfPayment.get():
        mb.showerror(
            "Incomplete data", "The data is incomplete, meaning fill all the fields first!")
    else:
        msg = f'Your expense can be read like: \n "You paid {amount.get()} to {payee.get()} for {description.get()} on {dateField.get_date()} via {modeOfPayment.get()}'

        addQuestion = mb.askyesno(
            'Read your record like :', f'{msg}\n\nShould I add it to the database?')

        if addQuestion:
            addAnotherExpense()
        else:
            mb.showinfo("OK", "Please take your time to add this record")


if __name__ == "__main__":
    dbconnector = sqlite3.connect("Expense_Tracker.db")
    dbcursor = dbconnector.cursor()

    dbconnector.execute(
        "CREATE TABLE IF NOT EXISTS ExpenseTracker (ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, Date DATETIME, Payee TEXT, Description TEXT, Amount FLOAT, ModeOfPayement TEXT)"
    )

    dbconnector.commit()

    main_win = Tk()
    main_win.title("EXPENSE TRACKER - JAVAPOINT")

    main_win.geometry("1415x650+400+100")
    main_win.resizable(0, 0)
    main_win.config(bg="#FFFAF0")
    # main_win.iconbitmap("./piggyBank.ico")

frameLeft = Frame(main_win, bg="#FFF8DC")
frameRight = Frame(main_win, bg="#DEB887")
frameL1 = Frame(frameLeft, bg="#FFF8DC")
frameL2 = Frame(frameLeft, bg="#FFF8DC")
frameL3 = Frame(frameLeft, bg="#FFF8DC")
frameR1 = Frame(frameRight, bg="#DEB887")
frameR2 = Frame(frameRight, bg="#DEB887")

frameLeft.pack(side=LEFT, fill="both")
frameRight.pack(side=RIGHT, fill="both", expand=True)
frameL1.pack(fill="both")
frameL2.pack(fill="both")
frameL3.pack(fill="both")
frameR1.pack(fill="both")
frameR2.pack(fill="both", expand=True)


headingLabel = Label(frameL1,
                     text="EXPENSE TRACKER",
                     font=("Bahnschrift Condensed", "25"),
                     width=20,
                     bg="#8B4513",
                     fg="#FFFAF0")
subheadingLabel = Label(
    frameL1,
    text="Data Entry Frame",
    font=("Bahnschrift Condensed", "25"),
    width=20,
    bg="#F5DEB3",
    fg="#000000"
)

headingLabel.pack(fill="both")
subheadingLabel.pack(fill="both")


dateLabel = Label(
    frameL2,
    text="Date",
    font=("consolas", "11", "bold"),
    bg="#FFF8DC",
    fg="#000000"

)

descriptionLabel = Label(frameL2,
                         text="Description",
                         font=("consolas", "11", "bold"),
                         bg="#FFF8DC",
                         fg="#000000")

amountLabel = Label(
    frameL2,
    text="Amount",
    font=("consolas", "11", "bold"),
    bg="#FFF8DC",
    fg="#000000")

payeeLabel = Label(
    frameL2,
    text="Payee",
    font=("consolas", "11", "bold"),
    bg="#FFF8DC",
    fg="#000000")

modelLabel = Label(
    frameL2,
    text="Mode Of \nPayment:",
    font=("consolas", "11", "bold"),
    bg="#FFF8DC",
    fg="#000000")


dateLabel.grid(row=0, column=0, sticky=W, padx=10, pady=10)
descriptionLabel.grid(row=1, column=0, sticky=W, padx=10, pady=10)
amountLabel.grid(row=2, column=0, sticky=W, padx=10, pady=10)
payeeLabel.grid(row=3, column=0, sticky=W, padx=10, pady=10)
modelLabel.grid(row=4, column=0, sticky=W, padx=10, pady=10)

description = StringVar()
payee = StringVar()
modeOfPayment = StringVar(value="Cash")
amount = DoubleVar()

# Drop down calander for the user to enter the date

dateField = DateEntry(
    frameL2,
    date=datetime.datetime.now().date(),
    font=("consolas", "11"),
    relief=GROOVE
)

# creating entry fields to enter the labelled data

descriptionField = Entry(
    frameL2,
    text=description,
    width=20,
    font=("consolas", "11"),
    bg="#FFFFFF",
    fg="#000000",
    relief=GROOVE
)

amountField = Entry(
    frameL2,
    text=amount,
    width=20,
    font=("consolas", "11"),
    bg="#FFFFFF",
    fg="#000000",
    relief=GROOVE
)

payeeField = Entry(
    frameL2,
    text=payee,
    width=20,
    font=("consolas", "11"),
    bg="#FFFFFF",
    fg="#000000",
    relief=GROOVE
)

modeField = OptionMenu(
    frameL2,
    modeOfPayment, *["Cash", "Cheque", "Credit Card", "Debit Card",
                     "UPI", "Paytm", "GooglePay", "PhonePe", "Razorpay"]

)

modeField.config(width=15, font=("consolas", "10"),
                 relief=GROOVE, bg="#FFFFFF")

dateField.grid(row=0, column=1, sticky=W, padx=10, pady=10)
descriptionField.grid(row=1, column=1, sticky=W, padx=10, pady=10)
amountField.grid(row=2, column=1, sticky=W, padx=10, pady=10)
payeeField.grid(row=3, column=1, sticky=W, padx=10, pady=10)
modeField.grid(row=4, column=1, sticky=W, padx=10, pady=10)

insertButton = Button(
    frameL3, text="Add Expense",
    font=("Bahnschrift Condensed", "13"), width=30, bg="#90EE90", fg="#000000", relief=GROOVE,
    activebackground="#008000",
    activeforeground="#98FB98",
    command=addAnotherExpense

)


convertButton = Button(
    frameL3,
    text="Convert to Text Before Adding",
    font=("Bahnschrift Condensed", "13"), width=30, bg="#90EE90", fg="#000000", relief=GROOVE,
    activebackground="#90EE90",
    activeforeground="#000000",
    command=expenseToWordsBeforeAdding
)

resetButton = Button(
    frameL3,
    text="Rest the fields",
    font=("Bahnschrift Condensed", "13"), width=30, bg="#90EE90", fg="#000000", relief=GROOVE,
    activebackground="#008000",
    activeforeground="#FFB4B4",
    command=expenseToWordsBeforeAdding
)
insertButton.grid(row=0, column=1, sticky=W, padx=50, pady=10)
convertButton.grid(row=1, column=1, sticky=W, padx=50, pady=10)
resetButton.grid(row=2, column=1, sticky=W, padx=50, pady=10)


viewButton = Button(
    frameR1,
    text="View Selected Expense\'s Details",
    font=("Bahnschrift Condensed", "13"), width=35, bg="#FFDEAD", fg="#000000", relief=GROOVE,
    activebackground="#A0522D",
    activeforeground="#FFF8DC",
    command=viewExpenseInfo
)


editButton = Button(
    frameR1,
    text="Edit Selected Expense",
    font=("Bahnschrift Condensed", "13"), width=35, bg="#FFDEAD", fg="#000000", relief=GROOVE,
    activebackground="#A0522D",
    activeforeground="#FFF8DC",
    command=editExpense
)

convertButton = Button(
    frameR1,
    text="Convert Selected Expense to a Sentence",
    font=("Bahnschrift Condensed", "13"), width=35, bg="#FFDEAD", fg="#000000", relief=GROOVE,
    activebackground="#A0522D",
    activeforeground="#FFF8DC",
    command=selectedExpenseToWords
)

deleteButton = Button(
    frameR1,
    text="Delete Selected Expense",
    font=("Bahnschrift Condensed", "13"), width=35, bg="#FFDEAD", fg="#000000", relief=GROOVE,
    activebackground="#A0522D",
    activeforeground="#FFF8DC",
    command=removeExpense
)

deleteAllButton = Button(
    frameR1,
    text="Delete All Expense",
    font=("Bahnschrift Condensed", "13"), width=35, bg="#FFDEAD", fg="#000000", relief=GROOVE,
    activebackground="#A0522D",
    activeforeground="#FFF8DC",
    command=removeAllExpenses
)

viewButton.grid(row=0, column=0, sticky=W, padx=10, pady=10)
editButton.grid(row=0, column=1, sticky=W, padx=10, pady=10)
convertButton.grid(row=0, column=2, sticky=W, padx=10, pady=10)
deleteButton.grid(row=1, column=0, sticky=W, padx=10, pady=10)
deleteAllButton.grid(row=1, column=1, sticky=W, padx=10, pady=10)

data_table = ttk.Treeview(
    frameR2,
    selectmode=BROWSE,
    columns=('ID', 'Date', 'Payee', 'Description', 'Amount', 'Mode of Payment')

)

Xaxis_Scrollbar = Scrollbar(
    data_table, orient=HORIZONTAL,
    command=data_table.xview
)

Yaxis_Scrollbar = Scrollbar(
    data_table, orient=VERTICAL,
    command=data_table.yview
)
Xaxis_Scrollbar.pack(side=BOTTOM, fill=X)
Yaxis_Scrollbar.pack(side=RIGHT, fill=Y)

data_table.config(yscrollcommand=Yaxis_Scrollbar.set,
                  xscrollcommand=Xaxis_Scrollbar.set)

data_table.heading('ID', text='S No.', anchor=CENTER)
data_table.heading('Date', text='Date', anchor=CENTER)
data_table.heading('Payee', text='Payee', anchor=CENTER)
data_table.heading('Description', text='Description', anchor=CENTER)
data_table.heading('Amount', text='Amount', anchor=CENTER)
data_table.heading('Mode of Payment', text='Mode of Payment', anchor=CENTER)

data_table.column('#0', width=0, stretch=NO)
data_table.column('#1', width=50, stretch=NO)
data_table.column('#2', width=95, stretch=NO)
data_table.column('#3', width=150, stretch=NO)
data_table.column('#4', width=450, stretch=NO)
data_table.column('#5', width=135, stretch=NO)
data_table.column('#6', width=140, stretch=NO)

data_table.place(relx=0, y=0, relheight=1, relwidth=1)

main_win.mainloop()
