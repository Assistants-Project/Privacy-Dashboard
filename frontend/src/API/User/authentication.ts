import baseURL from "../baseUrl";

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
    } else {
        const errDetail = await response.json();
        // Flask-smorest validation error
        if (errDetail?.errors) {
            const jsonErrors = errDetail.errors.json;
            if (jsonErrors && typeof jsonErrors === 'object') {
                const msgs = Object.values(jsonErrors).flat().join('\n');
                throw new Error(msgs || 'Validation error');
            }
            if (typeof errDetail.errors === 'string') {
                throw new Error(errDetail.errors);
            }
        }
        if (errDetail?.message) {
            throw new Error(errDetail.message);
        }

        throw new Error("Something went wrong")
    }
}

async function logOut() {
    await fetch(baseURL + 'auth/logout', { method: 'POST', credentials: "include" });
}

async function getUserInfo() {
    const response = await fetch(baseURL + 'auth/current', { credentials: "include" })
    if (response.ok) {
        const user = await response.json()
        return user;
    } else {
        const errDetail = await response.json();
        if (errDetail.error)
            throw errDetail.error
        if (errDetail.message)
            throw errDetail.message
        throw new Error("Error. Please reload the page")
    }
}


export default {login, logOut, getUserInfo}
