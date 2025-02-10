import cv2
import numpy as np
from time import sleep

# Vehicle Detection Variables
largura_min = 80  # min width of rectangle.
altura_min = 80  # min height of rectangle
offset = 6  # allowed errors between the pixels.
pos_linha = 550  # position to counting line
delay = 60  # FPS of the video

detec = []
carros = 0  # count of cars

# Function to calculate the center of the vehicle:
def pega_centro(x, y, w, h):
    x1 = int(w / 2)
    y1 = int(h / 2)
    cx = x + x1
    cy = y + y1
    return cx, cy

# Traffic Signal Calculation Variables
min_time = 20  #minimum green signal time.
max_time = 60  # maximum green signal time

# Function to calculate the green time based on the total vehicle count
def calculate_green_time(vehicle_count):
    green_time = min_time + (vehicle_count * (max_time - min_time) // 20)
    return green_time

# Ask user for video file
video_path = input("Enter the path to the video file: ")
cap = cv2.VideoCapture(video_path)
subtracao = cv2.createBackgroundSubtractorMOG2()

while True:
    ret, frame1 = cap.read()
    if not ret:
        break  # Stop when video ends
    
    tempo = float(1 / delay)
    sleep(tempo)
    
    grey = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(grey, (3, 3), 5)
    img_sub = subtracao.apply(blur)
    dilat = cv2.dilate(img_sub, np.ones((5, 5)))
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    dilatada = cv2.morphologyEx(dilat, cv2.MORPH_CLOSE, kernel)
    dilatada = cv2.morphologyEx(dilatada, cv2.MORPH_CLOSE, kernel)
    contorno, h = cv2.findContours(dilatada, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    cv2.line(frame1, (25, pos_linha), (1200, pos_linha), (255, 127, 0), 3)
    
    for i, c in enumerate(contorno):
        (x, y, w, h) = cv2.boundingRect(c)
        validar_contorno = (w >= largura_min) and (h >= altura_min)
        if not validar_contorno:
            continue

        cv2.rectangle(frame1, (x, y), (x + w, y + h), (0, 255, 0), 2)
        centro = pega_centro(x, y, w, h)
        detec.append(centro)
        cv2.circle(frame1, centro, 4, (0, 0, 255), -1)

        for (x, y) in detec:
            if y < (pos_linha + offset) and y > (pos_linha - offset):
                carros += 1
                detec.remove((x, y))

    cv2.putText(frame1, f"VEHICLE COUNT: {carros}", (450, 70), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 5)

    cv2.imshow("Video Original", frame1)
    cv2.imshow("Detectar", dilatada)

    if cv2.waitKey(1) == 27:  # Press ESC to exit early
        break

# Calculate final green signal duration after video ends
green_time = calculate_green_time(carros)
print("\nFinal Vehicle Count:", carros)
print("Green signal duration for the road:", green_time, "seconds")

cv2.destroyAllWindows()
cap.release()