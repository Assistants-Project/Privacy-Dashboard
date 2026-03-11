type RequestSelectedConsent = {
    uuid: string;
    content?: string;
}

class RequestModel {
    uuid: string
    right_type: RightType
    additional_information: string
    selected_consents: RequestSelectedConsent[] | undefined
    response: string | undefined
    created_at: string //sempre presente
    handled_at: string | undefined
    status: RequestStatus
    application_uuid: string //sempre legata ad un app


    //constructor minimo, i campi opzionali vengono poi valorizzati dal service
    constructor(uuid: string, right_type: RightType, created_at: string, application_uuid: string, additional_information: string, status: RequestStatus) {
        this.uuid = uuid
        this.right_type = right_type
        this.created_at = created_at
        this.application_uuid = application_uuid
        this.additional_information = additional_information
        this.status = status

        this.selected_consents = undefined
        this.response = undefined
        this.handled_at = undefined
    }
}

/**
 * Represents the type of the right
 */
enum RightType {
    ACCESS_DATA = "ACCESS_DATA",
    ASK_INFORMATION = "ASK_INFORMATION",
    COMPILE_COMPLAINT = "COMPILE_COMPLAINT",
    ERASE_DATA = "ERASE_DATA",
    REMOVE_EVERYTHING = "REMOVE_EVERYTHING",
    WITHDRAW_CONSENT = "WITHDRAW_CONSENT",
}

//etichette per la ui
const RIGHT_TYPE_LABELS: Record<RightType, string> = {
    [RightType.ACCESS_DATA]: "Access data",
    [RightType.ASK_INFORMATION]: "Ask information",
    [RightType.COMPILE_COMPLAINT]: "Compile complaint",
    [RightType.ERASE_DATA]: "Erase data",
    [RightType.REMOVE_EVERYTHING]: "Remove everything",
    [RightType.WITHDRAW_CONSENT]: "Withdraw consent",
};

//testo predefinito per la submit di una request (prefisso) da completare con il nome dell'app
const RIGHT_TYPE_MESSAGE_PREFIX: Record<RightType, string> = {
    [RightType.ACCESS_DATA]: "I would like to exercise my right of access to my personal data processed by ",
    [RightType.ASK_INFORMATION]: "I would like to request additional information about the processing performed by ",
    [RightType.COMPILE_COMPLAINT]: "I would like to file a complaint regarding the processing performed by ",
    [RightType.ERASE_DATA]: "I would like to request the erasure of my personal data processed by ",
    [RightType.REMOVE_EVERYTHING]: "I would like to request the removal of all my personal data and associated processing by ",
    [RightType.WITHDRAW_CONSENT]: "I would like to withdraw my consent(s) for ",
};

//per costruire il messaggio completo
const buildPredefinedRightMessage = (rightType: RightType, applicationName?: string): string => {
    const prefix = RIGHT_TYPE_MESSAGE_PREFIX[rightType] ?? "I would like to exercise a GDPR right regarding "
    return `${prefix}${applicationName}.`
}

//represent the status of the request
enum RequestStatus {
    PENDING = "PENDING", //not already managed by a DC/DPO
    HANDLED = "HANDLED" //already managed by DC/DPO
}

export { RequestModel, RightType, RIGHT_TYPE_LABELS, RIGHT_TYPE_MESSAGE_PREFIX, buildPredefinedRightMessage, RequestStatus }
export type { RequestSelectedConsent }
