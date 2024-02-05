import tkinter as tk
from tkinter import ttk


class Functions:
    """Functions to add and remove parts of the bottom bar"""
    def add(self: ttk.Label, col: int, **params):
        self.grid(column=col, row=0, sticky='ns', **params)
    def remove(self: ttk.Label):
        self.grid_forget()

class Welcome(ttk.Label, Functions):
    """Welcome label on log in screen"""
    def __init__(self, master) -> None:
        super().__init__(master, text='Welcome to Mastermind!', font='QuinqueFive', background=darkBlue)

class User(ttk.Menubutton, Functions):
    """User profile dropdown for after the user has logged in"""
    def __init__(self, master) -> None:
        super().__init__(master, text='User Profile', direction='above', style='dark.TButton', padding=9)
        self.userMenu = tk.Menu(self, tearoff=False)
        self.passChangeFrame = ttk.Frame(app)
        self['menu'] = self.userMenu
        # Add drop down menu options 
        for i, c in zip(('Log out', 'Change Password'), (self.logout, self.change_pass)):
            self.userMenu.add_command(label=i, background=darkBlue, activebackground=fgYellow, foreground=fgYellow, activeforeground=darkBlue, font=('QuinqueFive'), command=c)
        self.delMenu = tk.Menu(self.userMenu, tearoff=False)
        self.delMenu.add_command(label='Confirm', background=darkBlue, activebackground=fgYellow, foreground=fgYellow, activeforeground=darkBlue, font=('QuinqueFive'), command=self.delete_account)
        self.userMenu.add_cascade(label='Delete Account', menu=self.delMenu, background=darkBlue, activebackground=fgYellow, foreground=fgYellow, activeforeground=darkBlue, font=('QuinqueFive'))

    def logout(self):
        """Method to log the user out after that option is selected"""
        global window, done
        # Remove the password change window if it was present
        self.passChangeFrame.grid_forget()
        window.frame.grid(row=1, column=0, sticky='n')
        # Go back to the login / signup screen
        window.remove(); done = True
        window = LoginSignup(mainFrame)
        window.create()

    def change_pass(self):
        """Method to allow the user to change their password"""
        def confirm():
            """Procedure that is called when the confirm button is pressed to check if the inputs are valid"""
            [i.pack_forget() for i in self.errorFrame.winfo_children()]  # Remove current errors
            if self.passEntry.get() == self.confirmEntry.get():  # Check that the 2 passwords match
                if len(self.passEntry.get()) >= 3:  # Check that password has at least 3 characters
                    database.execute(f"UPDATE user SET password = ? WHERE username = ?;", [encrypt(self.passEntry.get()), userName])
                    self.passChangeFrame.grid_forget(); window.frame.grid(row=1, column=0, sticky='n')
            else:  # Add error labels if necessary
                ttk.Label(self.errorFrame, text="Two passwords don't match", style='warning.TLabel').pack(pady=5)
            if len(self.passEntry.get()) < 3:
                ttk.Label(self.errorFrame, text='Password must be 3 character or longer', style='warning.TLabel').pack(pady=5)

        def show_hide():
            """Procedure to switch the password fields to visible or not"""
            self.showHideButton['text'] = '*' if self.showHideButton['text'] == 'A' else 'A'
            for entry in filter(lambda e: type(e) is ttk.Entry, self.inputFrame.winfo_children()):
                entry.config(show='' if self.showHideButton['text'] == '*' else '*')

        window.frame.grid_forget()  # Hide the main window
        # Create password change window
        self.passChangeFrame.grid(column=0, row=1)
        self.inputFrame = ttk.Labelframe(self.passChangeFrame, text='Choose a password', borderwidth=5, relief='solid', labelanchor='n'); self.inputFrame.grid(column=0, row=0, padx=10)
        ttk.Label(self.inputFrame, text='New Password').grid(column=0, row=1, sticky='e', padx=10)
        self.passEntry = ttk.Entry(self.inputFrame, font=('QuinqueFive', 20), show='*')
        self.passEntry.grid(column=1, row=1, sticky='w', padx=10, pady=(15, 5))
        ttk.Label(self.inputFrame, text='Confirm Password').grid(column=0, row=2, sticky='e', padx=10)
        self.confirmEntry = ttk.Entry(self.inputFrame, font=('QuinqueFive', 20), show='*'); self.confirmEntry.grid(column=1, row=2, sticky='w', padx=10, pady=(5, 10))
        self.showHideButton = ttk.Button(self.inputFrame, text='A', command=show_hide, padding=0); self.showHideButton.grid(column=2, row=0, rowspan=3, sticky='w', pady=10, padx=(0, 10))
        # Add Confirm and Cancel buttons
        buttonFrame = ttk.Frame(self.passChangeFrame); buttonFrame.grid(column=0, row=1)
        ttk.Button(buttonFrame, text='Cancel', command= lambda: [self.passChangeFrame.grid_forget(), window.frame.grid(row=1, column=0, sticky='n')]).grid(column=0, row=0, sticky='w')
        ttk.Button(buttonFrame, text='Submit', command=confirm).grid(column=1, row=0, sticky='e')
        self.errorFrame = ttk.Frame(self.passChangeFrame); self.errorFrame.grid(column=0, row=2, pady=10)

    def delete_account(self):
        """Method to delete the current user account"""
        self.passChangeFrame.grid_forget(); window.frame.grid(row=1, column=0, sticky='n')
        database.execute(f"DELETE FROM User WHERE username = ?;", [userName])
        self.logout()

class Restart(ttk.Button, Functions):
    """Button on bottom bar to restart game"""
    def __init__(self, master) -> None:
        super().__init__(master, text='Restart', style='dark.TButton', command=self.activate)
    def activate(self):
        global done, window
        self.remove(); done = True
        window.remove(); window = GameSettings(mainFrame); window.create()

class Finish(ttk.Button, Functions):
    """Button on bottom bar to finish game"""
    def __init__(self, master) -> None:
        super().__init__(master, text='Finnish', style='dark.TButton', command=self.activate)
    def activate(self):
        global done, window
        self.remove(); done = True
        window.finished(False)