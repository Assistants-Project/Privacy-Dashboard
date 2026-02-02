import baseURL from "../baseUrl";
import { getApiError } from "../apiError";

async function getContacts() {
  let response = await fetch(baseURL + "users/contacts", {
    method: "GET",
    credentials: "include",
  });
  if (response.ok) {
    const result = await response.json();
    return result;
  } else {
    const errDetail = await response.json();
    if (errDetail?.message) {
      throw new Error(errDetail.message);
    }

    throw new Error("Something went wrong");
  }
}

//serve per poter scegliere il dpo da assegnare
async function getDpos() {
  const response = await fetch(baseURL + "users/dpos", {
    method: "GET",
    credentials: "include",
  });

  if (response.ok) {
    return await response.json();
  }

  throw await getApiError(response);
}

async function getMessagedContacts() {
  let response = await fetch(baseURL + "users/contacts/messaged", {
    method: "GET",
    credentials: "include",
  });
  if (response.ok) {
    const result = await response.json();
    return result;
  } else {
    const errDetail = await response.json();
    if (errDetail?.message) {
      throw new Error(errDetail.message);
    }

    throw new Error("Something went wrong");
  }
}

export { getContacts, getDpos, getMessagedContacts };
