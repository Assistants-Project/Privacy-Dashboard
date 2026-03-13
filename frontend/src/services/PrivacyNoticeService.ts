import {
  getPrivacyNoticeTemplate,
  getPrivacyNoticeByManagedApplicationUuid,
  removePrivacyNoticeByManagedApplicationUuid,
  getPrivacyNoticeByInstalledApplicationUuid,
  submitPrivacyNoticeByManagedApplicationUuid,
  associatePrivacyNoticeByManagedApplicationUuid,
} from "../API/GDPR/privacyNoticeAPI";

import { PrivacyNoticeModel } from "../models/privacy_notice";
import { Role } from "../models/user";

type PrivacyNoticeDto = {
  uuid: string;
  content: string;
};

const toPrivacyNoticeModel = (
  privacy_notice: PrivacyNoticeDto,
): PrivacyNoticeModel => {
  const model = new PrivacyNoticeModel(privacy_notice.uuid, privacy_notice.content);

  return model;
};

export const fetchManagedPrivacyNotice = async (
  applicationUuid: string,
): Promise<PrivacyNoticeModel | null> => {
  try {
    const privacy_notice = (await getPrivacyNoticeByManagedApplicationUuid(
      applicationUuid,
    )) as PrivacyNoticeDto | null;
    if (privacy_notice === null) {
      return null;
    }
    return toPrivacyNoticeModel(privacy_notice);
  } catch (err) {
    throw err;
  }
};

export const fetchInstalledPrivacyNotice = async (
  applicationUuid: string,
): Promise<PrivacyNoticeModel | null> => {
  try {
    const privacy_notice = (await getPrivacyNoticeByInstalledApplicationUuid(
      applicationUuid,
    )) as PrivacyNoticeDto | null;
    if (privacy_notice === null) {
      return null;
    }
    return toPrivacyNoticeModel(privacy_notice);
  } catch (err) {
    throw err;
  }
};

export const fetchPrivacyNoticeTemplate = async () => {
  try {
    const result = await getPrivacyNoticeTemplate();
    console.log("Privacy Notice Template retrieved successfully: ", result);
    return result;
  } catch (err) {
    console.error("Error getting privacy notice template:", err);
  }
};

//se presente allora PN è available, se null non è disponibile per quell'app
//se ci fosse un errore nel fetch viene propagato al chiamante (apps context) che lo gestisce di conseguenza
export const handleFetchPrivacyNotice = async (
  applicationUuid: string,
  role: Role,
): Promise<PrivacyNoticeModel | null> => {
  try {
    let result: PrivacyNoticeModel | null;
    if (role === Role.DataSubject) {
      result = await fetchInstalledPrivacyNotice(applicationUuid);
    } else {
      result = await fetchManagedPrivacyNotice(applicationUuid);
    }
    //console.log("Privacy Notice retrieved successfully: ", result);
    return result;
  } catch (err) {
    throw err;
  }
};

export const handleSubmitPrivacyNotice = async (
  applicationUuid: string,
  privacyNoticeContent: string,
): Promise<PrivacyNoticeModel> => {
  try {
    const result = await submitPrivacyNoticeByManagedApplicationUuid(
      applicationUuid,
      privacyNoticeContent,
    );
    console.log("Privacy Notice submitted successfully");
    return result;
  } catch (err) {
    throw err;
  }
};

export const handleRemovePrivacyNotice = async (applicationUuid: string) => {
  try {
    await removePrivacyNoticeByManagedApplicationUuid(applicationUuid);
    console.log("Existing privacy notice removed from application.");
  } catch (err) {
    console.error("Error removing privacy notice:", err);
    throw err;
  }
};

export const handleReplacePrivacyNoticeWithExisting = async (
  targetApplicationUuid: string,
  privacyNoticeUuid: string,
): Promise<PrivacyNoticeModel> => {
  const result = await associatePrivacyNoticeByManagedApplicationUuid(
    targetApplicationUuid,
    privacyNoticeUuid,
  );
  return toPrivacyNoticeModel(result as PrivacyNoticeDto);
};
