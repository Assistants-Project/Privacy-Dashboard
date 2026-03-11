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

async function register(email: string,firstname: string,lastname: string,password: string,role: string) {
    let response = await fetch(baseURL + "auth/register", {
        method: 'POST',
        credentials: "include",
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
            email: email, 
            password: password,
            role: role,
            firstname: firstname,
            lastname: lastname,
        })
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

async function delete_current() {
    const response = await fetch(baseURL + "auth/current", {
        method: "DELETE",
        credentials: "include",
    });
    if (response.ok) {
        //no payload
        return;
    }

    throw await getApiError(response);
}

async function updateCurrentUserProfile(payload: { current_password: string; email?: string; new_password?: string; }) {
    const response = await fetch(baseURL + "auth/current", {
        method: "PATCH",
        credentials: "include",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
    });
    if (response.ok) {
        const user = await response.json();
        return user;
    }

    throw await getApiError(response);
}

export default { login, logOut, getUserInfo, delete_current, register, updateCurrentUserProfile }
