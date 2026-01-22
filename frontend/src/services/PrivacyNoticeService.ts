import {
  getPrivacyNoticeTemplate,
  getPrivacyNoticeByManagedApplicationUuid,
  writePrivacyNoticeByManagedApplicationUuid,
  removePrivacyNoticeByManagedApplicationUuid,
} from "../API/privacyNoticeAPI";


export const fetchPrivacyNoticeTemplate = async () => {
    try {
      console.log("Trying to get Privacy Notice Template");
      const result = await getPrivacyNoticeTemplate();
      console.log("Privacy Notice Template retrieved successfully: ", result);
      return result;
    } catch (err) {
      console.error("Error getting privacy notice template:", err);
    }
  };

export  const handleGetPrivacyNotice = async (applicationUuid: string) => {
    try {
      console.log(
        "Trying to get Privacy Notice for application: ",
        applicationUuid,
      );
      const result =
        await getPrivacyNoticeByManagedApplicationUuid(applicationUuid);
      console.log("Privacy Notice retrieved successfully: ", result);
      return result;
    } catch (err) {
      console.error("Error getting privacy notice:", err);
    }
  };

export const handleSubmitPrivacyNotice = async (
    applicationUuid: string,
    privacyNoticeContent: string,
  ) => {
    try {
      console.log(
        "Trying to submit Privacy Notice to application: ",
        applicationUuid,
        privacyNoticeContent,
      );
      const result = await writePrivacyNoticeByManagedApplicationUuid(
        applicationUuid,
        privacyNoticeContent,
      );
      console.log("Privacy Notice submitted successfully: ", result);
      return result;
    } catch (err) {
      console.error("Error submitting privacy notice:", err);
    }
  };

export  const handleRemovePrivacyNotice = async (applicationUuid: string) => {
    try {
      console.log(
        "Trying to delete existing privacy notice for application: ",
        applicationUuid,
      );
      await removePrivacyNoticeByManagedApplicationUuid(applicationUuid);
      console.log("Existing privacy notice deleted.");
    } catch (err) {
      console.error("Error deleting privacy notice:", err);
    }
  };