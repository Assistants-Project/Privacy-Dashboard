import {Evaluation} from "./question"
import {User} from "./user"


export enum DocumentStatus {
    Available = "AVAILABLE",
    Missing = "MISSING",
    Forbidden = "FORBIDDEN"
}

export type CreateApplicationRequest = {
    name: string;
    description?: string;
    available_consents?: string[];
};

export type CreateApplicationResponse = {
    application_uuid: string;
};

export class AppModel {

    uuid: string
    name: string
    description: string | undefined
    evaluation: Evaluation | undefined
    questionnaire_summary: string | undefined
    installed_at: string | undefined //se presente significa che l'oggetto Application è stato richiesto da un data subject per la sua casa
    data_controllers: User[] | undefined //array eventualmente vuoto se non ci sono data_controllers, undefined se c'è stato un errore
    dpo: User | undefined //solo 1 dpo per applicazione 
    pn_status: DocumentStatus | undefined //può essere undefined in caso di managed
    pia_status: DocumentStatus | undefined  //può essere undefined in caso di managed

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
        this.pn_status = undefined
        this.pia_status = undefined
    }
}
