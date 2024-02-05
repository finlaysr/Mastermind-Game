import tkinter as tk
from tkinter import ttk
from Game.uml_classes.Bar import Bar

class GameSettings:
    """Window where game settings are chosen"""
    def __init__(self, frame: ttk.Frame) -> None:
        self.frame = frame
        self.bar_user = Bar.User()  # Add user options dropdown to bottom bar
        self.bar_user.add()
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