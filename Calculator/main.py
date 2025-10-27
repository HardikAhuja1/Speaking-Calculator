import pyttsx3
import tkinter as tk
from tkinter import ttk
import threading
import queue

# Initialize text-to-speech engine in a dedicated thread
speech_queue = queue.Queue()
speaking = True  # toggle speech on/off
engine = None


def speech_worker():
    """Dedicated thread for speech - uses iterate() instead of runAndWait()"""
    global engine
    engine = pyttsx3.init()
    engine.setProperty("rate", 170)

    while True:
        text = speech_queue.get()
        if text is None:
            break

        if speaking and text.strip():
            engine.say(str(text))
            # Use iterate loop instead of runAndWait()
            engine.startLoop(False)
            engine.iterate()
            engine.endLoop()

        speech_queue.task_done()


# Start the speech worker thread
threading.Thread(target=speech_worker, daemon=True).start()


def speak(text):
    """Queue text for speech - clear old queue for fast typing"""
    if text.strip():
        # Clear any pending speech
        while not speech_queue.empty():
            try:
                speech_queue.get_nowait()
                speech_queue.task_done()
            except queue.Empty:
                break
        # Add new speech
        speech_queue.put(str(text))


def handle_button_click(clicked_button_text):
    current_text = result_var.get()

    if clicked_button_text == "=":
        try:
            # Replace custom symbols with Python operators
            expression = current_text.replace("÷", "/").replace("×", "*")
            result = eval(expression)

            # Check if the result is a whole number
            if isinstance(result, float) and result.is_integer():
                result = int(result)

            result_var.set(result)
            speak(f"The answer is {result}")
        except Exception:
            result_var.set("Error")
            speak("Error")
    elif clicked_button_text == "C":
        result_var.set("")
        speak("Clear")
    elif clicked_button_text == "🔇":
        global speaking
        speaking = not speaking
        speak("Voice muted" if not speaking else "Voice enabled")
    elif clicked_button_text == "%":
        # Convert the current number to a decimal by dividing it by 100
        try:
            current_number = float(current_text)
            result_var.set(current_number / 100)
            speak(f"{current_number} percent is {current_number/100}")
        except ValueError:
            result_var.set("Error")
            speak("Error")
    elif clicked_button_text == "±":
        # Convert the current number to its negative
        try:
            current_number = float(current_text)
            result_var.set(-current_number)
            speak("negative" if current_number > 0 else "positive")
        except ValueError:
            result_var.set("Error")
            speak("Error")
    else:
        result_var.set(current_text + clicked_button_text)
        words = {
            "×": "multiply",
            "÷": "divide",
            "+": "plus",
            "-": "minus",
            "=": "equals",
            "C": "clear"
        }
        speak(words.get(clicked_button_text, clicked_button_text))


# Create the main window
root = tk.Tk()
root.title("Calculate Kal le ho, kalo beta kalo")

# Entry widget to display the result with larger font size
result_var = tk.StringVar()
result_entry = ttk.Entry(
    root,
    textvariable=result_var,
    font=("Helvetica", 24),
    justify="right"
)
result_entry.grid(row=0, column=0, columnspan=4,
                  sticky="nsew", padx=10, pady=15, ipady=10)

# Button layout
buttons = [
    ("C", 1, 0), ("±", 1, 1), ("%", 1, 2), ("÷", 1, 3),
    ("7", 2, 0), ("8", 2, 1), ("9", 2, 2), ("×", 2, 3),
    ("4", 3, 0), ("5", 3, 1), ("6", 3, 2), ("-", 3, 3),
    ("1", 4, 0), ("2", 4, 1), ("3", 4, 2), ("+", 4, 3),
    ("0", 5, 0, 2), (".", 5, 2), ("=", 5, 3), ("🔇", 6, 0)
]

# Configure style for theme
style = ttk.Style()
style.theme_use('clam')
style.configure("TButton", font=("Segoe UI", 16, "bold"), width=10, height=4)

# Create buttons and add them to the grid
for button_info in buttons:
    button_text, row, col = button_info[:3]
    colspan = button_info[3] if len(button_info) > 3 else 1
    button = ttk.Button(root, text=button_text,
                        command=lambda text=button_text: handle_button_click(
                            text),
                        style="TButton")
    button.grid(row=row, column=col, columnspan=colspan,
                sticky="nsew", ipadx=10, ipady=4, padx=5, pady=5)

# Configure row and column weights so that they expand proportionally
for i in range(7):
    root.grid_rowconfigure(i, weight=1)

for i in range(4):
    root.grid_columnconfigure(i, weight=1)

# Set the window size to a 9:16 ratio
width = 500
height = 700
root.geometry(f"{width}x{height}")

# Make the window non-resizable
root.resizable(False, False)

# Keyboard control
root.bind("<Return>", lambda event: handle_button_click("="))
root.bind("<BackSpace>", lambda event: handle_button_click("C"))

# Run the main loop
root.mainloop()
