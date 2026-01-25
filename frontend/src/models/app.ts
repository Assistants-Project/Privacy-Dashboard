import {Evaluation} from "./question"
import {User} from "./user"

export class AppModel {

    uuid: string
    name: string
    description: string | undefined
    evaluation: Evaluation | undefined
    questionnaire_summary: string | undefined
    installed_at: string | undefined
    data_controllers: User[]
    dpos: User[]

    constructor(uuid: string, name: string) {
        this.uuid = uuid
        this.name = name
        this.description = undefined
        this.evaluation = undefined
        this.questionnaire_summary = undefined
        this.installed_at = undefined
        this.data_controllers = []
        this.dpos = []
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
//     "dpos": [
//       {
//         "uuid": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
//         "firstname": "string",
//         "lastname": "string",
//         "email": "string",
//         "profile_picture": "string",
//         "role": "DATA_SUBJECT"
//       }
//     ]
