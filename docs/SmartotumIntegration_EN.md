## SMARTOTUM INTEGRATION DOCUMENTATION - ALBERTO HUGONIN (Vers 0.5) 

### SMARTOTUM HOME AUTOMATION SYSTEM OPERATION

- The user can interface with the system through this API:
    - `POST https://api.smartotum.com/auth/signin`: performs the log-in with username and password.
    - `GET https://api.smartotum.com/service/systems/?offset=0&limit=100`: by passing their access token receives all the information of the systems they are responsible for and that it is possible to control, including the unique ID. 
    - `GET https://fixissuesbpoyqq.pods.smartotum.com/.dht/get_all`: by providing the unique ID of the system (internal POD of the home) to which they intend to connect e.g. `fixissuesbpoyqq` returns all the topics of the home that include: devices, applications, rules, rooms, users, scheduling, settings and much more.
    - It is possible to obtain elements of the same topic by replacing the `get_all` parameter with `topic_name/<chosen_topic>`.
- A non-exhaustive list of the topics present follows:
    - Environments/rooms: **domo_room**
    - Home apps: **domo_app**
    - Rules/policy: **privacy_rule**
    - Users/metadata: **domo_user**
    - Gateway/diagnostics: gateway (also present in smartotum devices)
    - Scheduling/Times: domo_schedule, domo_temperature_scheduling
    - Home settings: domo_house_mode, domo_house_temperature_mode, domo_room_temperature_setting
    - Connections: domo_actuator_connection
    - Notifications/log/analytics: domo_notifications, domo_last_notification, domo_ui_views_visits
    - We also have a series of topics that represent the **devices object of the rules** that we will create later: 
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
    - Each topic can present 1 or more entities / devices, for example for the domo_light topic all the lights installed in the Smarthome are present


### PRIVACY DASHBOARD -> SMARTOTUM

- The privacy dashboard retrieves information from the Smartotum system and reorganizes it to make it more easily usable for the following purposes:
    -  **Creation and Management of rules** for devices:
        - for compatible devices of a smart home it is possible to generate rules that will then be applied to the home automation system e.g.: 
          - you cannot turn on certain lights from 8 in the morning to 20 in the evening
          - cameras must be disabled from 14:00 to 20:00
    -   **Application management**:
        - the smart home can have applications installed that use and process the user's data and that therefore must comply with GDPR
        - The flow follows only in one direction: home applications are automatically imported into the Privacy Dashboard
        - any applications created at the privacy dashboard level for the moment cannot be linked to a home

- The **Data Subject** is the user of the application who wants to manage their personal data in relation to their personal smart home or third parties' smart homes to which they have access:
    - to be able to register and access the privacy dashboard they must be the owner of a Smartotum account
    - During registration basic information and authentication to their Smartotum account are requested
    - Following the log-in the client, by launching the refresh endpoint, retrieves and saves / synchronizes the following information from the Smartotum system:
        - all the homes to which the user has access, which includes home retrieval and assignment of each home to the user
        - for each home all its rooms, and a dummy room not present in the smartotum system is also created to group all devices without an assigned room
        - for each home all compatible devices are retrieved according to an allow list in the env file called SMARTOTUM_DEVICE_TOPICS and each device is assigned to its room which is consequently linked to a specific home
        - for the moment the list of applications is retrieved from a JSON file but the code already presents a good part of the logic for retrieval from Smartotum. It will later be possible to assign the app to a Data Controller who can then assign it to a DPO. 
        - Rules are for the moment only retrieved from Smartotum but not stored because the rules model at the database level is still missing.

The synchronization system starts at each call of the refresh endpoint because the system does not store the Smartotum access token but uses the one returned by the user at each call to the API.

### IMPORTANT APIs FOR DEVICE MANAGEMENT

These APIs operate directly on the Privacy Dashboard database and therefore return a snapshot of the data synchronized by the last manual refresh.

**Prerequisites**
- the user must have registered to the Privacy Dashboard using their Smartotum account (they are a Data Subject)
- the user must provide the cookie containing a valid Smartotum access token that must be linked to the account with which they registered to the Privacy Dashboard. The access token will then be validated by the @ds_required through the procedure explained later.

**Data Consistency**
- data remains unchanged until the user invokes the refresh endpoint `POST /api/homes/refresh`

#### GET /api/homes
- **Purpose**: list of smart homes associated with the user.
- **Parameters**: none.
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
- **Purpose**: list of rooms belonging to a specific smart home.
- **Parameters**: `system_uuid`
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
- **Purpose**: complete list of smart home devices, useful to filter them client-side.
- **Parameters**: `system_uuid`
- **Response** (extract):
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
- **Purpose**: retrieves devices belonging to a specific room, exploiting the room-device relationship.
- **Parameters**: `system_uuid`, `room_uuid` (path).
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
- **Purpose**: forces synchronization with Smartotum before consulting the data.
- **Parameters/Body**: none (the token in the cookie is used).
- **Suggested use**: call it when the user knows that the smart home configuration has been updated from outside the Privacy Dashboard.

- These APIs have been designed to make device selection immediate during rule creation by the PTP subsystem

### SMARTOTUM AUTHENTICATION MANAGEMENT

This deep dive serves to explain how Smartotum manages authentication and how the PrivacyDashboard system interfaces with it.

#### SMARTOTUM AUTHENTICATION 

For log-in a request is made: `POST https://api.smartotum.com/auth/signin`
```jsonc
{
  "formFields": [
    {"id":"email","value":"....."},
    {"id":"password","value":"..."}
  ]
}
```
Smartotum if authentication was successful responds with:
```jsonc
{
    "status": "OK",
    "user": {
        "id": "....-....-....-....-............",
        "email": "....",
        "timeJoined": 0000000000000
    }
}

st-access-token: expires after 1 hour
st-refresh-token: for refresh of the access token at expiration
```


#### PRIVACY DASHBOARD AUTHENTICATION

Through the call `POST http://privacydashboard.com/api/auth/login` providing:
```jsonc
{
    "email": "email@mail.com",
    "password": "password"
}
```
- The backend retrieves the email and searches in the database if there is a match, if there is it proceeds with authentication according to the type of user requesting access:
    - Data Controller or DPO: 
        - verifies the correctness of the password and prepares an access token that is returned
    - Data Subject:
        1. the request is forwarded to the SmartotumClient module which prepares the query to Smartotum and sends it according to the specifications explained previously
        2. once st-access-token is received the JWKS module is called which deals with decoding the token through decode_smartotum_token:
            - retrieves the json containing all active public keys by doing a get on SMARTOTUM_JWKS_URL
            - analyzes jwt header to retrieve the kid, i.e. the key identifier 
            - retrieves the public key corresponding to the kid in the json and returns it
            - through jwt.decode verifies the signature of the public key and decodes the token from which information such as sub (user identifier) and expiration are obtained
        3. once the fields that compose the token are obtained, sub is used and a match sub == user UUID is searched:
            - if the match is found, the user is returned to the client in the response body and the access token obtained from Smartotum in the cookies
            - if the match is not found, a wrong credentials error is raised (theoretically the client could be asked to register because they are subscribed to Smartotum but not to the PrivacyDashboard) 
        - Steps 2 and 3:
            - are an additional security because they guarantee that the token received is really from Smartotum 
            - also happen inside the decorator @ds_required() to protect the routes that must be called only by a DataSubject. 

#### ADVANTAGES
- not having access and refresh tokens saved makes the system safer against attacks that want to access Smartotum:
     - if the server held the refresh token and it was retrieved by an attacker it could be used to generate infinite access tokens thus compromising the user's home.
- makes the system simpler by not having to use encryption systems or secure wallets to keep the private key for encrypting the refresh token

#### DISADVANTAGES
- if Smartotum is offline the Data Subject cannot access the Privacy Dashboard
- it is not possible to update data in the background for all users because the server does not store the access token but only acts as an intermediary between Data Subject and Smartotum
- when the token expires after 1h from access or if the backend goes offline the user must log in again 

---

## ERROR HANDLING AND RETRY

SmartotumClient when it makes a call to the Smartotum API in case of a response with 500 series code or 429 (too many requests) retries after a certain backoff timer managed by the Retry library. The maximum time of the single HTTP request is configurable through `SMARTOTUM_TIMEOUT`


## APPLICATION MANAGEMENT

Applications for the moment are retrieved from a JSON file inside the /backend/config folder, whose path can be configured through the configuration file (env).

For the moment the JSON is structured like this:

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


The name is used inside the Privacy Dashboard as a unique name that identifies the application.
Therefore if multiple homes use the same application, in the Application table there is only one entry, while the relationship between the application and the home is contained in another table and is updated accordingly.
It follows that if an application is no longer present in a user's home only the relationship is deleted.
For the moment deletion of an application after it has been added is not supported.
The backend already has the code that allows retrieval of apps from Smartotum, keeping in mind this possible format:

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


## ENV CONFIGURATION PARAMETERS

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
