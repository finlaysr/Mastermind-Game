"""Finlay Robb - 02/09/23 - Mastermind game for AH Computing Project"""
import tkinter as tk
from tkinter import ttk
from random import choice, shuffle
from PIL import Image, ImageTk
from Modules.os import listdir
from hashlib import sha256
from ctypes import windll
import Modules.AHstandardAlgorythims as AHsa
import Modules.databaseFunctions as DBf

def load_images(dir_pass: str, scale: int | float = 1) -> dict[str, ImageTk.PhotoImage]:
    """Function to load images from a folder to a dictionary"""
    imgs: dict[str, ImageTk.PhotoImage] = {}
    # Loop for every image in the folder
    for filename in filter(lambda f: f[f.find('.'):] == '.png', listdir(dir_pass)):
        with Image.open(f'{dir_pass}/{filename}') as img:
            # Resize the image to the specified scale
            img = img.resize((int(img.size[0]*scale), int(img.size[1]*scale)))
            # Find the file name without the .png extension
            index = filename[:filename.find('.')]
            imgs[index] = ImageTk.PhotoImage(img)
    return imgs

def clear(frame: ttk.Frame) -> None:
    """Procedure to destroy all the objects in a frame"""
    [i.destroy() for i in frame.winfo_children()]

def encrypt(value: str) -> str:
    """Encrypt a string using the sha256 algorithm"""
    return sha256(value.encode()).hexdigest()

class LoginSignup:
    """First Window where the user can sign up or log in"""
    def __init__(self, frame: ttk.Frame):
        self.frame = frame
        self.bar_welcome = Bar.Welcome(); self.bar_welcome.add(col=1, pady=10)  # Configure the bottom bar
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

class GameSettings:
    """Window where game settings are chosen"""
    def __init__(self, frame: ttk.Frame) -> None:
        self.frame = frame
        self.bar_user = Bar.User()  # Add user options dropdown to bottom bar
        self.bar_user.add(col=1)
        # Preset difficulty options
        self.diffs = {'easy': (3, 15, 4), 'normal': (4, 10, 8), 'hard': (6, 8, 10), 'custom': (6, 11, 6)}

    def create(self):
        """Procedure to create this window"""
        root.state('normal')  # Make window not full screen
        self.codeLengthTk = tk.IntVar(value=4)
        self.shotsTk = tk.IntVar(value=10)
        self.colorAmountTk = tk.IntVar(value=8)
        # Create difficulty options
        difficultiesFrame = ttk.Labelframe(self.frame, text='Difficulty', borderwidth=5, relief='solid')
        difficultiesFrame.grid(column=0, row=1, padx=10, pady=(10, 10))
        self.difficultyTk = tk.StringVar(value='normal')
        for name, num, color in zip(('easy', 'normal', 'hard', 'custom'), range(4), ('green', 'yellow', 'red', 'lightblue')):
            ttk.Radiobutton(difficultiesFrame, text=name, variable=self.difficultyTk, value=name, style=f'{color}.Toolbutton', command=lambda n=name: self.selectDiff(n)).grid(column=num, row=0, padx=(10, 0) if num==0 else (0, 10) if num==3 else 0, pady=10)

        # Sliders to show and configure difficulty options
        sliderFrame = ttk.Frame(difficultiesFrame); sliderFrame.grid(column=0, row=2, columnspan=4)
        for index, ranges, var, label in zip((0,1,2), ((2, 10), (2,20), (2,10)), (self.codeLengthTk, self.shotsTk, self.colorAmountTk), ('Length', 'Shots', 'Colours')):
            ttk.Label(sliderFrame, text=label).grid(column=0, row=index, sticky='E')
            ttk.Scale(sliderFrame, orient='horizontal', length=300, from_=ranges[0], to=ranges[1], variable=var, cursor='sb_h_double_arrow', command=lambda event, v=var: [v.set(int(round(float(event)+0.01, 0))), self.difficultyTk.set('custom')]).grid(column=1, row=index, padx=10, pady=10)
            ttk.Label(sliderFrame, textvariable=var).grid(column=2, row=index)

        # Create mode selection options
        modeFrame = ttk.Labelframe(self.frame, text='Mode', borderwidth=5, relief='solid')
        self.modeTk = tk.StringVar(value='classic')
        self.modeDescriptions = {'classic': 'Try and find the code in the least number of shots', 'timed': 'Try and find the code in the shortest time', 'memory': "Same as classic, but you can't see past guesses"}
        modeDescriptionLabel = ttk.Label(modeFrame, justify='center')
        modeDescriptionLabel.grid(column=0, row=1, columnspan=3, pady=10)
        for id, color, num in zip(('classic', 'timed', 'memory'), ('yellow', 'lightblue', 'red'), range(3)):
            ttk.Radiobutton(modeFrame, text=id, value=id, variable=self.modeTk, style=f'{color}.Toolbutton', command=lambda mdl=modeDescriptionLabel: mdl.configure(text=self.modeDescriptions[self.modeTk.get()])).grid(column=num, row=0, padx=(10, 0) if num == 0 else (0,10) if num == 2 else 0, pady=(5, 0))
        modeFrame.grid(column=0, row=3, padx=10, pady=(0, 10))
        root.update()
        modeDescriptionLabel['wraplength'] = modeFrame.winfo_width()
        modeDescriptionLabel['text'] = self.modeDescriptions['classic']

        # Add check buttons for duplicate colors allowed and color-blind mode
        checkFrame = ttk.Frame(self.frame)
        checkFrame.grid(column=0, row=4, pady=0)
        self.duplicatesAllowed = [True]
        ttk.Label(checkFrame, text='Allow duplicates').grid(column=0, row=0, pady=0)
        duplicatesButton = ttk.Button(checkFrame, image=messageImgs['check_true'], padding=0, style='img.TButton', command=lambda: self.checkbutton(duplicatesButton, self.duplicatesAllowed))
        duplicatesButton.grid(column=1, row=0, pady=0)
        self.cbMode = [False]
        ttk.Label(checkFrame, text='Colour blind icons').grid(column=0, row=1, pady=0)
        cbButton = ttk.Button(checkFrame, image=messageImgs['check_false'], padding=0, style='img.TButton', command=lambda: self.checkbutton(cbButton, self.cbMode))
        cbButton.grid(column=1, row=1, pady=0)

        # Add confirm button and bind return key to check settings are valid and go to next screen using self.play() function 
        ttk.Button(self.frame, image=messageImgs['play'], style='img.TButton', padding=0, command=self.play).grid(column=0, row=6)
        root.bind('<Return>', lambda event: self.play())
        self.errorLabel = ttk.Label(self.frame, text='If duplicates not allowed colors must be >= length', wraplength=difficultiesFrame.winfo_width(), style='warning.TLabel', justify='center')

    def selectDiff(self, diff:str) -> None:
        """Procedure change sliders to correct position based on difficulty selected"""
        self.codeLengthTk.set(self.diffs[diff][0])
        self.shotsTk.set(self.diffs[diff][1])
        self.colorAmountTk.set(self.diffs[diff][2])

    def checkbutton(self, button: ttk.Button, var: list[bool]):
        """Procedure to alter appearance of check buttons and store change"""
        var[0] = not(var[0])
        button.config(image=messageImgs['check_true'] if var[0] else messageImgs['check_false'])

    def play(self):
        """Procedure to start game if conditions are valid"""
        global codeLength, colorAmount, mode, difficulty, shots, window
        if not self.duplicatesAllowed[0] and (self.codeLengthTk.get() > self.colorAmountTk.get()):  # If duplicates not allowed then check code length <= color amount
            self.errorLabel.grid(column=0, row=7)
        else:
            codeLength = self.codeLengthTk.get()
            colorAmount = self.colorAmountTk.get()
            mode = self.modeTk.get()
            shots = self.shotsTk.get() if mode != 'memory' else 1
            difficulty = self.difficultyTk.get()
            window.remove()  # Remove current window
            window = Game(mainFrame, self.duplicatesAllowed[0], self.cbMode[0])  # Set current window to game window
            window.create()  # Create game window

    remove = lambda self: [clear(mainFrame), self.bar_user.remove()]  # Function to remove this window

class Game:
    """Window where main game is played"""
    def __init__(self, frame: ttk.Frame, duplicates: bool, color_blind):
        self.frame = frame
        self.duplicates = duplicates; self.colorBlind = color_blind
        self.selectedPos = 0; self.prevSelected = 0
        self.guess = ['' for _ in range(codeLength)]
        self.boardData = []; self.scoreData = []
        # Configure bottom bar
        self.bar_restart = Bar.Restart(); self.bar_restart.add(0)
        self.bar_user = Bar.User(); self.bar_user.add(1)
        self.bar_finish = Bar.Finish(); self.bar_finish.add(2)

    def create(self):
        """Procedure to create this window"""
        root.state('zoomed')  # Make window full screen
        global timeShots, timerShotsLabel, window, done

        # Add welcome text, current difficulty, mode and shots taken / time taken so far
        self.infoFrame = ttk.Frame(mainFrame)
        self.infoFrame.grid(column=1, row=0, padx=20, sticky='NW')

        ttk.Label(self.infoFrame, text='Welcome to Mastermind!').grid(column=0, row=0, pady=(0, 10))
        ttk.Label(self.infoFrame, text=f'Difficulty: {difficulty}').grid(column=0, row=1, pady=(0, 10))
        ttk.Label(self.infoFrame, text=f'Mode: {mode}').grid(column=0, row=2, pady=(0, 20))
        timerShotsLabel = ttk.Label(self.infoFrame, text=f'{"Timer: 0:00" if mode == "timed" else "Shots used: 0"}' + (f"/{shots}" if mode == 'classic' else ""))
        timerShotsLabel.grid(column=0, row=3, pady=(0, 10))
        root.update()

        # Find the scale so everything fits on the screen and load the images at that scale
        totalHeight = (shots+1)*100 + messageImgs['mastermind'].height()
        totalWidth = 80 + 90*codeLength + int(round((codeLength+0.1)/2, 0))*20 + (int(round((codeLength+0.1)/2, 0))-1)*10
        screenHeight = root.winfo_height() - bottomBar.winfo_height()
        screenWidth = root.winfo_width() - self.infoFrame.winfo_height()
        scale = round(min([(screenHeight) / (totalHeight+135), (screenWidth) / totalWidth, 1]), 2)
        self.colorImgs = load_images(f'Images/{"colorBlind" if self.colorBlind else "colors"}', scale)
        self.boardParts = load_images('Images/board', scale)

        # Define some constants to be of use later when creating the window
        self.spacing = round(10*scale, 2)
        self.colorOrder = ['red', 'orange', 'yellow', 'green', 'blueLight', 'blueDark', 'purple', 'pink', 'white', 'black']

        # Generate the code using 2 different algorithms depending on if duplicate colors are allowed
        if self.duplicates:
            self.correctCode = [choice(self.colorOrder[:colorAmount]) for _ in range(codeLength)]
        else:
            self.correctCode = self.colorOrder[:colorAmount]
            shuffle(self.correctCode)
            self.correctCode = self.correctCode[:codeLength]
        print(*self.correctCode)

        # Start timer if in timed mode
        done = False; timeShots = 0
        if mode == 'timed':
            def timer():
                global timeShots
                if not done:
                    timeShots += 1
                    timerShotsLabel['text'] = f'Timer: {timeShots//60}:{timeShots%60:02d}'
                    root.after(1000, timer)
            if not done: root.after(1000, timer)

        # Set up past guesses board
        history_frame = ttk.Frame(self.frame)
        history_frame.grid(column=0, row=0, sticky='SW')
        for rw in range(shots-1):  # Make sure all the rows have extra space between them
            history_frame.rowconfigure(index=rw, minsize=self.boardParts['space_blank'].height() + self.spacing)

        self.historyColours = [[] for _ in range(shots)]  # 2D array for image labels for past guesses
        self.historyScores = [[] for _ in range(shots)]  # 2D array for image labels for past scores 
        for rw in range(shots):  # Add each row in the past history board
            for col in range(codeLength):  # Create and place each image label in the history board
                ttk.Label(history_frame, image=self.boardParts['space_blank']).grid(row=rw, column=col, sticky='NW')
                self.historyColours[-(rw+1)].append(ttk.Label(history_frame, image=self.boardParts['color_blank']))
                self.historyColours[-(rw+1)][-1].grid(row=rw, column=col, pady=(self.spacing*2, 0), padx=(self.spacing*2,0), sticky='NW')

            # Create and place the scores labels as well as the background shapes 
            curCol = col + 1
            ttk.Label(history_frame, image=self.boardParts['mark_leftEnd']).grid(row=rw, column=curCol, sticky='NW'); curCol += 1
            markCols = int(round((codeLength+0.1)/2, 0))
            for markCol in range(markCols):
                ttk.Label(history_frame, image=self.boardParts['mark_blankSpaces']).grid(row=rw, column=curCol, sticky='NW')
                self.historyScores[-(rw+1)].append(ttk.Label(history_frame, image=self.boardParts['mark_blank']))
                self.historyScores[-(rw+1)][-1].grid(row=rw, column=curCol, pady=(self.spacing*2, 0), sticky='NW')
                if markCol < markCols-1 or codeLength % 2 == 0:
                    self.historyScores[-(rw+1)].append(ttk.Label(history_frame, image=self.boardParts['mark_blank']))
                    self.historyScores[-(rw+1)][-1].grid(column=curCol, row=rw, pady=(self.spacing*5, 0), sticky='NW')
                if markCol < markCols-1:
                    curCol += 1
                    ttk.Label(history_frame, image=self.boardParts['mark_spacer']).grid(row=rw, column=curCol, sticky='NW')
                curCol += 1
            ttk.Label(history_frame, image=self.boardParts['mark_rightEnd']).grid(row=rw, column=curCol, sticky='NW')

        # Add spacing between the history board and current guess board
        self.frame.rowconfigure(2, minsize=self.spacing*2)

        # Set up current guess board
        self.optionsFrame = ttk.Frame(self.frame)
        self.optionsFrame.grid(column=0, row=3, sticky='NW')

        self.optionSpaces = []; self.optionColours = []  # Lists for background spaces and colors
        for option in range(codeLength):
            # Add the background images that can be changed when selected
            self.optionSpaces.append(ttk.Label(self.optionsFrame, image=self.boardParts['space_blank'], cursor='tcross'))
            self.optionSpaces[-1].bind("<Button-1>", lambda event, num=option: self.space_selected(num))
            self.optionSpaces[-1].grid(column=option, row=0, sticky='NW')
            # Add the spaces that can be clicked to select that space
            self.optionColours.append(ttk.Label(self.optionsFrame, image=self.boardParts['color_blank'], cursor='tcross'))
            self.optionColours[-1].bind("<Button-1>", lambda event, num=option: self.space_selected(num))
            self.optionColours[-1].grid(column=option, row=0, pady=(self.spacing*2, 0), padx=(self.spacing*2, 0), sticky='NW')

        # Add the confirm button that can be clicked once all the spaces are filled in
        ttk.Label(self.optionsFrame, image=self.boardParts['mark_leftEnd']).grid(column=option+1, row=0, sticky='NW')
        confirm_label = ttk.Label(self.optionsFrame, image=self.boardParts['space_confirmed'], cursor='center_ptr')
        confirm_label.bind("<Button-1>", lambda event: self.confirm_choice())
        confirm_label.grid(column=option+2, row=0)
        ttk.Label(self.optionsFrame, image=self.boardParts['mark_rightEnd']).grid(column=option+3, row=0)

        # Bind the number keys to the colors, the enter key to the confirm button, and the return key to move the slected space back one
        for key in (range(colorAmount) if colorAmount < 10 else list(range(colorAmount))+[-1]):
            root.bind(f'{key+1}', lambda event, k=key: self.color_selected(self.colorOrder[k]))
        root.bind('<Return>', lambda event: self.confirm_choice())
        root.bind('<BackSpace>', lambda event: self.space_selected(self.selectedPos - 1 if self.selectedPos != 0 else codeLength - 1))

        # Create pallete of available colors 
        self.paletteFrame = ttk.Frame(self.frame)
        self.paletteFrame.grid(column=0, row=4, sticky='NW', columnspan=2)
        self.paletteFrame.rowconfigure(index=0, minsize=self.spacing*7)

        selectedLabel = ttk.Label(self.paletteFrame, image=self.boardParts['color_selected'])
        for color, col in zip(self.colorOrder[:colorAmount], range(colorAmount)):
            c = ttk.Label(self.paletteFrame, image=self.colorImgs[color], cursor='tcross')
            c.bind("<Button-1>", lambda event, c=color: self.color_selected(c))
            # Add an outline around the color label when the mouse is over it
            c.bind("<Enter>", lambda event, c=col: selectedLabel.grid(column=c, row=0, columnspan=2, sticky='W'))
            c.bind("<Leave>", lambda event: selectedLabel.grid_forget())
            c.grid(column=col, row=0, padx=(self.spacing, 0) if col != colorAmount-1 else self.spacing)

        self.space_selected(0)  # Set the selected space to the first space

    def get_score(self, user_guess: list[str], correct: list[str]) -> dict:
        """Get the score of a guess based on the mastermind scoring system"""
        length = len(correct)
        score = {'a': 0, 'b': 0}
        for scoringMain in range(length):  # Find the amount of correct colors in the correct place
            if correct[scoringMain] == user_guess[scoringMain]:
                score['a'] += 1; correct[scoringMain] = 'X'; user_guess[scoringMain] = 'x'
        for scoringMain in range(length):  # Find the amount of correct colors in the wrong place
            for scoringMinor in range(length):
                if correct[scoringMain] == user_guess[scoringMinor]:
                    score['b'] += 1; correct[scoringMain] = 'X'; user_guess[scoringMinor] = 'x'
        return score

    def space_selected(self, selected: int):
        """Function for if a space is selected"""
        self.selectedPos = selected
        self.optionSpaces[self.prevSelected]['image'] = self.boardParts['space_blank']
        self.optionSpaces[selected]['image'] = self.boardParts['space_selected']
        self.prevSelected = selected

    def color_selected(self, color: str):
        """Function for if a color is selected"""
        self.guess[self.selectedPos] = color
        self.optionColours[self.selectedPos]['image'] = self.colorImgs[color]
        self.space_selected(self.selectedPos + 1 if self.selectedPos < codeLength - 1 else 0)

    def confirm_choice(self):
        """Function for when the confirm button pressed or enter key pressed"""
        global timeShots
        if '' in self.guess: return  # Check guess is filled in
        self.boardData.insert(0, self.guess)
        self.scoreData.insert(0, self.get_score(self.guess.copy(), self.correctCode.copy()))
        if len(self.boardData) > shots:
            self.boardData.pop(-1); self.scoreData.pop(-1)
        for item in range(len(self.optionColours)):  # Set the current guess to blank
            self.optionColours[item].config(image=self.boardParts['color_blank'])
        self.insert_all()
        if mode != 'timed':  # Update label 
            timeShots += 1
            timerShotsLabel['text'] = f'Shots used: {timeShots}' + (f'/{shots}' if mode != 'memory' else '')
        self.guess = ['' for _ in range(codeLength)]  # Set the guess back to blank
        self.space_selected(0)
        if self.scoreData[0]['a'] == codeLength:  # If guess was correct
            self.finished(True)
        elif mode == 'classic' and len(self.boardData) == shots:
            self.finished(False)  # If they have used all their shots and not guessed the correct code

    def insert_all(self):
        """Procedure to update the board images with the new guess"""
        for line in range(len(list(filter(lambda l: l is not [], self.boardData)))):
            for piece in range(len(self.boardData[0])):
                self.historyColours[line][piece]['image'] = self.colorImgs[self.boardData[line][piece]]
            for red in range(self.scoreData[line]['a']):
                self.historyScores[line][red]['image'] = self.boardParts['mark_red']
            for yellow in range(self.scoreData[line]['b']):
                self.historyScores[line][self.scoreData[line]['a']+yellow]['image'] = self.boardParts['mark_yellow']
            for blank in range(codeLength-self.scoreData[line]['a']-self.scoreData[line]['b']):
                self.historyScores[line][self.scoreData[line]['a']+self.scoreData[line]['b']+blank]['image'] = self.boardParts['mark_blank']

    def finished(self, correct: bool):
        """Procedure that is called when the user guesses correctly or gives up"""
        global done
        def next():
            global window
            window.remove()
            window = Table(mainFrame, correct)
            window.create()

        [root.unbind(key) for key in root.bind()]  # Remove all key bindings
        if correct: database.add_score(userName, mode, difficulty, timeShots)
        timerShotsLabel.destroy()
        self.bar_finish.remove()
        done = True
        ttk.Label(self.infoFrame, image=messageImgs[f'you{"Won" if correct else "Lost"}'], padding=0).grid(column=0, row=4, pady=20)
        if not correct:  # Show the correct code
            ttk.Label(self.infoFrame, text='Correct Code:').grid(column=0, row=5, pady=(0, 10))
            self.correctFrame = ttk.Frame(self.infoFrame)
            self.correctFrame.grid(column=0, row=6)
            for i, c in enumerate(self.correctCode):
                ttk.Label(self.correctFrame, image=self.boardParts['space_blank'], padding=0).grid(row=0, column=i, sticky='NW')
                ttk.Label(self.correctFrame, image=self.colorImgs[c]).grid(column=i, row=0, sticky='NW', padx=self.spacing*2, pady=self.spacing*2)

        ttk.Button(self.infoFrame, text='View Scores', command=next).grid(column=0, row=7, pady=20)
        self.paletteFrame.destroy(); self.optionsFrame.destroy()

    def remove(self):
        """Remove this window"""
        self.bar_restart.remove(); self.bar_user.remove(); self.bar_finish.remove()
        clear(mainFrame); [root.unbind(key) for key in root.bind()]

class Table:
    """Window where you can view scores"""
    def __init__(self, frame: ttk.Frame, won: bool) -> None:
        self.frame = frame
        self.won = won
        self.bar_restart = Bar.Restart(); self.bar_restart.add(0)
        self.bar_user = Bar.User(); self.bar_user.add(1)

    def create(self):
        """Procedure to create this window"""
        root.state('normal')  # Set the window to not full screen mode
        tableFrame = ttk.Labelframe(self.frame, text='Scores', borderwidth=5, relief='solid')
        tableFrame.grid(column=1, row=0, sticky='N', padx=(0, 10))
        # Get all past scores from database with same settings as last game
        self.data = database.select(f"SELECT * FROM Score WHERE mode = ? AND difficulty = ?;", [mode, difficulty])
        # Get score from game just played, and sort by score ascending using insertion sort
        self.prev = self.data[-1] if self.won else ()
        self.data = AHsa.insertion_sort(self.data, lambda l: l[3], False)

        # Create table based on tkinter's treeview widget
        self.tree = ttk.Treeview(tableFrame, columns=('username', 'score', 'date', 'time'), show='headings', displaycolumns='#all', selectmode='none', height=10)
        for i, h in enumerate(('username', 'score', 'date', 'time')):
            self.tree.heading(i, text=h, anchor=tk.W)
            self.tree.column(i, stretch=True, width=400 if i == 0 else 200)
        self.tree.grid(row=0, column=0, sticky='nsew')
        self.tree.tag_configure('prev', background=darkBlue)

        # Create a scrollbar
        self.scrollbar = ttk.Scrollbar(tableFrame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscroll=self.scrollbar.set)

        # filers to choose a difficulty and mode
        filter_frame = ttk.Labelframe(self.frame, text='Filter', borderwidth=5, relief='solid')
        filter_frame.grid(column=0, row=0, padx=10, sticky='ns')
        ttk.Label(filter_frame, text='Difficulty', font=('QuinqueFive'), background=darkBlue, padding=10).grid(column=0, row=0, sticky='ew')
        diffs = ['easy', 'normal', 'hard', 'custom']
        self.diff = tk.StringVar(value=difficulty)
        for i, color in enumerate(('green', 'yellow', 'red', 'lightblue')):
            ttk.Radiobutton(filter_frame, value=diffs[i], variable=self.diff, text=diffs[i], style=f'{color}.TRadiobutton', command=self.addItems).grid(column=0, row=1+i, pady=(5, 0), sticky='W')
        ttk.Label(filter_frame, text='Mode', font=('QuinqueFive'), background=darkBlue, padding=10).grid(column=0, row=5, pady=(10, 0), sticky='ew')
        modes = ['classic', 'timed', 'memory']
        self.mode = tk.StringVar(value=mode)
        for i, color in enumerate(('yellow', 'red', 'lightblue')):
            ttk.Radiobutton(filter_frame, value=modes[i], variable=self.mode, text=modes[i], style=f'{color}.TRadiobutton', command=self.addItems).grid(column=0, row=6+i, pady=(5, 0), sticky='W')

        self.addItems()  # Add initial data to the table

    def addItems(self):
        """Add new items to the table when filters changed"""
        self.data = AHsa.insertion_sort(database.select(f"SELECT * FROM Score WHERE mode = ? AND difficulty = ?;", [self.mode.get(), self.diff.get()]), lambda l: l[3], False)
        [self.tree.delete(i) for i in self.tree.get_children()]
        for vs in self.data:  # Add data row by row
            self.tree.insert('', tk.END, values=vs[:1]+vs[3:], tags='prev' if vs == self.prev and self.won else '')

        self.scrollbar.grid_forget() if len(self.data) <= self.tree.cget('height') else self.scrollbar.grid(row=0, column=1, sticky='ns')  # Add scrollbar if needed

    def remove(self):
        """Remove this window"""
        self.bar_restart.remove(); self.bar_user.remove()
        clear(mainFrame)

class Bar(ttk.Frame):
    """Class for bar at bottom of window"""

    class Functions:
        def add(self: ttk.Label, col, **params):
            self.grid(column=col, row=0, sticky='ns', **params)
        def remove(self: ttk.Label):
            self.grid_forget()

    class Welcome(ttk.Label, Functions):
        """Welcome label on log in screen"""
        def __init__(self) -> None:
            super().__init__(bottomBar, text='Welcome to Mastermind!', font='QuinqueFive', background=darkBlue)

    class User(ttk.Menubutton, Functions):
        """User profile dropdown for after the user has logged in"""
        def __init__(self) -> None:
            super().__init__(bottomBar, text='User Profile', direction='above', style='dark.TButton', padding=9)
            self.userMenu = tk.Menu(self, tearoff=False)
            self.passChangeFrame = ttk.Frame(root)
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
        def __init__(self) -> None:
            super().__init__(bottomBar, text='Restart', style='dark.TButton', command=self.activate)
        def activate(self):
            global done, window
            self.remove(); done = True
            window.remove(); window = GameSettings(mainFrame); window.create()

    class Finish(ttk.Button, Functions):
        """Button on bottom bar to finish game"""
        def __init__(self) -> None:
            super().__init__(bottomBar, text='Finnish', style='dark.TButton', command=self.activate)
        def activate(self):
            global done, window
            self.remove(); done = True
            window.finished(False)


# Set constants for hex colors that are used throughout the program
bgBlue = '#2a2aff'; fgYellow = '#ffcc00'; darkBlue='#000080'
# Create main window
root = tk.Tk(); root.title('Mastermind'); root.config(bg=bgBlue)
root.columnconfigure(0, weight=1)
root.iconbitmap('Images/logo.ico')  # Set the window icon
messageImgs = load_images('Images/messages', 0.5)  # Load some images like the mastermind text logo

# Define the style settings to be used by each corresponding tkinter themed widget
mainStyle = ttk.Style(); mainStyle.theme_use('classic')
mainStyle.theme_settings('classic', {
    '.': {
        'configure': {'font': ('QuinqueFive', 20), 'foreground': fgYellow, 'background': bgBlue, 'borderwidth': 0, 'relief': 'solid', 'highlightthickness': 0}},
    'dark.TFrame': {
        'configure': {'background': darkBlue}},
    'Toolbutton': {
        'configure': {'background': bgBlue, 'activebackground': darkBlue, 'borderwidth': 0, 'padding': (20, 10, 20, 10)},
        'map': {'background': [('selected', darkBlue), ('active', darkBlue), ('!selected', bgBlue)]}},
    'TEntry': {
        'configure': {'fieldbackground': darkBlue, 'insertcolor': fgYellow, 'insertwidth': 5, 'highlightthickness': 5, 'selectbackground': fgYellow, 'selectforeground': darkBlue, 'selectborderwidth': 0},
        'map': {'highlightcolor': [('focus', fgYellow), ('!focus', '#000000')]}},
    'TButton': {
        'configure': {'shiftrelief': 5},
        'map': {'background': [('active', darkBlue)]}},
    'dark.TButton': {
        'configure': {'background': darkBlue, 'font': 'QuinqueFive'},
        'map': {'background': [('active', bgBlue)]}},
    'img.TButton': {
        'map': {'background': [('active', bgBlue)]}},
    'noShift.img.TButton': {
        'configure': {'shiftrelief': 0}},
    'warning.TLabel': {
        'configure': {'foreground': '#ff0000', 'font': ('QuinqueFive', 15)}},
    'TScale': {
        'configure': {'relief': 'flat', 'sliderrelief': 'flat', 'sliderlength': 40, 'troughcolor': fgYellow, 'sliderthickness': 30},
        'map': {'background': [('active', darkBlue), ('pressed', darkBlue)], 'sliderrelief': [('active', 'flat'), ('pressed', 'flat')]}},
    'Treeview': {
        'configure': {'rowheight': 40, 'font': ('QuinqueFive', 10), 'background': bgBlue, 'fieldbackground': bgBlue}},
    'Treeview.Heading':{
        'configure': {'background': darkBlue, 'padding': 10, 'font': 'QuinqueFive'},
        'map': {'background': [('active', darkBlue)]}},
    'TScrollbar': {
        'configure': {'troughcolor': darkBlue, 'background': fgYellow, 'arrowsize': 20},
        'map': {'background': [('active', fgYellow)]}},
    'TRadiobutton': {
        'map': {'background': [('active', bgBlue)]}}
})
mainStyle.element_create('custom.indicator', 'image', messageImgs['check_false'], ('selected', '!disabled', messageImgs['check_true']))
mainStyle.layout(
    'TRadiobutton',
    [('Radiobutton.padding',
    {'sticky': 'nswe',
     'children': [('custom.indicator', {'side': 'left', 'sticky': ''}),
                  ('Radiobutton.label', {'side': 'left', 'sticky': 'nsew'})]})])

for hex, color in zip(('#ff0000', fgYellow, '#00ff00', '#2ad4ff'), ('red', 'yellow', 'green', 'lightblue')):
    mainStyle.configure(f'{color}.Toolbutton', foreground=hex)
for hex, color in zip(('#ff0000', fgYellow, '#00ff00', '#2ad4ff'), ('red', 'yellow', 'green', 'lightblue')):
    mainStyle.configure(f'{color}.TRadiobutton', foreground=hex, font=('QuinqueFive', 10))

# Add logo at top of window and option bar at bottom
ttk.Label(root, image=messageImgs['mastermind']).grid(row=0, column=0, columnspan=2, pady=(0,10))
root.rowconfigure(9, weight=1)
bottomBar = Bar(root, style='dark.TFrame')
bottomBar.grid(row=10, column=0, columnspan=10, sticky='ew', pady=(10, 0))
bottomBar.columnconfigure(1, weight=1)

try:  # Start program in try statement so that the database connection will always be closed
    database = DBf.Database('gameData.db')
    database.create_tables()  # Create empty database if one doesn't already exist
    mainFrame = ttk.Frame(root)
    mainFrame.grid(row=1, column=0, sticky='n')
    # Go to log in / sign up window to start
    window = LoginSignup(mainFrame)
    window.create()
    windll.shcore.SetProcessDpiAwareness(1)  # Sets the window to the correct dpi scaling on the screen
    root.mainloop()  # Start tkinter
finally:
    database.finish()  # Close database connection
