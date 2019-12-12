import PySimpleGUI as sg


sg.change_look_and_feel('Dark Blue 3')

# class hockeyCard:


layout = [
    [sg.Text('Name'), sg.InputText()],[sg.Text('Team'), sg.InputText()],
    [sg.Checkbox('Rookie'), sg.Checkbox('Memorobilia'), sg.Checkbox('Autograph'),
     sg.Checkbox('S/N')],
    [sg.Text('Run Number'), sg.InputText()],[sg.Text('Year'), sg.InputText(),],
    [sg.Submit(), sg.Cancel()],
    [sg.Text('Price'),sg.Output(size=(10,10), pad=(5, 5))]
]

window = sg.Window('Hockey_Card', layout)

while True:                             # The Event Loop
    event, values = window.read()
    print(event, values) #debug
    if event in (None, 'Exit', 'Cancel'):
        break



        """name, team, rookie Y/N, memorabilia Y/N, autographed Y/N, serial Y/N and then the ML model outputs the price variable. Is that about right @Michael Middleton ? (edited) 
Michael Middleton 7:41 PM
Yea and now the run number qnd year as well"""