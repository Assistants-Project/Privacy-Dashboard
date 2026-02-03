import {
  getManagedApplications,
  getInstalledApplications,
  getCatalogApplications,
  claimManagedApplication,
  assignDpoToManagedApplication,
  UpdateApps
} from "../API/Applications/applicationAPI";
import { AppModel, DocumentStatus } from "../models/app"
import { Evaluation } from "../models/question";
import { Role, User } from "../models/user";

//l'idea principale è che recuperiamo la risposta ottenuta dal backend già come oggetto e la 
//castiamo al DTO (InstalledApplicationDto) che lo realizziamo nel modo più generale possibile
//compatibilmente con lo schema dell'endpoint ottenuto da swagger:
//se un parametro è required allora possiamo prenderlo direttamente del tipo dichiarato
//se un parametro è required ma è indicato anche object | null allora nel dto lo mappiamo come object | null
//se un parametro non è required ed è dichiarato come object | null allora nel dto lo mappiamo come param?: object | null
//perchè il parametro può non arrivare (?) o se arriva essere un oggetto null
//se un parametro non è requirec ma è indicato come object nel dto lo mappiamo come param?: object

//Mantenedno l'informazione parametro presente o no e valore interno null o no possiamo poi
//ricostruire i vari casi di interesse, ad esempio firstname settato (presente come parametro) ma vuoto (quindi null)

const fetchManagedApplications = async () => {
    try {
      const applications = await getManagedApplications();
      return applications;
    } catch (err) {
      console.error("Error fetching managed applications:", err);
    }
  };

type UserDto = {
  uuid: string,
  email: string; 
  firstname: string;
  //profile_picture NON CI SERVE PER IL MOMENTO
  lastname: string;
  role: Role;
};

type InnerApplicationDto = {
  uuid: string; //uuid anche se in swagger è indicato come non obbligatorio in realtà lo è 
  name: string;
  description?: string | null;
  evaluation?: Evaluation | null;
  questionnaire_summary?: string | null;
};

type DocumentStatusDto = "AVAILABLE" | "MISSING" | "FORBIDDEN";

type ApplicationDto = {
  application: InnerApplicationDto;
  installed_at?: string;  //può non essere presente se è un data controller a fare richiesta dell'app da catalogo
  data_controllers: UserDto[];
  dpo: UserDto | null;
  pn_status?: DocumentStatusDto; //di solito sempre presente
  pia_status?: DocumentStatusDto;
};

//serve per nornalizzare un parametro che nel caso sia un oggetto null venga tradotta in undefined, mentre
//se l'oggetto è una stringa lo mappiamo al valore che rappresenta:
//se la stringa è vuota lo mappiamo a undefined
//utile per description che se non ci arriva lo mettiamo a undefined ma se ci arriva una stringa vuota lo mappiamo
//anche esso a undefined
const normalizeOptionalString = (value: unknown): string | undefined =>
  typeof value === "string" && value.trim() !== "" ? value : undefined;

//ci proteggiamo nel caso venga aggiunta una valutazione in futuro
const normalizeOptionalEvaluation = (value: unknown): Evaluation | undefined =>
  value === Evaluation.GREEN || value === Evaluation.ORANGE || value === Evaluation.RED
    ? value
    : undefined;

const normalizeOptionalDocumentStatus = (value: unknown): DocumentStatus | undefined =>
  value === "AVAILABLE" || value === "MISSING" || value === "FORBIDDEN"
    ? (value as DocumentStatus)
    : undefined;


const toUserModel = (dto: UserDto): User =>
  //sono tutte stringhe o parametri required che nel caso siano vuoti non ci importa
  new User(
    dto.uuid,
    dto.email,
    dto.firstname,
    dto.lastname,
    dto.role,
  );

//trasforma quello che riceve dal backend nel nostro AppModel
//va bene sia per la chiamata a catalogo sia quella installed
const toAppModel = (dto: ApplicationDto): AppModel => {
  const app = dto.application ?? {}; 

  const model = new AppModel(app.uuid, app.name);
  model.description = normalizeOptionalString(app.description);
  model.evaluation = normalizeOptionalEvaluation(app.evaluation);
  model.questionnaire_summary = normalizeOptionalString(app.questionnaire_summary);
  model.installed_at = normalizeOptionalString(dto.installed_at);
  //manteniamo per il data controller array vuoto -> non ci sono
  //undefined non ci è stato inviato un dato corretto
  model.data_controllers = Array.isArray(dto.data_controllers)
    ? (dto.data_controllers as UserDto[]).map(toUserModel)
    : undefined;

  //type guard minima
  model.dpo = dto.dpo?.role === Role.DPO ? toUserModel(dto.dpo as UserDto) : undefined;
  model.pn_status = normalizeOptionalDocumentStatus(dto.pn_status);
  model.pia_status = normalizeOptionalDocumentStatus(dto.pia_status);

  return model;
};

  const fetchInstalledApplications = async (smartHomeUuid: string): Promise<AppModel[] | undefined> => {
    try {
      //cast semplice, permette di trattare il valore ritornato com un ApplicationDTO 
      const applications = (await getInstalledApplications(smartHomeUuid)) as ApplicationDto[];
      //controlliamo che sia un array 
      if (!Array.isArray(applications)) {
        console.warn("Unexpected installed applications payload:", applications);
        return undefined;
      }
      return applications.map(toAppModel);
    } catch (err) {
      throw err
    }
  }

  const fetchCatalogApplications = async (): Promise<AppModel[] | undefined> => {
    try {
      //cast semplice, permette di trattare il valore ritornato com un ApplicationDTO 
      const applications = (await getCatalogApplications()) as ApplicationDto[];
      //controlliamo che sia un array 
      if (!Array.isArray(applications)) {
        console.warn("Unexpected installed applications payload:", applications);
        return undefined;
      }
      return applications.map(toAppModel);
    } catch (err) {
      throw err
    }
  }


export const updateCatalogApplications = async (): Promise<boolean | undefined> => {
  try {
    const response = (await UpdateApps()) as boolean;
    return response;
  } catch (err) {
     throw err
  }
};

export const claimApplicationAsDataController = async (
  applicationUuid: string,
): Promise<boolean> => {
  try {
    return await claimManagedApplication(applicationUuid);
  } catch (err) {
    throw err;
  }
};

export const assignDpoToApplication = async (applicationUuid: string,dpoUuid: string): Promise<boolean> => {
  try {
    return await assignDpoToManagedApplication(applicationUuid, dpoUuid);
  } catch (err) {
    throw err;
  }
};


export {fetchManagedApplications, fetchInstalledApplications, fetchCatalogApplications}
