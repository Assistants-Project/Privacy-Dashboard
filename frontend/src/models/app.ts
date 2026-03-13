import {Evaluation} from "./question"
import {UserModel} from "./user"


export enum DocumentStatus {
    Available = "AVAILABLE",
    Missing = "MISSING"
}

export type CreateApplicationRequest = {
    id: string;
    title: string;
    description?: string;
    available_consents?: string[];
};

export type UpdateApplicationRequest = {
    title: string;
    description?: string;
};

export type RefreshApplicationsResult = {
    message: string;
    warnings: string[];
};

export type SyncMessage = {
    level: "warning" | "error";
    text: string;
};

export type CreateApplicationResponse = {
    application_uuid: string;
};

export class AppModel {

    uuid: string
    name: string
    title: string
    description: string | undefined
    evaluation: Evaluation | undefined
    questionnaire_summary: string | undefined
    installed_at: string | undefined //se presente significa che l'oggetto Application è stato richiesto da un data subject per la sua casa
    owner: UserModel //Data Controller owner
    data_controllers: UserModel[] //array eventualmente vuoto se non ci sono data_controllers
    dpo: UserModel | undefined //solo 1 dpo per applicazione 
    pn_status: DocumentStatus | undefined //può essere undefined in caso di managed
    pia_status: DocumentStatus | undefined  //può essere undefined in caso di managed
    pending_right_requests_count: number //numero di right requests ancora pending per quella app

    //constructor minimo
    constructor(uuid: string, name: string, title: string, owner: UserModel) {
        this.uuid = uuid
        this.name = name
        this.title = title
        this.description = undefined
        this.evaluation = undefined
        this.questionnaire_summary = undefined
        this.installed_at = undefined
        this.owner = owner
        this.data_controllers = []
        this.dpo = undefined
        this.pn_status = undefined
        this.pia_status = undefined
        this.pending_right_requests_count = 0
    }
}
