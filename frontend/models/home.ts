/**
 * Represents a home of a user
 */
class HomeModel {
    uuid: string
    name: string
    address: string | undefined
    zip_code: string | undefined
    country: string | undefined
    // latitude: string
    // longitude: string
    // timezone: string
    // language: string



    constructor(uuid: string, name: string, address: string, zip_code: string, country: string) {
        this.uuid = uuid
        this.name = name
        this.address = address
        this.zip_code = zip_code
        this.country = country;
    }
}

export { HomeModel }