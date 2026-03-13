type RelatedApplicationModel = {
    uuid: string;
    name: string;
    title: string;
};

class UserModel {
    uuid: string
    email: string
    firstname: string
    lastname: string
    role: Role
    relatedApplications?: RelatedApplicationModel[]


    constructor(uuid: string, email: string, firstname: string, lastname: string, role: Role, relatedApplications?: RelatedApplicationModel[]) {
        this.email = email
        this.firstname = firstname
        this.lastname = lastname
        this.role = role
        this.uuid = uuid
        this.relatedApplications = relatedApplications
        
    }
}

/**
 * Represents the role of a user.
 * The values present in this enum are the only valid values for the role of a user.
 */
enum Role {
    DataSubject = "DATA_SUBJECT",
    DataController = "DATA_CONTROLLER",
    DPO = "DATA_PROTECTION_OFFICER"
}

const ROLE_LABELS: Record<Role, string> = {
    [Role.DataSubject]: "Data Subject",
    [Role.DataController]: "Data Controller",
    [Role.DPO]: "Data Protection Officer",
};

const getRoleLabel = (role: Role): string => ROLE_LABELS[role] ?? role;

export { UserModel, Role, ROLE_LABELS, getRoleLabel }
export type { RelatedApplicationModel }
