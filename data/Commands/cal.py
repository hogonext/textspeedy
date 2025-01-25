# open calculator by Python

import pyautogui
import time

# Adjust this if the calculator shortcut is in a different location
calculator_path = 'C:\\Windows\\System32\\calc.exe' 

# Open the Start menu (assuming Windows)
pyautogui.press('win') 

# Type 'calculator' to search
pyautogui.typewrite('calculator') 

# Small delay to allow the search to complete
time.sleep(0.5)  

# Press Enter to open the first search result
pyautogui.press('enter')