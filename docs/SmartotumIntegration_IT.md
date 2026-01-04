## DOCUMENTAZIONE INTEGRAZIONE CON SMARTOTUM - ALBERTO HUGONIN (Vers 0.5) 

### FUNZIONAMENTO SISTEMA DOMOTICA SMARTOTUM

- Utente può interfacciarsi con il sistema attraverso questa API:
    - `POST https://api.smartotum.com/auth/signin`: effettua il log-in con nome utente e password.
    - `GET https://api.smartotum.com/service/systems/?offset=0&limit=100`: passando il suo access token riceve tutte le informazioni dei sistemi di cui è responsabile e che è possibile controllare compreso l'ID univoco. 
    - `GET https://fixissuesbpoyqq.pods.smartotum.com/.dht/get_all`: fornendo l'ID univoco del sistema (POD interno alla casa) a cui intende collegarsi ad es `fixissuesbpoyqq` restituisce tutti i topic della casa che includono: dispositivi, applicazioni, regole, camere, utenti, pianificazione orari, impostazioni e molto altro.
    - È possibile ottenere elementi dello stesso topic sostituendo il parametro `get_all` con  `topic_name/<topic_scelto>`.
- Segue una lista non esaustiva dei topic presenti:
    - Ambienti/stanze: **domo_room**
    - App della casa: **domo_app**
    - Regole/policy: **privacy_rule**
    - Utenti/metadati: **domo_user**
    - Gateway/diagnostica: gateway (presente anche nei dispositivi smartotum)
    - Pianificazione/Orari: domo_schedule, domo_temperature_scheduling
    - Impostazioni casa: domo_house_mode, domo_house_temperature_mode, domo_room_temperature_setting
    - Connessioni: domo_actuator_connection
    - Notifiche/log/analytics: domo_notifications, domo_last_notification, domo_ui_views_visits
    - Abbiamo inoltre una serie di topic che rappresentano i **dispositivi oggetto delle regole** che andremo a creare in seguito: 
        - domo_light
        - domo_light_dimmable
        - domo_rgbw_light
        - domo_switch
        - domo_button
        - domo_bistable_button
        - domo_window_sensor
        - domo_siren
        - domo_ble_thermometer
        - domo_ble_valve
        - domo_ble_contact
        - domo_roller_shutter
        - domo_ac_unit
        - domo_floor_valve
        - domo_camera
    - Ciascun topic può presentare 1 o più entità / dispositivi, ad esempio per il topic domo_light sono presenti tutte le luci installate nella Smarthome


### PRIVACY DASHBOARD -> SMARTOTUM

- La privacy dashboard recupera informazioni dal sistema Smartotum e le riorganizza per renderle più facilmente utilizzabili per i seguenti scopi:
    -  **Creazione e Gestione delle regole** per i dispositivi:
        - per i dispositivi compatibili di una smart home è possibile generare delle regole che verranno poi applicate al sistema di domotica ad es: 
          - non si possono accendere determinate luci dalle 8 del mattino alle 20 di sera
          - le telecamere devono essere disattivate dalle 14:00 alle 20:00
    -   **Gestione delle applicazioni**:
        - la smart home può avere delle applicazioni installate che utilizzano e elaborano i dati dell'utente e che quindi devono rispondere al GDPR
        - Il flusso segue solo in una direzione: applicazioni della casa vengono automaticamente importate nella Privacy Dashboard
        - eventuali applicazioni create a livello della privacy dashboard per il momento non possono essere legate ad una casa

- Il **Data Subject** è l'utente dell'applicazione che vuole gestire i suoi dati personali in relazione alla sua smart home personale o di terzi di cui ha accesso:
    - per potersi registrare e accedere alla privacy dashboard deve essere possessore di un account Smartotum
    - Durante la registrazione vengono chieste informazioni base e l'autenticazione al suo account Smartotum
    - In seguito al log-in il client lanciando l'endpoint di refresh vengono recuperate e salvate / sincronizzate le seguenti informazioni dal sistema Smartotum:
        - tutte le case di cui l'utente ha accesso che comprende recupero delle case e assegnazione di ciascuna casa all'utente
        - per ciascuna casa tutte le sue stanze e viene creata anche una stanza fittizia non presente nel sistema smartotum per raggruppare tutti i dispositivi senza una stanza assegnata
        - per ciascuna casa si recuperano tutti i dispositivi compatibili secondo una allow list nel file env chiamata SMARTOTUM_DEVICE_TOPICS e si assegna ciascun dispositivo alla sua stanza che si collega di conseguenza ad una determinata casa
        - per il momento viene recuperata la lista delle applicazioni da un file JSON ma il codice presenta già una buona parte di logica per il recupero da Smartotum. Si può in seguito  assegnare la app ad un Data Controller che potrà poi assegnarle ad un DPO. 
        - Le regole vengono per il momento solo recuperate da Smartotum ma non memorizzate perchè manca ancora il modello delle regole a livello del database.

Il sistema di sincronizzazione parte ad ogni chiamata dell' endpoint di refresh perché il sistema non memorizza l'access token di Smartotum ma utilizza quello ritornato dall'utente ad ogni chiamata all'API.

### API IMPORTANTI PER GESTIONE DISPOSITIVI

Queste API operano direttamente sul database della Privacy Dashboard e restituiscono quindi una snapshot dei dati sincronizzati dall' ultimo refresh manuale.

**Prerequisiti**
- l'utente deve essersi registrato alla Privacy Dashboard utilizzando il suo account Smartotum (è un Data Subject)
- l'utente deve fornire il cookie contenente un access token Smartotum valido che deve essere legato all'account con cui si è registrato alla Privacy Dashboard. L'access token verrà poi validato dalla @ds_required tramite il procedimento spiegato in seguito.

**Consistenza dei Dati**
- i dati restano invariati finché l'utente non invoca l'endpoint di refresh `POST /api/homes/refresh`

#### GET /api/homes
- **Scopo**: elenco delle smart home associate all'utente.
- **Parametri**: nessuno.
- **Response**:
```json
[
  {
    "address": "Indirizzo",
    "name": "Fix Issues",
    "uuid": "fixissuesbpoyqq"
  }
]
```

#### GET /api/homes/{system_uuid}/rooms
- **Scopo**: elenco delle stanze appartenenti a una smart home specifica.
- **Parametri**: `system_uuid`
- **Response**:
```jsonc
[
  {
    "category": "House",
    "name": "Fix Issues",
    "room_uuid": "00000000-0000-0000-0000-000000000000"
  },
  {
    "category": "living",
    "name": "Stanza 1",
    "room_uuid": "bf673d0c-13ff-4e7c-9169-9a2cf2d28bb4"
  }
  // ... altre stanze
]
```

#### GET /api/homes/{system_uuid}/devices
- **Scopo**: elenco completo dei dispositivi della smart home, utile per filtrarli lato client.
- **Parametri**: `system_uuid`
- **Response** (estratto):
```jsonc
[
  {
    "device_uuid": "5d5ab482-3e02-4fdc-8b2b-83308ec446b6",
    "name": "Luce 11",
    "room_uuid": "bf673d0c-13ff-4e7c-9169-9a2cf2d28bb4",
    "topic_name": "domo_light"
  },
  {
    "device_uuid": "30b4bd14-029a-48fe-b57c-a9028aca2bbc",
    "name": "L2",
    "room_uuid": "bf673d0c-13ff-4e7c-9169-9a2cf2d28bb4",
    "topic_name": "domo_light"
  }
  // ... altri dispositivi
]
```

#### GET /api/homes/{system_uuid}/rooms/{room_uuid}/devices
- **Scopo**: recupera i dispositivi appartenenti a una specifica stanza, sfruttando la relazione stanza-dispositivo.
- **Parametri**: `system_uuid`, `room_uuid` (path).
- **Response**:
```jsonc
[
  {
    "device_uuid": "5d5ab482-3e02-4fdc-8b2b-83308ec446b6",
    "name": "Luce 11",
    "room_uuid": "bf673d0c-13ff-4e7c-9169-9a2cf2d28bb4",
    "topic_name": "domo_light"
  },
  {
    "device_uuid": "30b4bd14-029a-48fe-b57c-a9028aca2bbc",
    "name": "L2",
    "room_uuid": "bf673d0c-13ff-4e7c-9169-9a2cf2d28bb4",
    "topic_name": "domo_light"
  }
  // ... altri dispositivi della stanza
]
```

#### POST /api/homes/refresh
- **Scopo**: forza la sincronizzazione con Smartotum prima di consultare i dati.
- **Parametri/Body**: nessuno (fa fede il token nel cookie).
- **Uso suggerito**: invocarlo quando l'utente sa che la configurazione della smart home è stata aggiornata da fuori la Privacy Dashboard.

- Queste API sono state progettate per rendere immediata la selezione dei dispositivi durante la creazione delle regole da parte del sottosistema PTP

### GESTIONE DELL'AUTENTICAZIONE A SMARTOTUM

Questo approfondimento serve per spiegare come Smartotum gestisce l'autenticazione e di come il sistema PrivacyDashboard si interfaccia ad esso.

#### AUTENTICAZIONE SMARTOTUM 

Per il log-in viene fatta una richiesta: `POST https://api.smartotum.com/auth/signin`
```jsonc
{
  "formFields": [
    {"id":"email","value":"....."},
    {"id":"password","value":"..."}
  ]
}
```
Smartotum se autenticazione ha avuto successo risponde con:
```jsonc
{
    "status": "OK",
    "user": {
        "id": "....-....-....-....-............",
        "email": "....",
        "timeJoined": 0000000000000
    }
}

st-access-token: con scadenza dopo 1 ora
st-refresh-token: per il refresh dell'access token alla scadenza
```


#### AUTENTICAZIONE PRIVACY DASHBOARD

Attraverso la chiamata `POST http://privacydashboard.com/api/auth/login` fornendo:
```jsonc
{
    "email": "email@mail.com",
    "password": "password"
}
```
- Il backend recupera la email e cerca nel database se c'è una corrispondenza, se c'è procede all'autenticazione secondo il tipo di utente che richiede l'accesso:
    - Data Controller o DPO: 
        - si verifica la correttezza della password e si prepara un access token che viene ritornato
    - Data Subject:
        1. si inoltra la richiesta al modulo SmartotumClient che prepara la query a Smartotum e la invia secondo le specifiche spiegate precedentemente
        2. ricevuto st-access-token si chiama il modulo JWKS che si occupa della decodifica del token attraverso la decode_smartotum_token:
            - recupera il json contenente tutte le chiavi pubbliche attive facendo una get su SMARTOTUM_JWKS_URL
            - analizza header jwt per recuperare il kid cioè l'identificativo della chiave 
            - recupera la chiave pubblica corrispondente al kid nel json e la ritorna
            - attraverso la jwt.decode verifica la firma della chiave pubblica e decodifica il token da cui si ottengono informazioni come sub (identificativo utente) e scadenza
        3. ottenuti i campi che compongono il token si utilizza il sub e si va a cercare una corrispondenza sub == UUID utente:
            - se la corrispondenza c'è viene ritornato al client l'utente nel body della risposta e l'access token ottenuto da Smartotum nei cookie
            - se la corrispondenza non c'è viene lanciato un errore di credenziali errate (teoricamente si potrebbe chiedere al client di registrarsi perché è iscritto a Smartotum ma non alla PrivacyDashboard) 
        - I passaggi 2 e 3:
            - sono una sicurezza in più perché garantiscono che il token ricevuto sia veramente di Smartotum 
            - avvengono anche all'interno del decoratore @ds_required() per proteggere le route che devono essere chiamate solo da un DataSubject. 

#### VANTAGGI
- non avendo access e refresh token salvati rende il sistema più sicuro da attacchi che voglio accedere a Smartotum:
     - se il server detenesse il refresh token e venisse recuperato da un attaccante potrebbe essere usato per generare infiniti access token così da compromettere la casa dell'utente.
- rende il sistema più semplice non dovendo utilizzare sistemi di cifratura o wallet sicuri per tenere la chiave privata per la cifratura del refresh token

#### SVANTAGGI
- se Smartotum è offline il Data Subject non può accedere alla Privacy Dashboard
- non è possibile aggiornare i dati in background per tutti gli utenti perché il server non memorizza l'access token ma fa solo da intermediario tra Data Subject e Smartotum
- quando il token scade dopo 1h dall'accesso o se il backend va offline l'utente deve fare di nuovo il log-in 

---

## GESTIONE ERRORI E RETRY

SmartotumClient quando effettua una chiamata all’API di Smartotum in caso di risposta con codice serie 500 o 429 (troppe richieste) riprova dopo un certo backoff timer gestito dalla libreria Retry. Il tempo massimo della singola richiesta HTTP è configurabile attraverso `SMARTOTUM_TIMEOUT`


## GESTIONE APPLICAZIONI

Le applicazioni per il momento vengono recuperate da un file JSON all’interno di della cartella /backend/config, il cui path può essere configurato attraverso il file di configurazione (env).

Il JSON per il momento è così strutturato:

```json
[
 { "name": "appdaemon", "description": "for managing automations" },
 { "name": "domo-ir-controller", "description": "for managing air conditioning devices with a fake IR remote controller"},
 { "name": "domo-mosquitto", "description": "for managing MQTT connections" },
 { "name": "domo-scheduler", "description": "for managing the schedule of different gateways"},
 { "name": "domo-shelly-stock-manager", "description": "for managing actuators" },
 { "name": "esphome-updater", "description": "for managing updates of esphome devices" },
 { "name": "file-sync", "description": "to sync remote and local dht" },
 { "name": "homeassistant", "description": "for managing the ui and the home system" },
 { "name": "smartotum-asterisk", "description": "for managing video doorbell voip calls" },
 { "name": "smartotum-camera-manager", "description": "for managing cameras" },
 { "name": "smartotum-certbot", "description": "for managing SSL HTTPS certificates" },
 { "name": "domo-vpn", "description": "for managing vpn connections with the cloud" }
]
```


Il nome viene utilizzato all’interno della Privacy Dashboard come nome univoco che identifica l’applicazione.
Per tanto se più case utilizzano una stessa applicazione nella tabella Application è presente una sola entry, mentre la relazione tra l’applicazione e la casa è contenuta all’interno di un altra tabella e viene aggiornata di conseguenza.
Ne deriva il fatto che se un’applicazione non è più presente nella casa di un utente viene cancellata solo la relazione.
Per il momento non è supportata la cancellazione di un’applicazione dopo che è stata aggiunta.
Il backend ha già il codice che permette il recupero delle app da Smartotum, tenendo in mente questo possibile format:

```json
[
  {
    "topic_name": "domo_app",
    "topic_uuid": "u9392-388....",
    "value": { "id": "com.smartotum.homeassistant", "name": "Home Assistant" }
  },
  {
    "topic_name": "domo_app",
    "topic_uuid": "u9392-389....",
    "value": { "id": "com.smartotum.appdaemon", "name": "Appdaemon" }
  }
]
```


## PARAMETRI DI CONFIGURAZION ENV

```dotenv
POSTGRES_USER=<postgres_username>
POSTGRES_PASSWORD=<postgres_password>
POSTGRES_DB=<db_name>
POSTGRES_PORT=<5434>
FLASK_ENV=<development> 
DEV_DATABASE_URI=postgresql+psycopg2://<postgres_username>:<postgres_password>@localhost:5434/privacy_db
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173


SMARTOTUM_BASE_URL=https://api.smartotum.com
SMARTOTUM_API_BASE_PATH=/auth
SMARTOTUM_JWKS_URL=https://api.smartotum.com/auth/jwt/jwks.json
SMARTOTUM_ISSUER=https://api.smartotum.com/auth

SMARTOTUM_TIMEOUT=<integer_number>
SMARTOTUM_RID=emailpassword
SMARTOTUM_AUTH_MODE=header

SMARTOTUM_DEVICE_TOPICS=domo_light,domo_light_dimmable,domo_rgbw_light,domo_switch,domo_roller_shutter,domo_camera

SMARTOTUM_APPLICATIONS_JSON=./config/smartotum-apps.json
```
