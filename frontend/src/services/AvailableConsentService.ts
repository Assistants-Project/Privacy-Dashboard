import {giveConsentsInSmartHomeByUuid,getAvailableConsentsByApplicationUuid,getGivenConsentsBySmartHomeUuid,} from "../API/GDPR/availableConsentAPI";
import {AvailableConsentModel,GivenConsentInHomeModel,} from "../models/available_consent";

type AvailableConsentDto = {
  uuid: string;
  content: string;
};

type GivenConsentInHomeDto = {
  available_consent: AvailableConsentDto;
  application_uuid: string;
  given_at: string;
};

const normalizeString = (value: unknown): string =>
  typeof value === "string" ? value : "";

const toAvailableConsentModel = (dto: AvailableConsentDto,): AvailableConsentModel => {
  return new AvailableConsentModel(
    normalizeString(dto.uuid),
    normalizeString(dto.content),
  );
};

const toGivenConsentInHomeModel = (dto: GivenConsentInHomeDto,): GivenConsentInHomeModel => {
  return new GivenConsentInHomeModel(
    toAvailableConsentModel(dto.available_consent),
    normalizeString(dto.application_uuid),
    normalizeString(dto.given_at),
  );
};

export const fetchAvailableConsentsByApplication = async (applicationUuid: string): Promise<AvailableConsentModel[] | undefined> => {
  
  try {
    const payload = (await getAvailableConsentsByApplicationUuid(applicationUuid,)) as unknown;

    if (!Array.isArray(payload)) {
      console.warn("Unexpected available consents payload:", payload);
      return undefined;
    }

    return (payload as AvailableConsentDto[]).map(toAvailableConsentModel);
  } catch (err) {
    throw err;
  }
};

export const fetchGivenConsentsBySmartHome = async (smartHomeUuid: string,): Promise<GivenConsentInHomeModel[] | undefined> => {
  
  try {
    const payload = (await getGivenConsentsBySmartHomeUuid(
      smartHomeUuid,
    )) as unknown;

    if (!Array.isArray(payload)) {
      console.warn("Unexpected given consents payload:", payload);
      return undefined;
    }

    return (payload as GivenConsentInHomeDto[]).map(toGivenConsentInHomeModel);
  } catch (err) {
    throw err;
  }
};

export const giveConsentsInSmartHome = async (smartHomeUuid: string,selectedConsents: string[],): Promise<void> => {
  
  const normalizedSelectedConsents = Array.from(
    new Set(
      selectedConsents
        .filter((value): value is string => typeof value === "string")
        .map((value) => value.trim())
        .filter((value) => value !== ""),
    ),
  );

  if (normalizedSelectedConsents.length === 0) return;
  await giveConsentsInSmartHomeByUuid(smartHomeUuid, normalizedSelectedConsents);

};