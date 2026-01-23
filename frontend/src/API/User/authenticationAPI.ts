import baseURL from "../baseUrl";
import { getApiError } from "../apiError";

/** ------------------- Access APIs ------------------------ */

async function login(email: string, password: string) {
    let response = await fetch(baseURL + "auth/login", {
        method: 'POST',
        credentials: "include",
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email: email, password: password },)
    })
    if (response.ok) {
        const user = await response.json()
        return user
    }

    throw await getApiError(response);
}

async function logOut() {
    await fetch(baseURL + 'auth/logout', { method: 'POST', credentials: "include" });
}

async function getUserInfo() {
    const response = await fetch(baseURL + 'auth/current', { credentials: "include" })
    if (response.ok) {
        const user = await response.json()
        return user;
    }

    throw await getApiError(response, "Error. Please reload the page")
}


export default {login, logOut, getUserInfo}
