class AvailableConsentModel {
  uuid: string;
  content: string;

  constructor(uuid: string, content: string) {
    this.uuid = uuid;
    this.content = content;
  }
}

class GivenConsentInHomeModel {
  
  available_consent: AvailableConsentModel;
  application_uuid: string;
  given_at: string;

  constructor(available_consent: AvailableConsentModel,application_uuid: string,given_at: string) {
    
    this.available_consent = available_consent;
    this.application_uuid = application_uuid;
    this.given_at = given_at;
  }
}

export { AvailableConsentModel, GivenConsentInHomeModel };
