import { HomeModel } from "./home"
class User {
    uuid: string
    email: string
    firstname: string
    lastname: string
    role: Role


    constructor(uuid: string, email: string, firstname: string, lastname: string, role: Role) {
        this.email = email
        this.firstname = firstname
        this.lastname = lastname
        this.role = role
        this.uuid = uuid
        
    }
}

/**
 * Represents the role of a user.
 * The values present in this enum are the only valid values for the role of a user.
 */
enum Role {
    DataSubject = "DATA_SUBJECT",
    DatController = "DATA_CONTROLLER",
    DPO = "DATA_PROTECTION_OFFICER"
}

export { User, Role }