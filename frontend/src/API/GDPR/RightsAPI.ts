import baseURL from "../baseUrl";
import { RequestStatus } from "../../models/request"
import { getApiError } from "../apiError";


async function getRequestsInbox(status?: RequestStatus) {
    const query = status ? `?status=${encodeURIComponent(status)}` : "";
    let response = await fetch(baseURL + `requests/${query}`, {
        method: "GET",
        credentials: "include",
    });
    if (response.ok) {
        const result = await response.json();
        return result;
    }

    throw await getApiError(response);

}

async function getRequestsHome(home_uuid: string, status?: RequestStatus) {
    const query = status ? `?status=${encodeURIComponent(status)}` : "";
    let response = await fetch(baseURL + `requests/home/${encodeURIComponent(home_uuid)}${query}`, {
        method: "GET",
        credentials: "include",
    });
    if (response.ok) {
        const result = await response.json();
        return result;
    }

    throw await getApiError(response);

}

type SubmitRequestDto = {
  right_type: string;
  additional_information: string;
  smart_home_uuid: string;
  application_uuid: string;
  selected_consents?: string[];
};

async function submitRequest(dto: SubmitRequestDto) {
    let response = await fetch(baseURL + "requests/submit", {
        method: "POST",
        credentials: "include",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(dto),
    });
    if (response.ok) {
        return await response.json();
    }

    throw await getApiError(response);
}

type HandleRequestDto = {
  status: string;
  response?: string;
};

async function handleRequest(request_uuid: string, dto: HandleRequestDto) {
    let response = await fetch(baseURL + `requests/handle/${encodeURIComponent(request_uuid)}`, {
        method: "PUT",
        credentials: "include",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(dto),
    });
    if (response.ok) {
        return await response.json();
    }

    throw await getApiError(response);
}

export {
    getRequestsInbox,
    getRequestsHome,
    submitRequest,
    handleRequest,
};

