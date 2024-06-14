% Definisce la larghezza e l'altezza dell'immagine desiderata
w = 360;
h = 240;

% Definisce l'intervallo desiderato di area del volto per il movimento avanti/indietro
fbRange = [6200, 6800];

% Definisce i coefficienti PID (Proporzionale, Integrale, Derivativo) per il controllo della velocità
pid = [0.4, 0.4, 0];

% Inizializza l'errore di posizione orizzontale precedente nel controllo PID
pError = 0;

% Carica il classificatore pre-addestrato per il rilevamento dei volti
faceCascade = vision.CascadeObjectDetector('FrontalFaceCART');

% Funzione per trovare il volto e rinquadrarlo
function [img, faceInfo] = findFace(img, faceCascade)
% Restituisce l'immagine con i volti evidenziati e le informazioni sul volto (coordinate del centro e area)
% img: Immagine in cui cercare il volto
% faceCascade: Classificatore a cascata pre-addestrato per il rilevamento dei volti

    % Converte l'immagine in scala di grigi
    imgGray = rgb2gray(img);

    % Utilizza il classificatore a cascata per rilevare volti nell'immagine
    bbox = step(faceCascade, imgGray);

    % Lista per salvare coordinate del centro del volto
    myFaceListC = [];

    % Lista per salvare i valori delle aree del volto
    myFaceListArea = [];

    % Disegna rettangoli attorno ai volti rilevati
    for i = 1:size(bbox, 1)
        x = bbox(i, 1);
        y = bbox(i, 2);
        w = bbox(i, 3);
        h = bbox(i, 4);

        % Disegna un rettangolo rosso attorno al viso
        img = insertShape(img, 'Rectangle', bbox(i, :), 'Color', 'red', 'LineWidth', 2);

        % Calcola il centro del rettangolo
        cx = x + w / 2;
        cy = y + h / 2;

        % Calcola l'area del rettangolo
        area = w * h;

        % Disegna un pallino verde al centro del volto
        img = insertShape(img, 'FilledCircle', [cx, cy, 5], 'Color', 'green');

        % Aggiunge le coordinate del centro del volto alla lista
        myFaceListC = [myFaceListC; [cx, cy]];

        % Aggiunge l'area del volto alla lista
        myFaceListArea = [myFaceListArea; area];
    end

    % Verifica se la lista delle aree dei volti rilevati non è vuota
    if ~isempty(myFaceListArea)
        % Trova l'indice dell'area piu' grande nella lista delle aree dei volti rilevati
        [~, i] = max(myFaceListArea);

        % Restituisce l'immagine originale e una lista contenente le coordinate del centro del volto e l'area del volto con l'area piu' grande
        faceInfo = {myFaceListC(i, :), myFaceListArea(i)};
    else
        % Se non ci sono volti rilevati, restituisce l'immagine originale e coordinate e area vuote
        faceInfo = {[0, 0], 0};
    end
end

% Funzione per inseguire il volto
function error = trackFace(info, w, pid, pError, fbRange)
% Restituisce l'errore orizzontale attuale per il controllo PID
% parrotObj: Oggetto drone
% info: Informazioni sul volto rilevato (coordinate del centro e area)
% w: Larghezza dell'immagine
% pid: Coefficienti PID per il controllo della velocità
% pError: Errore di posizione orizzontale precedente
% fbRange: Intervallo desiderato di area del volto per il movimento avanti/indietro


  % Estrae l'area del volto rilevato dalla lista info.
    area = info{2};

  % Estrae le coordinate x e y del centro del volto rilevato dalla lista info.
    x = info{1}(1);
    y = info{1}(2);

  % Inizializza la variabile fb (forward/backward) a 0, che rappresenta il movimento avanti/indietro.
    fb = 0;

% Calcola l'errore di posizione orizzontale rispetto al centro dell'immagine.
%  w // 2 è la metà della larghezza dell'immagine, rappresentando il centro orizzontale.
    error = x - w / 2;

% Calcola la velocità di rotazione utilizzando un controllo proporzionale-integrativo (PI)
% pid[0] è il coefficiente proporzionale (P) e pid[1] è il coefficiente integrativo (I).
    speed = pid(1) * error + pid(2) * (error - pError);

% Limita la velocità calcolata tra -100 e 100 per evitare valori eccessivi
% e si assicura che speed sia un intero 
    speed = round(min(max(speed, -100), 100));

% Se l'area del volto è entro l'intervallo desiderato (fbRange), non c'è movimento avanti/indietro.
    if area > fbRange(1) && area < fbRange(2)
        fb = 0;
% Se l'area del volto è maggiore dell'intervallo massimo (troppo vicino), il movimento è indietro (fb = -20).
    elseif area > fbRange(2)
        fb = -20;
% Se l'area del volto è minore dell'intervallo minimo (troppo lontano) e non è zero, il movimento è avanti (fb = 20).
    elseif area < fbRange(1) && area ~= 0
        fb = 20;
    end
% Se x è 0 (nessun volto rilevato), la velocità e l'errore sono impostati a 0.
    if x == 0
        speed = 0;
        error = 0;
    end

% Stampa la velocità di rotazione (speed) e il movimento avanti/indietro (fb).
    fprintf('Speed: %d, fb: %d, area: %d\n', speed, fb, area);
end

% Avvia la cattura video dalla webcam
cam = webcam;

while true
    % Leggi un frame dalla webcam
    img = snapshot(cam);

    % Ridimensiona l'immagine alla larghezza 'w' e all'altezza 'h'
    img = imresize(img, [h, w]);

    % Trova il volto nell'immagine ridimensionata
    [img, info] = findFace(img, faceCascade);

    % Traccia il volto rilevato
    pError = trackFace(info, w, pid, pError, fbRange);

    % Mostra il frame con i volti rilevati
    imshow(img);

    % Esce dal ciclo se viene premuto il tasto 'q'
    if strcmp(get(gcf, 'CurrentCharacter'), 'q')
        break;
    end
    pause(0.01);
end

% Rilascia la webcam
clear cam;
