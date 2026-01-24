import baseURL from "../baseUrl";
import { getApiError } from "../apiError";

async function getHomes() {
  let response = await fetch(baseURL + "homes", {
    method: "GET",
    credentials: "include",
  });
  if (response.ok) {
    const homes = await response.json();
    return homes;
  }

  throw await getApiError(response);
}

async function getHomeRooms(homeUuid: string) {
  let response = await fetch(`${baseURL}homes/${homeUuid}/rooms`, {
    method: "GET",
    credentials: "include",
  });
  if (response.ok) {
    return await response.json();
  }

  throw await getApiError(response);
}

export { getHomes, getHomeRooms };
