class PrivacyNotice {
    uuid: string
    content: string


    constructor(uuid: string, content: string) {
        this.uuid = uuid
        this.content = content
    }
}

export { PrivacyNotice }