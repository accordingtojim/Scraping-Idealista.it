import json
import sqlite3
from datetime import datetime

def import_json_to_sqlite(json_file, sqlite_db):
    """
    Importa i dati da un file JSON in un database SQLite.
    Se l'annuncio esiste, aggiorna i dettagli e registra la variazione di prezzo.
    Se l'annuncio non esiste, lo inserisce insieme al prezzo iniziale.

    :param json_file: Percorso al file JSON.
    :param sqlite_db: Percorso al file del database SQLite.
    """
    # Carica i dati dal file JSON
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Connessione al database SQLite (verrà creato se non esiste)
    conn = sqlite3.connect(sqlite_db)
    cursor = conn.cursor()

    # Creazione delle tabelle con i campi corrispondenti al JSON
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS properties (
        id_casa TEXT PRIMARY KEY,
        indirizzo TEXT,
        zona TEXT,
        comune TEXT,
        prezzo TEXT,
        prezzo_al_m2 TEXT,
        superficie_in_mq TEXT,
        url TEXT,
        directory TEXT,
        data_creazione TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS cronologia_prezzi (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_casa TEXT,
        prezzo TEXT,
        data_modifica TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (id_casa) REFERENCES properties(id_casa)
    )
    ''')

    # Inserimento o aggiornamento dei dati nel database
    for item in data:
        id_casa = item.get('Id_casa')
        nuovo_prezzo = item.get('Prezzo')

        # Inserisci o aggiorna l'annuncio
        cursor.execute('''
        INSERT INTO properties (
            id_casa, indirizzo, zona, comune, prezzo,
            prezzo_al_m2, superficie_in_mq, url, directory
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id_casa) DO UPDATE SET
            indirizzo=excluded.indirizzo,
            zona=excluded.zona,
            comune=excluded.comune,
            prezzo=excluded.prezzo,
            prezzo_al_m2=excluded.prezzo_al_m2,
            superficie_in_mq=excluded.superficie_in_mq,
            url=excluded.url,
            directory=excluded.directory
        ''', (
            id_casa,
            item.get('Indirizzo'),
            item.get('Zona'),
            item.get('Comune'),
            nuovo_prezzo,
            item.get('Prezzo al m²'),
            item.get('Superficie in mq'),
            item.get('Url'),
            item.get('Directory')
        ))

        # Controlla l'ultimo prezzo registrato
        cursor.execute('''
        SELECT prezzo FROM cronologia_prezzi
        WHERE id_casa = ?
        ORDER BY data_modifica DESC
        LIMIT 1
        ''', (id_casa,))
        ultimo_prezzo = cursor.fetchone()

        # Se il prezzo è cambiato, registra la variazione
        if ultimo_prezzo is None or ultimo_prezzo[0] != nuovo_prezzo:
            cursor.execute('''
            INSERT INTO cronologia_prezzi (id_casa, prezzo, data_modifica)
            VALUES (?, ?, ?)
            ''', (
                id_casa,
                nuovo_prezzo,
                datetime.now()
            ))

    # Salva (commit) le modifiche e chiudi la connessione
    conn.commit()
    conn.close()

    print(f'Dati importati e aggiornati con successo in {sqlite_db}')
