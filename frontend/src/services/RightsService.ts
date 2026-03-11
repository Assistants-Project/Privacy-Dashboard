import {
  getRequestsHome,
  getRequestsInbox,
  handleRequest,
  submitRequest,
} from "../API/GDPR/RightsAPI";
import { RequestModel, RequestSelectedConsent, RequestStatus, RightType } from "../models/request";

//l'idea principale è che recuperiamo la risposta ottenuta dal backend già come oggetto e la
//castiamo al DTO che lo realizziamo nel modo più generale possibile compatibilmente
//con lo schema dell'endpoint ottenuto da swagger:
//se un parametro è required allora possiamo prenderlo direttamente del tipo dichiarato
//se un parametro è required ma è indicato anche come object | null allora nel dto lo mappiamo come object | null
//se un parametro non è required ed è dichiarato come object | null allora nel dto lo mappiamo come param?: object | null
//perchè il parametro può non arrivare (?) o se arriva essere un oggetto null
//se un parametro non è required ed è indicato come object allora nel dto lo mappiamo come param?: object
//
//Mantenendo l'informazione "parametro presente o no" e "valore interno null o no" possiamo poi
//ricostruire i vari casi di interesse, ad esempio una stringa presente ma vuota.

//DTO della richiesta 
type RequestDto = {
  uuid: string;
  right_type: RightType;
  additional_information: string;
  selected_consents?: Array<{ uuid?: string | null; content?: string | null }> | null;
  response: string | null; //può arrivare vuota dal backend
  created_at: string;
  handled_at: string | null;
  status: RequestStatus;
};

//DTO della risposta del backend per la lista di requests (wrapper con informazioni aggiuntive)
type RequestResItemDto = {
  request: RequestDto;
  user_email: string;
  application_name: string;
  application_uuid: string;
};

//DTO per la submit della request (rispetta lo schema del backend)
type SubmitRequestDto = {
  right_type: RightType;
  additional_information: string;
  smart_home_uuid: string;
  application_uuid: string;
  selected_consents?: string[];
};

//DTO per la handle della request (DC/DPO)
//permette di cambiare lo stato e inserire una risposta ad una richiesta
type HandleRequestDto = {
  status: RequestStatus;
  response?: string;
};

//modello che usiamo nel frontend per rappresentare un elemento di lista
type RequestListItem = {
  request: RequestModel;
  user_email: string;
  application_name: string;
};

//se stringa required è vuota (null) la mappiamo a stringa vuota (per sicurezza)
const normalizeString = (value: unknown): string =>
  typeof value === "string" ? value : "";

//se stringa facoltativa è vuota la mappiamo a undefined
const normalizeOptionalString = (value: unknown): string | undefined =>
  typeof value === "string" && value.trim() !== "" ? value : undefined;

const normalizeOptionalSelectedConsents = (
  value: unknown,
): RequestSelectedConsent[] | undefined => {
  if (!Array.isArray(value)) return undefined;

  const normalized = value
    .map((item): RequestSelectedConsent | undefined => {
      if (typeof item === "string") {
        const uuid = item.trim();
        return uuid ? { uuid } : undefined;
      }
      if (!item || typeof item !== "object") return undefined;
      const rawUuid = "uuid" in item ? item.uuid : undefined;
      const rawContent = "content" in item ? item.content : undefined;
      const uuid = typeof rawUuid === "string" ? rawUuid.trim() : "";
      if (!uuid) return undefined;
      const content =
        typeof rawContent === "string" && rawContent.trim() !== ""
          ? rawContent
          : undefined;
      return { uuid, ...(content ? { content } : {}) };
    })
    .filter((item): item is RequestSelectedConsent => item !== undefined);

  if (normalized.length === 0) return undefined;
  return normalized;
};

//trasforma quello che riceve dal backend nel nostro RequestModel
//application_uuid non è dentro request ma arriva nel wrapper della response
const toRequestModel = (dto: RequestDto, application_uuid: unknown): RequestModel => {
  const model = new RequestModel(
    normalizeString(dto.uuid),
    dto.right_type,
    normalizeString(dto.created_at),
    normalizeString(application_uuid),
    normalizeString(dto.additional_information),
    dto.status,
  );

  //questi due campi possono essere null o stringa vuota, quindi li mappiamo a undefined
  model.selected_consents = normalizeOptionalSelectedConsents(dto.selected_consents);
  model.response = normalizeOptionalString(dto.response);
  model.handled_at = normalizeOptionalString(dto.handled_at);

  return model;
};

//trasforma un item della lista dal backend nel nostro modello per la UI
const toRequestListItem = (dto: RequestResItemDto): RequestListItem => {
  return {
    request: toRequestModel(dto.request, dto.application_uuid),
    user_email: normalizeString(dto.user_email),
    application_name: normalizeString(dto.application_name),
  };
};

//carica la lista di richieste lato Data Controller / DPO (inbox)
export const fetchRequestsInbox = async (
  status?: RequestStatus,
): Promise<RequestListItem[] | undefined> => {
  try {
    //cast semplice, permette di trattare il valore ritornato come RequestResItemDto[]
    const payload = (await getRequestsInbox(status)) as unknown;
    if (!Array.isArray(payload)) {
      console.warn("Unexpected requests inbox payload:", payload);
      return undefined;
    }
    return (payload as RequestResItemDto[]).map(toRequestListItem);
  } catch (err) {
    throw err;
  }
};

//carica la lista di richieste lato Data Subject, filtrate per casa corrente e stato (stato è facoltativo)
export const fetchRequestsHome = async (
  home_uuid: string,
  status?: RequestStatus,
): Promise<RequestListItem[] | undefined> => {
  try {
    const payload = (await getRequestsHome(home_uuid, status)) as unknown;
    if (!Array.isArray(payload)) {
      console.warn("Unexpected requests home payload:", payload);
      return undefined;
    }
    return (payload as RequestResItemDto[]).map(toRequestListItem);
  } catch (err) {
    throw err;
  }
};

//sottomette una nuova request lato Data Subject
export const submitRightRequest = async (
  dto: SubmitRequestDto,
): Promise<RequestModel | undefined> => {
  try {
    const payload = (await submitRequest(dto)) as unknown;
    const request = payload as RequestDto;
    return toRequestModel(request, dto.application_uuid);
  } catch (err) {
    throw err;
  }
};

//gestisce una request lato Data Controller / DPO (aggiorna status e/o risposta)
export const handleRightRequest = async (
  request_uuid: string,
  application_uuid: string,
  status: RequestStatus,
  response?: string,
): Promise<RequestModel | undefined> => {
  try {
    const dto: HandleRequestDto = {
      status,
      ...(typeof response === "string" ? { response } : {}),
    };

    const payload = (await handleRequest(request_uuid, dto)) as unknown;
    const request = payload as RequestDto;
    return toRequestModel(request, application_uuid);
  } catch (err) {
    throw err;
  }
};

export type { RequestListItem, SubmitRequestDto };
