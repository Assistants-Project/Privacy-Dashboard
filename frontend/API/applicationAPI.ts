import baseURL from "./baseUrl";

async function getManagedApplications() {
  let response = await fetch(baseURL + "/applications/managed", {
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

async function getPiaTemplate() {
  let response = await fetch(baseURL + "/applications/pia-template", {
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

export { getManagedApplications, getPiaTemplate };
