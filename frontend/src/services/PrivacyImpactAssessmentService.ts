import {
  getPiaTemplate,
  getPiaByManagedApplicationUuid,
  submitPiaByManagedApplicationUuid,
  removePiaByManagedApplicationUuid,
} from "../API/Applications/applicationAPI";
import { PIA } from "../models/PIA";

type PIADto = {
  application_uuid: string,
  content: any
}

//cache del pia template in modo da non richiederla ogni volta (si assume che non cambia spesso)
let piaTemplateCache: any | undefined = undefined;

const toPIAModel = (pia: PIADto): PIA => {

  const model = new PIA(
    pia.application_uuid,
    pia.content
  );

  return model;
};


export const fetchPiaTemplate = async (force: boolean = false) => {
  if (!force && piaTemplateCache !== undefined) return piaTemplateCache;
  console.log("Trying to get Privacy Impact Assessment Template");
  const result = await getPiaTemplate();
  piaTemplateCache = result;
  console.log("Privacy Impact Assessment Template retrieved successfully");
  return result;
};

export const handleGetPrivacyImpactAssessment = async (applicationUuid: string): Promise<PIA | null> => {
    try {
      console.log(
        "Trying to get Privacy Impact Assessment for application: ",
        applicationUuid,
      );
      const result = await getPiaByManagedApplicationUuid(applicationUuid) as PIADto | null;
      console.log("Privacy Impact Assessment retrieved successfully");
      if (result === null) {
        return null
      }
      return toPIAModel(result);
    } catch (err) {
      throw err;
    }
  };

export const submitPiaTemplate = async (
    applicationUuid: string,
    piaTemplate: any,
  ): Promise<void> => {
    try {
      await submitPiaByManagedApplicationUuid(applicationUuid, piaTemplate);
      console.log("Privacy Impact Assessment submitted successfully");
    } catch (err) {
      throw err;
    }
  };

export const removePiaTemplate = async (
    applicationUuid: string,
  ): Promise<void> => {
    try {
      await removePiaByManagedApplicationUuid(applicationUuid);
      console.log("Privacy Impact Assessment removed successfully");
    } catch (err) {
      throw err;
    }
  };
