import { getHomes, getHomeRooms } from "../API/Homes/homesAPI";
import { HomeModel } from "../models/home";

type HomeDto = {
  uuid: string;
  name: string;
  //sono tutti parametri opzionali
  address?: string | null; // ? esprime se manca nella risposta, mentre | null la proprietà c'è ma la stringa è vuota 
  zip_code?: string | null;
  country?: string | null;
  // latitude?: number | null;
  // longitude?: number | null;
  // timezone?: string | null;
  // language?: string | null;
};

//se stringa required è vuota (null) la mappiamo a stringa vuota (per sicurezza)
const normalizeString = (value: unknown): string =>
  typeof value === "string" ? value : "";

//se stringa facoltativa è vuota la mappiamo a undefined
const normalizeOptionalString = (value: unknown): string | undefined =>
  typeof value === "string" ? value : undefined;

const toHomeModel = (home: HomeDto): HomeModel => {

  const model = new HomeModel(
    normalizeString(home.uuid),
    normalizeString(home.name),
    normalizeOptionalString(home.address),
    normalizeOptionalString(home.zip_code),
    normalizeOptionalString(home.country),
  );

  return model;
};

export const fetchHomes = async (): Promise<HomeModel[] | undefined> => {
  try {
    const homes = (await getHomes()) as HomeDto[];
    if (!Array.isArray(homes)) {
      console.warn("Unexpected homes payload:", homes);
      return undefined;
    }
    return homes.map(toHomeModel);
  } catch (err) {
    console.error("Error getting homes:", err);
  }
};

export const fetchHomeRooms = async (homeUuid: string) => {
  try {
    return await getHomeRooms(homeUuid);
  } catch (err) {
    console.error("Error getting home rooms:", err);
  }
};
