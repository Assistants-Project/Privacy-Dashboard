import { getApiError } from "../apiError";
import baseURL from "../baseUrl";

async function getAvailableConsentsByApplicationUuid(applicationUuid: string) {
  const response = await fetch(
    baseURL + `available-consents/application/${encodeURIComponent(applicationUuid)}`,
    {
      method: "GET",
      credentials: "include",
    },
  );
  if (response.ok) {
    return await response.json();
  }
  throw await getApiError(response);
}

async function getGivenConsentsBySmartHomeUuid(smartHomeUuid: string) {
  const response = await fetch(
    baseURL + `available-consents/home/${encodeURIComponent(smartHomeUuid)}`,
    {
      method: "GET",
      credentials: "include",
    },
  );
  if (response.ok) {
    return await response.json();
  }
  throw await getApiError(response);
}

async function giveConsentsInSmartHomeByUuid(
  smartHomeUuid: string,
  selectedConsents: string[],
) {
  const response = await fetch(
    baseURL + `available-consents/home/${encodeURIComponent(smartHomeUuid)}`,
    {
      method: "POST",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ selected_consents: selectedConsents }),
    },
  );
  if (response.status === 204 || response.ok) {
    return;
  }
  throw await getApiError(response);
}

export {
  getAvailableConsentsByApplicationUuid,
  getGivenConsentsBySmartHomeUuid,
  giveConsentsInSmartHomeByUuid,
};
