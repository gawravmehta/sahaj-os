import Button from "@/components/ui/Button";
import { InputField, SelectInput } from "@/components/ui/Inputs";
import Skeleton from "@/components/ui/Skeleton";
import Tag from "@/components/ui/Tag";
import { lawfulBasisOptions } from "@/constants/vendorOptions";
import { apiCall } from "@/hooks/apiCall";
import React, { useEffect, useState } from "react";

const DataProcessing = ({ vendorData, loading }) => {
  const [editingDataProcessing, setEditingDataProcessing] = useState(false);
  const [purposeOptions, setPurposeOptions] = useState([]);
  const [dataElementsOptions, setDataElementsOptions] = useState([]);

  const [data_processing_activity, setData_processing_activity] = useState(
    vendorData?.data_processing_activity || []
  );

  useEffect(() => {
    getAllDataPurpose();
    getAllDataElement();
  }, []);

  const getAllDataPurpose = async () => {
    let URL = `/purposes/get-all-purposes`;

    try {
      const response = await apiCall(URL);

      const purposesData = response.purposes || response.data || [];

      setPurposeOptions(
        purposesData
          ?.filter((data) => data.purpose_id && data.purpose_title)
          ?.map((data) => ({
            value: data.purpose_id,
            label: data.purpose_title,
          }))
      );
    } catch (error) {
      toast.error(message);
    }
  };

  const getAllDataElement = async () => {
    try {
      const response = await apiCall(
        "/data-elements/get-all-data-element?status=published"
      );
      if (response) {
        const dataElements = response.data || response.data_elements || [];

        setDataElementsOptions(
          dataElements
            ?.filter((data) => data?.de_id && data?.de_name)
            ?.map((data) => ({
              value: data?.de_id,
              label: data?.de_name,
            })) || []
        );
      }
    } catch (error) {
      setDataElementsOptions([]);
    }
  };

  const handleSubmit = () => {
    try {
      const response = apiCall(
        `/vendor/edit-data-processing-activities/${vendorData._id}`,
        {
          method: "PATCH",
          data: data_processing_activity,
        }
      );
    } catch (error) {
      console.error("Error submitting data processing activity:", error);
    }
  };

  return (
    <div className="custom-scrollbar mx-auto mt-4 h-[calc(100vh-190px)] w-full max-w-2xl space-y-4 overflow-auto pb-6">
      <div className="flex flex-col gap-2">
        <span className="flex items-center justify-between  text-subHeading">
          <h1> Processing Category:</h1>
        </span>
        <div className="flex flex-wrap gap-2">
          {!loading ? (
            vendorData?.processing_category?.map((tag, index) => (
              <Tag
                key={index}
                className="text-xs"
                variant="outlineBlue"
                label={tag.replace(/_/g, " ")}
              />
            ))
          ) : (
            <Skeleton variant="single" />
          )}
        </div>
      </div>
      <div className="flex flex-col gap-2">
        <span className="flex items-center justify-between  text-subHeading">
          <h1> Data Categories: </h1>
        </span>
        <div className="flex flex-wrap gap-2">
          {!loading ? (
            vendorData?.data_categories?.map((tag, index) => (
              <Tag
                key={index}
                className="text-xs"
                variant="outlineBlue"
                label={tag.replace(/_/g, " ")}
              />
            ))
          ) : (
            <Skeleton variant="single" />
          )}
        </div>
      </div>
      {!editingDataProcessing && (
        <div className="flex justify-end">
          <Button onClick={() => setEditingDataProcessing(true)}>
            Edit Processing Activity
          </Button>
        </div>
      )}
      {editingDataProcessing && (
        <div>
          <SelectInput
            name="dpr_security_policy"
            label="Purpose"
            options={purposeOptions}
            className="mb-0.5"
            isMulti={true}
            value={purposeOptions.filter((option) =>
              data_processing_activity.some(
                (activity) => activity.purpose_id === option.value
              )
            )}
            disabled={true}
            onChange={(selected) => {
              const selectedPurposes = selected || [];
              const updatedActivities = selectedPurposes.map((p) => {
                const existing = data_processing_activity.find(
                  (a) => a.purpose_id === p.value
                );
                return (
                  existing || {
                    activity_name: "",
                    purpose_id: p.value,
                    purpose: p.label,
                    lawful_basis: "",
                    data_elements: [],
                    frequency: "",
                    storage_location: "",
                  }
                );
              });
              setData_processing_activity(updatedActivities);
            }}
            placeholder="Select Purposes"
            tooltipText="Why this activity is carried out."
          />

          {data_processing_activity.length > 0 &&
            data_processing_activity?.map((activity, index) => (
              <div
                key={activity.purpose_id}
                className="border border-[#d4d1d1] p-3 my-2 flex flex-col gap-3"
              >
                <h4 className=" mb-2">
                  <span className="font-semibold">For Purpose</span> :{" "}
                  {activity.purpose}
                </h4>

                <InputField
                  name={`activity_name_${index}`}
                  label="Activity Name"
                  placeholder={"Enter Activity Name"}
                  value={activity.activity_name}
                  onChange={(e) => {
                    const updated = [...data_processing_activity];
                    updated[index].activity_name = e.target.value;
                    setData_processing_activity(updated);
                  }}
                />

                <SelectInput
                  name={`lawful_basis_${index}`}
                  label="Lawful Basis"
                  placeholder={"Select Lawful Basis"}
                  options={lawfulBasisOptions}
                  value={
                    lawfulBasisOptions.find(
                      (opt) => opt.value === activity.lawful_basis
                    ) || null
                  }
                  onChange={(selected) => {
                    const updated = [...data_processing_activity];
                    updated[index].lawful_basis = selected?.value || "";
                    setData_processing_activity(updated);
                  }}
                />

                <SelectInput
                  name={`data_elements_${index}`}
                  label="Data Elements"
                  options={dataElementsOptions}
                  isMulti={true}
                  placeholder={"Select Data Elements"}
                  value={dataElementsOptions.filter((opt) =>
                    activity.data_elements.includes(opt.value)
                  )}
                  onChange={(selected) => {
                    const updated = [...data_processing_activity];
                    updated[index].data_elements = selected
                      ? selected.map((s) => s.value)
                      : [];
                    setData_processing_activity(updated);
                  }}
                />

                <InputField
                  name={`frequency_${index}`}
                  label="Frequency"
                  placeholder="Enter Frequency"
                  value={activity.frequency}
                  onChange={(e) => {
                    const updated = [...data_processing_activity];
                    updated[index].frequency = e.target.value;
                    setData_processing_activity(updated);
                  }}
                />

                <InputField
                  name={`storage_location_${index}`}
                  label="Storage Location"
                  placeholder="Enter Storage Location"
                  value={activity.storage_location}
                  onChange={(e) => {
                    const updated = [...data_processing_activity];
                    updated[index].storage_location = e.target.value;
                    setData_processing_activity(updated);
                  }}
                />
              </div>
            ))}
        </div>
      )}

      {editingDataProcessing && (
        <div className="flex items-center justify-end gap-4">
          <Button onClick={handleSubmit}>Submit</Button>
          <Button
            variant="secondary"
            onClick={() => setEditingDataProcessing(false)}
          >
            Cancel
          </Button>
        </div>
      )}
      {!editingDataProcessing && (
        <div className="flex flex-col gap-2">
          <div>
            <span className="flex items-center justify-between  text-subHeading">
              <h1>Activity: </h1>
            </span>

            {vendorData?.data_processing_activity?.map((activity, i) =>
              !loading ? (
                <p key={i}>{activity.activity_name}</p>
              ) : (
                <div key={i}>
                  <Skeleton variant="single" className={"h-4 w-64"} />
                </div>
              )
            )}
          </div>
          <div>
            <span className="flex items-center justify-between  text-subHeading">
              <h1>Purpose: </h1>
            </span>
            {vendorData?.data_processing_activity?.map((activity, i) =>
              !loading ? (
                <p key={i} className="capitalize">
                  {activity.purpose}
                </p>
              ) : (
                <div key={i}>
                  <Skeleton variant="single" className={"h-4 w-64"} />
                </div>
              )
            )}
          </div>
          <div>
            <span className="flex items-center justify-between  text-subHeading">
              <h1> Lawful Basis: </h1>
            </span>
            {vendorData?.data_processing_activity?.map((activity, i) =>
              !loading ? (
                <p key={i} className="capitalize">
                  {activity.lawful_basis.replace(/_/g, " ")}
                </p>
              ) : (
                <div key={i}>
                  <Skeleton variant="single" className={"h-4 w-64"} />
                </div>
              )
            )}
          </div>
          <div className="flex flex-col gap-2">
            <span className="flex items-center justify-between  text-subHeading">
              <h1>Data Elements: </h1>
            </span>
            <div className="flex flex-wrap gap-2">
              {vendorData?.data_processing_activity?.map((activity, i) =>
                !loading ? (
                  activity.data_elements.map((element, index) => (
                    <Tag
                      key={`${i}-${index}`}
                      className="text-xs"
                      variant="outlineBlue"
                      label={element}
                    />
                  ))
                ) : (
                  <Skeleton key={i} variant="single" />
                )
              )}
            </div>
          </div>
          <div className="flex items-center justify-between">
            <div>
              <span className="flex items-center justify-between  text-subHeading">
                <h1>Frequency: </h1>
              </span>
              {vendorData?.data_processing_activity?.map((activity, i) =>
                !loading ? (
                  <p key={i} className="capitalize">
                    {activity.frequency}
                  </p>
                ) : (
                  <div key={i}>
                    <div key={i}>
                      <Skeleton variant="single" className={"h-4 w-64"} />
                    </div>
                  </div>
                )
              )}
            </div>
            <div>
              <span className="flex items-center justify-between  text-subHeading">
                <h1>Storage Location: </h1>
              </span>
              {vendorData?.data_processing_activity?.map((activity, i) =>
                !loading ? (
                  <p key={i} className="capitalize">
                    {activity.storage_location}
                  </p>
                ) : (
                  <div key={i}>
                    <Skeleton variant="single" className={"h-4 w-64"} />
                  </div>
                )
              )}
            </div>
          </div>
        </div>
      )}
      <div>
        <span className="flex items-center justify-between  text-subHeading">
          <h1>Data Retention Policy: </h1>
        </span>
        {!loading ? (
          <p className="capitalize">{vendorData?.data_retention_policy}</p>
        ) : (
          <Skeleton variant="single" className={"h-4 w-28"} />
        )}
      </div>

      <div className="flex items-center justify-between">
        <div>
          <span className="flex items-center justify-between  text-subHeading">
            <h1>Data Location: </h1>
          </span>
          {vendorData?.data_location?.map((location, i) =>
            !loading ? (
              <p key={i} className="capitalize">
                {location}
              </p>
            ) : (
              <div key={i}>
                <Skeleton variant="single" className={"h-4 w-64"} />
              </div>
            )
          )}
        </div>
        <div>
          <span className="flex items-center justify-between  text-subHeading">
            <h1>Cross Border: </h1>
          </span>
          {!loading ? (
            <p>{vendorData.cross_border === false ? "No" : "Yes"}</p>
          ) : (
            <Skeleton variant="single" className={"h-4 w-28"} />
          )}
        </div>
      </div>

      <div>
        <span className="flex items-center justify-between  text-subHeading">
          <h1>Sub-processors: </h1>
        </span>
        {vendorData?.sub_processors?.map((processors, i) =>
          !loading ? (
            <p key={i} className="mb-1">
              {" "}
              {i + 1}. {processors}
            </p>
          ) : (
            <div key={i}>
              <Skeleton variant="single" className={"h-4 w-64"} />
            </div>
          )
        )}
      </div>
    </div>
  );
};

export default DataProcessing;
