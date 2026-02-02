import {
  getPrivacyNoticeTemplate,
  getPrivacyNoticeByManagedApplicationUuid,
  writePrivacyNoticeByManagedApplicationUuid,
  removePrivacyNoticeByManagedApplicationUuid,
  getPrivacyNoticeByInstalledApplicationUuid
} from "../API/GDPR/privacyNoticeAPI";

import {
  PrivacyNotice
} from "../models/privacy_notice"
import { Role } from "../models/user";

type PrivacyNoticeDto = {
  uuid: string,
  content: string
}


const toPrivacyNoticeModel = (privacy_notice: PrivacyNoticeDto): PrivacyNotice => {

  const model = new PrivacyNotice(
    privacy_notice.uuid,
    privacy_notice.content
  );

  return model;
};


export const fetchManagedPrivacyNotice = async (applicationUuid: string): Promise<PrivacyNotice | null> => {
  try {
    const privacy_notice = (await getPrivacyNoticeByManagedApplicationUuid(applicationUuid)) as PrivacyNoticeDto | null;
    if (privacy_notice === null) {
      return null
    }
    return toPrivacyNoticeModel(privacy_notice);
  } catch (err) {
     throw err
  }
};

export const fetchInstalledPrivacyNotice = async (applicationUuid: string): Promise<PrivacyNotice | null> => {
  try {
    const privacy_notice = (await getPrivacyNoticeByInstalledApplicationUuid(applicationUuid)) as PrivacyNoticeDto | null;
    if (privacy_notice === null) {
      return null
    }
    return toPrivacyNoticeModel(privacy_notice);
  } catch (err) {
     throw err
  }
};


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

export  const handleFetchPrivacyNotice = async (applicationUuid: string, role: Role) => {
    try {
      console.log(
        "Trying to get Privacy Notice for application: ",
        applicationUuid,
      );
      let result: PrivacyNotice | null;
      if (role === Role.DataSubject) {
        result = await fetchInstalledPrivacyNotice(applicationUuid)
      } else {
        result = await fetchManagedPrivacyNotice(applicationUuid)
      }
      //console.log("Privacy Notice retrieved successfully: ", result);
      return result;
    } catch (err) {
      throw err
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
