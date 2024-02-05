import tkinter as tk
from tkinter import ttk
from random import choice, shuffle
from Game.uml_classes.Bar import Bar

class Game:
    """Window where main game is played"""
    def __init__(self, frame: ttk.Frame, duplicates: bool, color_blind):
        self.frame = frame
        self.duplicates = duplicates; self.colorBlind = color_blind
        self.selectedPos = 0; self.prevSelected = 0
        self.guess = ['' for _ in range(codeLength)]
        self.boardData = []; self.scoreData = []
        # Configure bottom bar
        self.bar_restart = Bar.Restart(); self.bar_restart.add()
        self.bar_user = Bar.User(); self.bar_user.add()
        self.bar_finish = Bar.Finish(); self.bar_finish.add()

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