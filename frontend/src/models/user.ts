import { HomeModel } from "./home"
class User {
    email: string
    firstname: string
    lastname: string
    role: Role
    homes: HomeModel[] | undefined
    current_home: HomeModel | undefined


    constructor(email: string, firstname: string, lastname: string, role: Role, homes?: HomeModel[], current_home?: HomeModel) {
        this.email = email
        this.firstname = firstname
        this.lastname = lastname
        this.role = role
        this.homes = homes
        this.current_home = current_home
        
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