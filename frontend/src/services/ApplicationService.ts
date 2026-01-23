import {
  getManagedApplications,
} from "../API/Applications/applicationAPI";
  
const fetchManagedApplications = async () => {
    try {
      const applications = await getManagedApplications();
      return applications;
    } catch (err) {
      console.error("Error fetching managed applications:", err);
    }
  };

  export {fetchManagedApplications}