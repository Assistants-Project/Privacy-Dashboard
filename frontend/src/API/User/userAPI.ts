import baseURL from "../baseUrl";

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

export { getMessagedContacts };
