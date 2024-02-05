import tkinter as tk
from tkinter import ttk
from Game.uml_classes.Bar import Bar

class LoginSignup:
    """First Window where the user can sign up or log in"""
    def __init__(self, frame: ttk.Frame):
        self.frame = frame
        self.bar_welcome = Bar.Welcome(); self.bar_welcome.add()  # Configure the bottom bar
        self.signUpTk = tk.BooleanVar(value=True)  # Variable to store if signing up or loging in
        self.userNameTk = tk.StringVar(); self.passwordTk = tk.StringVar()

    def create(self):
        """Procedure to create the window"""
        root.state('normal')  # Make the window not full screen
        for r in ('Sign up', 'Log in'):  # Add the Sign-up and Log in options
            ttk.Radiobutton(self.frame, text=r, variable=self.signUpTk, value=(r == 'Sign up'), style='Toolbutton', command=self.switch_login_sign_up).grid(column=0 if (r == 'Sign up') else 1, row=0, pady=0, sticky='E' if (r == 'Sign up') else 'W')

        # Add labels and text entry fields for username, password and confirm password fields
        self.inputFrame = ttk.Frame(self.frame, borderwidth=5)
        self.inputFrame.grid(column=0, row=2, columnspan=2, sticky='N', padx=10)
        for id, var, index in zip(('username', 'password'), (self.userNameTk, self.passwordTk), range(2)):
            ttk.Label(self.inputFrame, text=id).grid(column=0, row=index, sticky='E', padx=(10, 0))
            ttk.Entry(self.inputFrame, textvariable=var, name=id, show='' if id == 'username' else '*', font=('QuinqueFive', 20)).grid(row=index, column=1, padx=10, pady=10)
        self.passConfirmLabel = ttk.Label(self.inputFrame, text='Confirm password')
        self.passConfirmEntry = ttk.Entry(self.inputFrame, show='*', name='confirmPassword', font=('QuinqueFive', 20))
        self.passConfirmLabel.grid(column=0, row=2, sticky='E', padx=(10, 0))
        self.passConfirmEntry.grid(row=2, column=1, padx=10, pady=10)

        # Button to show password as text instead of *
        self.showHideButton = ttk.Button(self.inputFrame, text='A', padding=0, command=lambda: self.show_hide_pass(self.passConfirmEntry.cget('show') == '*'))
        self.showHideButton.grid(row=1, column=2, rowspan=3, padx=(0, 10), pady=10, sticky='W')

        # Errors if entry not valid
        errorFrame = ttk.Frame(self.frame); errorFrame.grid(row=5, column=0, sticky='N', columnspan=2)
        self.errors = ('Username already exits', 'Username must be 3 characters or longer', 'Password must be 3 characters or longer', "Two passwords don't match", 'Invalid username', 'Incorrect password')
        self.errorLabels = [ttk.Label(errorFrame, text=e, style='warning.TLabel') for e in self.errors]

        # When Submit button or Enter Key pressed check fields are valid
        ttk.Button(self.frame, text='Submit', command=self.confirm).grid(column=0, row=4, columnspan=2, sticky='N')
        root.bind('<Return>', lambda event: self.confirm())

    def switch_login_sign_up(self):
        """Procedure to hide/show password confirm label and text entry when mode switch"""
        for errorLabel in self.errorLabels:
            errorLabel.pack_forget()
        if self.signUpTk.get():
            self.passConfirmLabel.grid(column=0, row=2, sticky='E', padx=(10, 0))
            self.passConfirmEntry.grid(row=2, column=1, padx=10, pady=10)
        else:
            self.passConfirmLabel.grid_forget(); self.passConfirmEntry.grid_forget()

    def show_hide_pass(self, show_pass: bool):
        """Procedure to show or hide password when button pressed"""
        for entry in filter(lambda e: type(e) is ttk.Entry and e.winfo_name() != 'username', self.inputFrame.winfo_children()):
            entry.config(show='' if show_pass else '*')
        self.showHideButton['text'] = '*' if show_pass else 'A'

    def confirm(self):
        """Procedure to check all inputs are valid before proceeding"""
        global userName, window
        valid = True; userName=self.userNameTk.get().lower()
        for errorLabel in self.errorLabels: errorLabel.pack_forget()
        # get list of current usernames
        current_usernames = list(map(lambda l: l[0], database.select('SELECT username FROM User;')))
        if self.signUpTk.get():  # If user is signing up
            if userName in current_usernames:  # username already exists
                self.errorLabels[0].pack(pady=5); valid = False
            if len(userName) < 3:  # username is not long enough
                self.errorLabels[1].pack(pady=5); valid = False
            if len(self.passwordTk.get()) < 3:  # password is not long enough
                self.errorLabels[2].pack(pady=5); valid = False
            if self.passwordTk.get().lower() != self.passConfirmEntry.get().lower():
                self.errorLabels[3].pack(pady=5)  # password and confirm password don't match
                valid = False
            if valid:
                # If all conditions met then add user to database
                database.add_user(userName, encrypt(self.passwordTk.get().lower()))
        else:  # else if on log in section
            if userName not in current_usernames:  # username doesn't exist
                self.errorLabels[4].pack(pady=5); valid = False
            elif database.select(f"SELECT password FROM User WHERE username = ?", [userName])[0][0] != encrypt(self.passwordTk.get().lower()):
                self.errorLabels[5].pack(pady=5); valid = False  # password incorrect
        if valid:  # if no errors encountered
            self.remove()  # remove this window
            window = GameSettings(mainFrame)  # change window to game setting window
            window.create()  # create game settings window

    def remove(self):
        """Procedure to remove this window"""
        self.bar_welcome.remove()  # clear bottom frame
        clear(mainFrame)  # clear everything from window