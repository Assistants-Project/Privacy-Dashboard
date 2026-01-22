import baseURL from "./baseUrl";

async function getHomes() {
  let response = await fetch(baseURL + "/homes", {
    method: "GET",
    credentials: "include",
  });
  if (response.ok) {
    const homes = await response.json();
    return homes;
  } else {
    const errDetail = await response.json();
    if (errDetail?.message) {
      throw new Error(errDetail.message);
    }
    throw new Error("Something went wrong");
  }
}

async function getHomeRooms(homeUuid: string) {
  let response = await fetch(`${baseURL}/homes/${homeUuid}/rooms`, {
    method: "GET",
    credentials: "include",
  });
  if (response.ok) {
    return await response.json();
  } else {
    const errDetail = await response.json();
    if (errDetail?.message) {
      throw new Error(errDetail.message);
    }
    throw new Error("Something went wrong");
  }
}

export { getHomes, getHomeRooms };
