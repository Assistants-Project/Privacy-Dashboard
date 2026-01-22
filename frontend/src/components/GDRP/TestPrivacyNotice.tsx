import {
  Button,
  FormSelect,
  ToggleButton,
  ToggleButtonGroup,
} from "react-bootstrap";
import { useState, useEffect } from "react";
import ReactQuill from "react-quill";
import {
  fetchPrivacyNoticeTemplate,
  handleGetPrivacyNotice,
  handleSubmitPrivacyNotice,
  handleRemovePrivacyNotice
} from "../../services/PrivacyNoticeService";
import "react-quill/dist/quill.snow.css";

function TestPrivacyNotice(props: any) {
  const [value, setValue] = useState("");
  const [isTemplate, setIsTemplate] = useState<number>(0); // 0 = none, 1 = scratch, 2 = template

  // TODO: move this application fetching logic elsewhere and pass data here via props if needed
  const [managedApplications, setManagedApplications] = useState<any[]>([]);
  const [selectedApplicationUuid, setSelectedApplicationUuid] =
    useState<string>("");

  const [fetchedNotice, setFetchedNotice] = useState<any>("");

  useEffect(() => {
    const fetchData = async () => {
      const applications = await props.fetchManagedApplications();
      setManagedApplications(applications || []);
    };
    fetchData();
  }, []);

  useEffect(() => {
    const setValueToTemplate = async () => {
      const template = await fetchPrivacyNoticeTemplate();
      setValue(template?.content || "");
    };
    if (isTemplate === 2) {
      setValueToTemplate();
    } else {
      setValue("");
    }
  }, [isTemplate]);

  const handleSubmit = async () => {
    if (!selectedApplicationUuid) {
      alert("Please select an application.");
      return;
    }
    try {
      // TODO: for semplicity, we first remove any existing privacy notice before submitting a new one, REMOVE THIS!
      await handleRemovePrivacyNotice(selectedApplicationUuid);
      const submittedNotice = await handleSubmitPrivacyNotice(
        selectedApplicationUuid,
        value
      );
      // TODO: for simplicity, we fetch directly here the submitted privacy notice to verify it was stored correctly, REMOVE THIS!
      const fetchedNoticeResult = await handleGetPrivacyNotice(
        selectedApplicationUuid
      );
      console.log("Submitted Notice:", submittedNotice.uuid);
      console.log("Fetched Notice:", fetchedNoticeResult.uuid);
      if (
        submittedNotice &&
        fetchedNoticeResult &&
        submittedNotice.uuid === fetchedNoticeResult.uuid
      ) {
        setFetchedNotice(fetchedNoticeResult);
        setSelectedApplicationUuid("");
        setIsTemplate(0);
        setValue("");
      } else {
        alert("Error verifying the submitted Privacy Notice.");
      }
    } catch (err) {
      console.error("Error submitting privacy notice:", err);
    }
  };

  return (
    <div className="d-flex flex-column align-items-center p-4">
      <h1>Privacy Notice</h1>
      <div className="w-50">
        <p>Choose a managed application to submit a privacy notice for:</p>
        <FormSelect
          className="mb-3"
          onChange={(e) => setSelectedApplicationUuid(e.target.value)}
          value={selectedApplicationUuid}
        >
          <option className="d-none" value="" disabled>
            Select an application
          </option>
          {managedApplications.map((app) => (
            <option key={app.application.uuid} value={app.application.uuid}>
              {app.application.name}
            </option>
          ))}
        </FormSelect>
        <p>Choose whether to write from scratch or from a provided template:</p>
        <ToggleButtonGroup
          type="radio"
          name="options"
          defaultValue={0}
          onChange={(val) => setIsTemplate(val)}
        >
          <ToggleButton id="tbg-radio-1" variant="outline-dark" value={1}>
            Scratch
          </ToggleButton>
          <ToggleButton id="tbg-radio-2" variant="outline-dark" value={2}>
            Template
          </ToggleButton>
        </ToggleButtonGroup>
        {isTemplate > 0 && (
          <div className="my-3 p-3 border rounded">
            <ReactQuill
              className="mb-3"
              theme="snow"
              value={value}
              onChange={setValue}
            />
            <Button variant="dark" onClick={handleSubmit} className="mt-3">
              Submit Privacy Notice
            </Button>
          </div>
        )}
      </div>
      {fetchedNotice && fetchedNotice.uuid && fetchedNotice.content && (
        <div className="mt-4 p-3 border rounded w-50">
          <h4>Privacy Notice Submitted Successfully!</h4>
          <p>UUID: {fetchedNotice.uuid}</p>
          <div dangerouslySetInnerHTML={{ __html: fetchedNotice.content }} />
        </div>
      )}
      <Button variant="secondary" onClick={props.onLogout} className="mt-3">
        Logout
      </Button>
    </div>
  );
}

export { TestPrivacyNotice };
