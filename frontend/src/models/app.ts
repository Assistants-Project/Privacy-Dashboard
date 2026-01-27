import {Evaluation} from "./question"
import {User} from "./user"

export class AppModel {

    uuid: string
    name: string
    description: string | undefined
    evaluation: Evaluation | undefined
    questionnaire_summary: string | undefined
    installed_at: string | undefined //se presente significa che l'oggetto Application è stato richiesto da un data subject per la sua casa
    data_controllers: User[] | undefined //array eventualmente vuoto se non ci sono data_controllers, undefined se c'è stato un errore
    dpo: User | undefined //solo 1 dpo per applicazione 

    //constructor minimo
    constructor(uuid: string, name: string) {
        this.uuid = uuid
        this.name = name
        this.description = undefined
        this.evaluation = undefined
        this.questionnaire_summary = undefined
        this.installed_at = undefined
        this.data_controllers = []
        this.dpo = undefined
    }
}


// "uuid": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
//       "name": "string",
//       "description": "string",
//       "evaluation": "GREEN",
//       "questionnaire_summary": "string"


//       "data_controllers": [
//       {
//         "uuid": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
//         "firstname": "string",
//         "lastname": "string",
//         "email": "string",
//         "profile_picture": "string",
//         "role": "DATA_SUBJECT"
//       }
//     ],
//     "dpo": {
//       "uuid": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
//       "firstname": "string",
//       "lastname": "string",
//       "email": "string",
//       "profile_picture": "string",
//       "role": "DATA_PROTECTION_OFFICER"
//     }
