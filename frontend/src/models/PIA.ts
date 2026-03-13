class PIAModel {
    application_uuid: string
    content: any


    constructor(application_uuid: string, content: any) {
        this.application_uuid = application_uuid
        this.content = content
    }
}

export { PIAModel }
