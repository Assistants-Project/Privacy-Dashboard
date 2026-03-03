import {addAvailableConsentToManagedApplicationByUuid,getAvailableConsentsByApplicationUuid,getConsentsStateBySmartHomeAndApplicationUuid,removeAvailableConsentFromManagedApplicationByUuid,setGivenConsentsBySmartHomeAndApplicationUuid,} from "../API/GDPR/availableConsentAPI";
import {ConsentModel,} from "../models/available_consent";

type AvailableConsentDto = {
  uuid: string;
  content: string;
  sifis_action_id?: string | null;
};

type ConsentStateDto = {
  uuid: string;
  content: string;
  given?: boolean;
  given_at?: string | null;
  sifis_action_id?: string | null;
};

const normalizeString = (value: unknown): string =>
  typeof value === "string" ? value : "";

const normalizeOptionalString = (value: unknown): string | undefined =>
  typeof value === "string" ? value : undefined;

const normalizeBoolean = (value: unknown): boolean | undefined => {
  if (value === true) return true;
  if (value === false) return false;
  return undefined;
};

const toConsentModel = (dto: ConsentStateDto,): ConsentModel => {
  const normalizedGivenAt = dto.given_at === null ? undefined : normalizeOptionalString(dto.given_at);
  return new ConsentModel(
    normalizeString(dto.uuid),
    normalizeString(dto.content),
    normalizeBoolean(dto.given),
    normalizedGivenAt,
    normalizeOptionalString(dto.sifis_action_id === null ? undefined : dto.sifis_action_id),
  );
};

export const fetchAvailableConsentsByApplication = async (applicationUuid: string): Promise<ConsentModel[]> => {
  try {
    const payload = (await getAvailableConsentsByApplicationUuid(applicationUuid,)) as unknown;

    if (!Array.isArray(payload)) {
      throw new Error("Unexpected available consents payload");
    }

    return (payload as AvailableConsentDto[]).map(toConsentModel);
  } catch (err) {
    throw err;
  }
};

export const fetchConsentsStateBySmartHomeAndApplication = async (smartHomeUuid: string,applicationUuid: string,): Promise<ConsentModel[]> => {
  try {
    const payload = (await getConsentsStateBySmartHomeAndApplicationUuid(
      smartHomeUuid,
      applicationUuid,
    )) as unknown;

    if (!Array.isArray(payload)) {
      throw new Error("Unexpected consent state payload");
    }

    return (payload as ConsentStateDto[]).map(toConsentModel);
  } catch (err) {
    throw err;
  }
};

export const giveConsentsInSmartHome = async (smartHomeUuid: string,applicationUuid: string,selectedConsents: string[],): Promise<void> => {
  const normalizedSelectedConsents = Array.from(
    new Set(
      selectedConsents
        .filter((value): value is string => typeof value === "string")
        .map((value) => value.trim())
        .filter((value) => value !== ""),
    ),
  );

  if (normalizedSelectedConsents.length === 0) return;
  await setGivenConsentsBySmartHomeAndApplicationUuid(
    smartHomeUuid,
    applicationUuid,
    normalizedSelectedConsents,
  );
};

export const addAvailableConsentToManagedApplication = async (applicationUuid: string, content: string): Promise<ConsentModel> => {
  const normalizedContent = content.trim();
  const payload = await addAvailableConsentToManagedApplicationByUuid(applicationUuid, normalizedContent) as AvailableConsentDto;
  return toConsentModel(payload);
};

export const removeAvailableConsentFromManagedApplication = async (applicationUuid: string, availableConsentUuid: string): Promise<void> => {
  await removeAvailableConsentFromManagedApplicationByUuid(applicationUuid, availableConsentUuid);
};
