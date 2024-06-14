import cv2
# Importa il modulo OpenCV, comunemente utilizzato per il rilevamento e l'elaborazione delle immagini.

import numpy as np
# Importa il modulo NumPy, una libreria di calcolo scientifico, comunemente utilizzata per operazioni su array.

w, h = 360, 240
# Definisce le variabili 'w' e 'h' con valori specifici, rappresentando rispettivamente la larghezza e l'altezza desiderate per l'immagine.

fbRange = [6200, 6800]
# Definisce la lista 'fbRange' contenente due valori, rappresentando l'intervallo desiderato di area del volto per il movimento avanti/indietro.

pid = [0.4, 0.4, 0]
# Definisce la lista 'pid' contenente tre valori, che rappresentano i coefficienti PID (Proporzionale, Integrale, Derivativo) per il controllo della velocità.

pError = 0
# Inizializza la variabile 'pError' a 0, che rappresenta l'errore di posizione orizzontale precedente nel controllo PID.


# Trova il volto e lo rinquadra
def findFace(img):

    # Carica il classificatore pre-addestrato per il rilevamento dei volti
    faceCascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

    # Converte il frame in scala di grigi
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Utilizza il metodo detectMultiScale del classificatore a cascata per rilevare volti nell'immagine.
    faces = faceCascade.detectMultiScale(
        imgGray,  # L'immagine in scala di grigi in cui effettuare il rilevamento dei volti.
        1.2,  # scaleFactor: il fattore di ridimensionamento ad ogni scala successiva dell'immagine.
        8  # minNeighbors: il numero di rettangoli vicini richiesti per mantenere l'area come volto.
    )

    # Lista per salvare coordinate del centro del volto
    myFaceListC = []

    # Lista per salvare i valori delle aree del volto
    myFaceListArea = []

    # Disegna rettangoli attorno ai volti rilevati
    for (x, y, w, h) in faces:

        # Disegna un rettangolo rosso attorno al viso
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)

        # Calcola il centro del rettangolo
        cx = x + w // 2

        cy = y + h // 2

        # Calcola l'area del rettangolo
        area = w * h

        # Disegna un pallino verde al centro del volto
        cv2.circle(img, (cx, cy), 5, (0, 255, 0), cv2.FILLED)

        # Aggiunge le coordinate del centro del volto alla lista myFaceListC
        myFaceListC.append([cx, cy])

        # Aggiunge l'area del volto alla lista myFaceListArea
        myFaceListArea.append(area)

    # Verifica se la lista delle aree dei volti rilevati non è vuota
    if len(myFaceListArea) != 0:

        # Trova l'indice dell'area piu' grande nella lista delle aree dei volti rilevati
        i = myFaceListArea.index(max(myFaceListArea))

        # Restituisce l'immagine originale e una lista contenente:
        # - Le coordinate del centro del volto con l'area piu' grande
        # - L'area del volto con l'area piu' grande
        return img, [myFaceListC[i], myFaceListArea[i]]

    else:

        # Se non ci sono volti rilevati, restituisce l'immagine originale e:
        # - Le coordinate [0, 0] (indicando che non è stato rilevato nessun volto)
        # - Un'area di 0
        return img, [[0, 0], 0]

# Insegue il volto
def trackFace(info, w, pid, pError):
    # Definisce la funzione trackFace che accetta quattro parametri:
    # info: lista contenente le coordinate del centro del volto e l'area del volto rilevato.
    # w: larghezza dell'immagine (utilizzata per calcolare l'errore di posizione orizzontale).
    # pid: lista contenente i coefficienti PID [P, I, D] per il controllo della velocità.
    # pError: l'errore di posizione orizzontale precedente (utilizzato nel controllo PID).

    area = info[1]
    # Estrae l'area del volto rilevato dalla lista info.

    x, y = info[0]
    # Estrae le coordinate x e y del centro del volto rilevato dalla lista info.

    fb = 0
    # Inizializza la variabile fb (forward/backward) a 0, che rappresenta il movimento avanti/indietro.

    error = x - w // 2
    # Calcola l'errore di posizione orizzontale rispetto al centro dell'immagine.
    # w // 2 è la metà della larghezza dell'immagine, rappresentando il centro orizzontale.

    speed = pid[0] * error + pid[1] * (error - pError)
    # Calcola la velocità di rotazione utilizzando un controllo proporzionale-integrativo (PI)
    # pid[0] è il coefficiente proporzionale (P) e pid[1] è il coefficiente integrativo (I).

    speed = int(np.clip(speed, -100, 100))
    # Limita la velocità calcolata tra -100 e 100 per evitare valori eccessivi.
    # np.clip() assicura che la velocità rimanga entro questi limiti.

    if area > fbRange[0] and area < fbRange[1]:
        fb = 0
        # Se l'area del volto è entro l'intervallo desiderato (fbRange), non c'è movimento avanti/indietro.

    elif area > fbRange[1]:
        fb = -20
        # Se l'area del volto è maggiore dell'intervallo massimo (troppo vicino), il movimento è indietro (fb = -20).

    elif area < fbRange[0] and area != 0:
        fb = 20
    # Se l'area del volto è minore dell'intervallo minimo (troppo lontano) e non è zero, il movimento è avanti (fb = 20).

    if x == 0:
        speed = 0
        error = 0
        # Se x è 0 (nessun volto rilevato), la velocità e l'errore sono impostati a 0.

    print(speed, fb)
    # Stampa la velocità di rotazione (speed) e il movimento avanti/indietro (fb).

    return error
    # Restituisce l'errore di posizione orizzontale attuale per essere utilizzato nel prossimo ciclo.


# Avvia la cattura video dalla webcam
cap = cv2.VideoCapture(0)

while True:

    # Leggi un frame dalla webcam
    _, img = cap.read()

    # Ridimensiona l'immagine 'img' alla larghezza 'w' e all'altezza 'h'.
    img = cv2.resize(img, (w, h))

    # Trova il volto nell'immagine ridimensionata utilizzando la funzione 'findFace'.
    # La funzione 'findFace' restituisce l'immagine elaborata e le informazioni sul volto rilevato.
    img, info = findFace(img)

    # Traccia il volto rilevato utilizzando la funzione 'trackFace'.
    # La funzione 'trackFace' prende le informazioni sul volto 'info', la larghezza dell'immagine 'w',
    # i parametri PID 'pid' e l'errore precedente 'pError', restituendo l'errore attuale.
    pError = trackFace(info, w, pid, pError)

    #print("Center", info[0], "Area", info[1])

    # Mostra il frame con i volti rilevati
    cv2.imshow("Output", img)

    # Esce dal ciclo se viene premuto il tasto 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):

      break

 # Rilascia la cattura video e chiudi tutte le finestre
cap.release()
cv2.destroyAllWindows()