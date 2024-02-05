import tkinter as tk
from tkinter import ttk
from Game.uml_classes.Bar import Bar
from Game.Modules import AHstandardAlgorythims as AHsa

class Table:
    """Window where you can view scores"""
    def __init__(self, frame: ttk.Frame, won: bool) -> None:
        self.frame = frame
        self.won = won
        self.bar_restart = Bar.Restart(); self.bar_restart.add()
        self.bar_user = Bar.User(); self.bar_user.add()

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