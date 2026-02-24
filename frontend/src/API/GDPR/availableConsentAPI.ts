import { getApiError } from "../apiError";
import baseURL from "../baseUrl";

async function getAvailableConsentsByApplicationUuid(applicationUuid: string) {
  const response = await fetch(
    baseURL + `consents/application/${encodeURIComponent(applicationUuid)}`,
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

async function getConsentsStateBySmartHomeAndApplicationUuid(smartHomeUuid: string, applicationUuid: string) {
  const response = await fetch(
    baseURL + `consents/home/${encodeURIComponent(smartHomeUuid)}/application/${encodeURIComponent(applicationUuid)}`,
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

async function setGivenConsentsBySmartHomeAndApplicationUuid(
  smartHomeUuid: string,
  applicationUuid: string,
  selectedConsents: string[],
) {
  const response = await fetch(
    baseURL + `consents/home/${encodeURIComponent(smartHomeUuid)}/application/${encodeURIComponent(applicationUuid)}`,
    {
      method: "PUT",
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

async function addAvailableConsentToManagedApplicationByUuid(applicationUuid: string, content: string) {
  const response = await fetch(
    baseURL + `consents/application/${encodeURIComponent(applicationUuid)}`,
    {
      method: "POST",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ content }),
    },
  );
  if (response.status === 201 || response.ok) {
    return await response.json();
  }
  throw await getApiError(response);
}

async function removeAvailableConsentFromManagedApplicationByUuid(applicationUuid: string, availableConsentUuid: string) {
  const response = await fetch(
    baseURL + `consents/application/${encodeURIComponent(applicationUuid)}/${encodeURIComponent(availableConsentUuid)}`,
    {
      method: "DELETE",
      credentials: "include",
    },
  );
  if (response.status === 204 || response.ok) {
    return;
  }
  throw await getApiError(response);
}

export {
  getAvailableConsentsByApplicationUuid,
  getConsentsStateBySmartHomeAndApplicationUuid,
  setGivenConsentsBySmartHomeAndApplicationUuid,
  addAvailableConsentToManagedApplicationByUuid,
  removeAvailableConsentFromManagedApplicationByUuid,
};
