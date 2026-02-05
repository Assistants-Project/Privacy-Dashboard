import baseURL from "../baseUrl";
import { getApiError } from "../apiError";

async function getManagedApplications() {
  let response = await fetch(baseURL + "applications/managed", {
    method: "GET",
    credentials: "include",
  });
  if (response.ok) {
    const applications = await response.json();
    return applications;
  } else {
    const errDetail = await response.json();
    if (errDetail?.message) {
      throw new Error(errDetail.message);
    }

    throw new Error("Something went wrong");
  }
}

async function getInstalledApplications(smartHomeUuid: string) {
  let response = await fetch(baseURL + `applications/home/${encodeURIComponent(smartHomeUuid)}`, {
    method: "GET",
    credentials: "include",
  });
  if (response.ok) {
    const applications = await response.json();
    return applications;
  }

  throw await getApiError(response);

}

async function getCatalogApplications() {
  let response = await fetch(baseURL + `applications/catalog`, {
    method: "GET",
    credentials: "include",
  });
  if (response.ok) {
    const applications = await response.json();
    return applications;
  }

  throw await getApiError(response);

}

async function claimManagedApplication(applicationUuid: string): Promise<boolean> {
  const response = await fetch(
    baseURL + `applications/managed/${encodeURIComponent(applicationUuid)}`,
    {
      method: "POST",
      credentials: "include",
    },
  );

  if (response.status === 201) return true;
  if (response.status === 204) return false;

  throw await getApiError(response);
}

async function assignDpoToManagedApplication(applicationUuid: string,dpoUuid: string): Promise<boolean> {
  const response = await fetch(baseURL +`applications/managed/${encodeURIComponent(applicationUuid)}/dpo`,
{
      method: "PUT",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ dpo_uuid: dpoUuid }),
    },
  );

  if (response.status === 201) return true;
  if (response.status === 204) return false;

  throw await getApiError(response);
}

async function UpdateApps() {
  let response = await fetch(baseURL + "applications/refresh", {method: "POST",credentials: "include"});
  if (response.ok) {
    return true;
  }

  throw await getApiError(response);
}

async function getPiaTemplate() {
  let response = await fetch(baseURL + "applications/pia-template", {
    method: "GET",
    credentials: "include",
  });
  if (response.ok) {
    const piaTemplate = await response.json();
    return piaTemplate;
  } else {
    const errDetail = await response.json();
    if (errDetail?.message) {
      throw new Error(errDetail.message);
    }

    throw new Error("Something went wrong");
  }
}

async function getPiaByManagedApplicationUuid(applicationUuid: string) {
  let response = await fetch(
    baseURL + "applications/managed-application/" + applicationUuid + "/pia",
    {
      method: "GET",
      credentials: "include",
    }
  );
  if (response.status === 204 || response.status === 404) {
    return null;
  }
  if (response.ok) {
    const result = await response.json();
    return result;
  } else {
    throw await getApiError(response);
  }
}

async function submitPiaByManagedApplicationUuid(
  applicationUuid: string,
  content: any
) {
  let response = await fetch(
    baseURL + "applications/managed-application/" + applicationUuid + "/pia",
    {
      method: "PUT",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ content }),
    }
  );
  if (!response.ok) {
    const errDetail = await response.json();
    // Flask-smorest validation error
    if (errDetail?.errors) {
      const jsonErrors = errDetail.errors.json;
      if (jsonErrors && typeof jsonErrors === "object") {
        const msgs = Object.values(jsonErrors).flat().join("\n");
        throw new Error(msgs || "Validation error");
      }
      if (typeof errDetail.errors === "string") {
        throw new Error(errDetail.errors);
      }
    }
    if (errDetail?.message) {
      throw new Error(errDetail.message);
    }

    throw new Error("Something went wrong");
  }
}

export {
  getManagedApplications,
  getPiaTemplate,
  getPiaByManagedApplicationUuid,
  submitPiaByManagedApplicationUuid,
  getInstalledApplications,
  getCatalogApplications,
  claimManagedApplication,
  assignDpoToManagedApplication,
  UpdateApps
};
