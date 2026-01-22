import {
  getPiaTemplate,
  getPiaByManagedApplicationUuid,
  submitPiaByManagedApplicationUuid,
} from "../API/applicationAPI";


export const fetchPiaTemplate = async () => {
    try {
      console.log("Trying to get Privacy Impact Assessment Template");
      const result = await getPiaTemplate();
      console.log("Privacy Impact Assessment Template retrieved successfully");
      return result;
    } catch (err) {
      console.error("Error getting privacy impact assessment template:", err);
    }
  };

export const handleGetPrivacyImpactAssessment = async (applicationUuid: string) => {
    try {
      console.log(
        "Trying to get Privacy Impact Assessment for application: ",
        applicationUuid,
      );
      const result = await getPiaByManagedApplicationUuid(applicationUuid);
      console.log("Privacy Impact Assessment retrieved successfully");
      return result;
    } catch (err) {
      console.error("Error getting privacy impact assessment:", err);
    }
  };

export const submitPiaTemplate = async (
    applicationUuid: string,
    piaTemplate: any,
  ) => {
    try {
      await submitPiaByManagedApplicationUuid(applicationUuid, piaTemplate);
      console.log("Privacy Impact Assessment submitted successfully");
      return;
    } catch (err) {
      console.error("Error submitting privacy impact assessment:", err);
    }
  };