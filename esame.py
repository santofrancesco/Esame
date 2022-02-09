class ExamException(Exception):
    pass

class CSVTimeSeriesFile:

    def __init__(self, name):
        self.name = name

    def get_data(self):
        #controllo la correttezza del nome del file
        if ( (self.name == '') or (self.name == None) ):
            raise ExamException('Errore: nessun file inserito.')
        if ( type(self.name) != str ):
            raise ExamException('Errore: nome del file inserito non valido.')

        #controllo duplicati
        lista_linee = []
        
        try:
            with open(self.name) as y:
                for line in y:
                    lista_linee.append(line)
       
                misuratore = 0
                for line in y:   
                    for i in lista_linee:
                        if (i == line):
                            misuratore+=1
                    if(misuratore >= 2):
                        raise ExamException('Errore: la linea {0} è presente più volte nel file.'.format(line))
                    misuratore=0
        except FileNotFoundError:
            raise ExamException('Errore: file non trovato.')
        
        lista1 = []
        with open(self.name) as x:
            for line in x:
                lista2 = line.strip().split(',')
                #skippo la prima linea
                if (lista2[0] == 'date'):
                    continue
                              
                #se per un mese non ci sono info, metto 0
                #converto prima in float, poi in int, per sicurezza
                #se i dati non sono divisi in due colonne, o se in una riga c'è solo un'informazione senza la virgola dopo, faccio raise IndexError
                try:
                    if (lista2[1] != ''):
                        #ValueError in caso che uno dei dati non è di tipo numerico
                        try:
                            lista2[1] = float(lista2[1])
                            lista2[1] = int(lista2[1])
                        except ValueError:
                            #raise ExamException('Errore: valori inseriti non validi.')
                            lista2[1] = 0    
                except IndexError:
                    raise ExamException('Errore: i dati non sono divisi in due colonne.')

                if (lista2[1] == ''):
                    lista2[1] = 0
                
                lista3 = []
                lista3.append(lista2[0])
                lista3.append(lista2[1])

                lista1.append(lista3)

        #### CODICE SOLO PER CONTROLLARE L’ORDINE DELLE DATE ####
        anni = []
        #prendo solo gli anni dal file e creo una lista anni
        with open(self.name) as x:
            for line in x:
                lista_linea = line.strip().split(',')
                lista_linea[0] = lista_linea[0].split('-')
                #skippo la prima linea
                if (lista_linea[0][0] == 'date'):
                    continue
                #se un elemento non è di tipo numerico alzo un'eccezione
                try:
                    lista_linea[0][0] = int(lista_linea[0][0])
                except ValueError:
                    #raise ExamException('Errore: i valori inseriti devono essere di tipo numerico.')
                    continue

                anni.append(lista_linea[0][0])
        #scorro gli elementi della lista anni e controllo l'ordine
        anno_precedente = 0
        for item in anni:
            if (item<anno_precedente):
                raise ExamException('Errore: le date non sono in ordine. L\'anno {0} viene dopo il {1}.'.format(anno_precedente, item))
            anno_precedente = item

        return lista1

#creo un oggetto, time_series_file, e poi creo time_series
time_series_file = CSVTimeSeriesFile(name='data.csv')
#chiamo get_data
time_series = time_series_file.get_data()


def compute_avg_monthly_difference(time_series, first_year, last_year):
    #controllo se first_year e last_year sono delle stringhe
    if ((first_year == None) or (last_year == None)):
        raise ExamException('Errore: first_year e/o last_year non inseriti.')
    
    if (type(first_year) != str):
        raise ExamException('Errore: first_year deve essere una stringa.')
    if (type(last_year) != str):
        raise ExamException('Errore: last_year deve essere una stringa.')

    #cambio gli anni da stringhe a int
    first_year = int(first_year)
    last_year = int(last_year)
    
    #se first_year è maggiore di last_year, inverto
    if (first_year>last_year):
        variabile_appoggio = first_year
        first_year = last_year
        last_year = variabile_appoggio
    #differenza tra last_year e first_year per calcolare la media più tardi
    differenza_anni = last_year - first_year

    lista_di_liste = []
    with open(time_series_file.name) as x:

        for line in x:
                #divido gli elementi per ',' e per '-'
                lista_raw = line.strip().split(',')
                lista_raw[0] = lista_raw[0].split('-')
                if (lista_raw[0][0] == 'date'):
                    continue              

                if (lista_raw[1] != ''):
                    try:
                        lista_raw[1] = float(lista_raw[1])
                        lista_raw[1] = int(lista_raw[1])
                    except ValueError:
                        #raise ExamException('Errore: i valori inseriti devono essere di tipo numerico.')
                        lista_raw[1] = 0
                    #se un numero è negativo lo moltiplico per -1
                    if (lista_raw[1]<0):
                        lista_raw[1] = lista_raw[1]*(-1)
                
                if (lista_raw[1] == ''):
                    lista_raw[1] = 0
                try:
                    #converto l'anno in int se possibile
                    lista_raw[0][0] = int(lista_raw[0][0])
                except:
                    continue
                
                #aggiungo solo gli elementi che mi servono(anno e passengers)
                lista_raffinata = []
                lista_raffinata.append(lista_raw[0][0])
                lista_raffinata.append(lista_raw[1])
                #aggiungo la lista con gli elementi necessari alla lista finale
                lista_di_liste.append(lista_raffinata)

        #controllo se first_year e/o last_year sono presenti nel file csv/txt
        flag_esistenza=0
        lista_anni = []
        for i in range( 0,int((len(lista_di_liste)/12)) ):
            lista_anni.append(lista_di_liste[flag_esistenza][0])
            flag_esistenza+=12
        if ((first_year not in lista_anni) and (last_year not in lista_anni)):
            raise ExamException('Errore: first_year e last_year non sono presenti nel file csv/txt inserito.')
        elif (first_year not in lista_anni):
            raise ExamException('Errore: first_year non presente nel file csv/txt inserito.')
        elif (last_year not in lista_anni):
            raise ExamException('Errore: last_year non presente nel file csv/txt inserito.')
        #controllo se gli anni sono in ordine crescente
        anno_prima = 0
        for item in lista_anni:
            if (item<anno_prima):
                raise ExamException('Errore: le date non sono in ordine.')
            anno_prima = item

        
    #creo una lista d'appoggio e una matrice per i mesi
    lista_scarsa = []
    matrice_mesi = [ [],[],[],[],[],[],[],[],[],[],[],[] ]
    #scorro gli elementi finché non trovo l'elemento corrispondente a first_year, per poi iniziare da quello
    contatore_elementi = 0
    for item in lista_di_liste:
        if(lista_di_liste[contatore_elementi][0]==first_year):
            break
        else:
            contatore_elementi+=12

    for i in range(first_year, last_year+1):
        #if(lista_di_liste[contatore_elementi][0]==i):
            for j in range(0, 12):
                lista_scarsa.append(lista_di_liste[contatore_elementi][1])
                contatore_elementi+=1
    #creo la matrice, con 12 liste(mesi), ogni lista contiene gli elementi per quel mese
    contatore_mesi = 0  
    for item in lista_scarsa:
        matrice_mesi[contatore_mesi].append(item)
        if(contatore_mesi==11):
            contatore_mesi=0
        else:
            contatore_mesi+=1
    #calcolo l'incremento tra i mesi e aggiungo i risultati uno per uno all'ultima lista, che poi returno
    incremento_medio = [] 
    contatore_matrice = 0   
    while(contatore_matrice<12):
        #conto gli zeri per un mese, se solo un elemento non è zero, allora appendo come incremento 0, in caso contrario calcolo l'incremento medio e appendo
        flag_zeri=0
        for item in matrice_mesi[contatore_matrice]:
            if(item != 0):
                flag_zeri+=1
            
        if (flag_zeri < 2):
            incremento_medio.append(0)
        else:
            incremento = 0
            incremento = (matrice_mesi[contatore_matrice][-1]-matrice_mesi[contatore_matrice][0])/differenza_anni 
            incremento_medio.append(incremento)
        
        contatore_matrice+=1
                
    return incremento_medio

#try:
#    avg_difference = compute_avg_monthly_difference(time_series, '1949', '1951')
#    print(avg_difference)
#except TypeError:
#    raise ExamException('Errore: non sono stati inseriti tutti i dati necessari.')