"use client";

import React, { useEffect, useMemo, useState } from "react";
import { IoCheckmark } from "react-icons/io5";
import { MdOutlineTimer } from "react-icons/md";
import { VscDebugRestart } from "react-icons/vsc";
import Button from "@/components/ui/Button";
import { apiCall } from "@/hooks/apiCall";
import toast from "react-hot-toast";
import { getErrorMessage } from "@/utils/errorHandler";
import Modal from "@/components/ui/Modal";
import { RxArrowTopRight } from "react-icons/rx";
import DataTable from "@/components/shared/data-table/DataTable";
import { LuCopy } from "react-icons/lu";
import { InputField, SelectInput, TextareaField } from "@/components/ui/Inputs";

const Steps = ({ breachData, refreshData }) => {
  const workflow = breachData?.workflow || [];
  const incidentId = breachData?._id;

  const mitigationSteps = breachData?.mitigation_steps || [];
  const dataElements = breachData?.data_element || [];

  const [dpData, setDpData] = useState([]);
  const [loading, setLoading] = useState(false);

  const [showAffectedPopulation, setShowAffectedPopulation] = useState(false);
  const [isManageWorkflowOpen, setIsManageWorkflowOpen] = useState(false);
  const [manageTab, setManageTab] = useState("addStep");
  const [newStageName, setNewStageName] = useState("");
  const [stepData, setStepData] = useState({
    stage_name: "",
    step_name: "",
    step_description: "",
  });

  const handleAddStep = async () => {
    if (
      !stepData.stage_name ||
      !stepData.step_name ||
      !stepData.step_description
    ) {
      toast.error("Please fill in all fields");
      return;
    }
    try {
      await apiCall(`/incidents/${incidentId}/add-step`, {
        method: "POST",
        data: {
          stage_name: stepData.stage_name,
          step: {
            step_name: stepData.step_name,
            step_description: stepData.step_description,
          },
        },
      });
      toast.success("Step added successfully");
      setStepData({ stage_name: "", step_name: "", step_description: "" });
      setIsManageWorkflowOpen(false);
      if (refreshData) refreshData();
    } catch (error) {
      toast.error(getErrorMessage(error));
    }
  };
  const handleCopy = (element, text) => {
    navigator.clipboard.writeText(element).then(() => {
      toast.success(`${text} copied Successfully`);
    });
  };

  const currentStageName = (breachData?.current_stage || "").toLowerCase();

  const initialIndex = useMemo(() => {
    if (!workflow.length) return 0;
    const idx = workflow.findIndex(
      (s) => s.stage_name.toLowerCase() === currentStageName
    );
    return idx === -1 ? 0 : idx;
  }, [currentStageName, workflow]);

  const [activeIndex, setActiveIndex] = useState(initialIndex);

  useEffect(() => {
    setActiveIndex(initialIndex);
  }, [initialIndex]);

  const fetchDpData = async () => {
    try {
      setLoading(true);
      const data = await apiCall(`/data-principal/search-data-principals`, {
        method: "POST",
        data: {
          filter: {
            data_elements: dataElements,
          },
        },
      });
      setDpData(data.data_principals);
      setLoading(false);
    } catch (error) {
      setLoading(false);
      console.error("Error fetching Dp data:", error);
    }
  };

  useEffect(() => {
    fetchDpData();
  }, []);

  const isLast = activeIndex === workflow.length - 1;

  const handleNextStage = async () => {
    if (isLast) return;

    try {
      await apiCall(`/incidents/${incidentId}/move-to-next-stage`, {
        method: "POST",
      });
      toast.success("Moved to next stage successfully");
      setActiveIndex((prev) => prev + 1);
    } catch (error) {
      toast.error(getErrorMessage(error));
    }
  };

  const handleSendNotification = async () => {
    try {
      await apiCall(`/incidents/send-notification/${incidentId}`, {
        method: "POST",
      });
      toast.success("Notification sent successfully");
    } catch (error) {
      toast.error(getErrorMessage(error));
    }
  };

  if (!workflow.length) {
    return (
      <div className="flex h-full items-center justify-center text-gray-500">
        No workflow data available.
      </div>
    );
  }

  const currentStage = workflow[activeIndex];

  const updatedStages = workflow.map((stage, index) => ({
    ...stage,
    isCompleted: index <= activeIndex,
  }));

  const userColumns = [
    {
      header: "DP ID",
      accessor: "dp_id",
      headerClassName: "pl-3 text-left w-40 ",
      render: (element) => {
        return (
          <div
            className="group flex cursor-default items-center space-x-2 pl-3"
            onClick={(e) => e.stopPropagation()}
          >
            <span>{element.slice(0, 8)}</span>
            <button
              onClick={() => handleCopy(element, "ID")}
              className="relative text-sm text-blue-500 opacity-0 hover:underline focus:outline-none group-hover:opacity-100"
            >
              <LuCopy size={16} />
            </button>
          </div>
        );
      },
    },

    {
      header: "Email",
      accessor: "dp_email",
      headerClassName: " text-left",
      render: (element) => {
        const hasData = Array.isArray(element) && element.length > 0;

        return (
          <div
            className="group mr-2 flex cursor-default"
            onClick={(e) => e.stopPropagation()}
          >
            <span className="flex flex-col">
              {[...(hasData ? element.slice(0, 2) : [])]
                .reverse()
                .map((item, index) => (
                  <span
                    key={index}
                    className={`${index === 0 && "font-semibold"}`}
                  >
                    {item}
                  </span>
                ))}
            </span>

            {hasData ? (
              <button
                onClick={() => handleCopy(element, "Email")}
                className="ml-1 text-sm text-blue-500 opacity-0 hover:underline focus:outline-none group-hover:opacity-100"
              >
                <LuCopy />
              </button>
            ) : (
              <span className="ml-2 text-sm text-gray-400">-</span>
            )}
          </div>
        );
      },
    },
    {
      header: "Mobile",
      accessor: "dp_mobile",
      headerClassName: "text-center",
      render: (element) => {
        const hasData = Array.isArray(element) && element.length > 0;

        return (
          <div className="mx-2 flex flex-col items-center justify-center gap-0.5">
            {hasData ? (
              [...element.slice(0, 2)].reverse().map((item, index) => (
                <span
                  key={index}
                  className={`${index === 0 && "font-semibold"}`}
                >
                  {item}
                </span>
              ))
            ) : (
              <span className="text-sm text-gray-400"> - </span>
            )}
          </div>
        );
      },
    },
    {
      header: "Country",
      accessor: "dp_country",
      headerClassName: "text-center w-40",
      render: (element) => {
        return (
          <div className="flex items-center justify-center capitalize">
            {element}
          </div>
        );
      },
    },
    {
      header: "State",
      accessor: "dp_state",
      headerClassName: "text-center w-40",
      render: (element) => {
        const formattedState = element ? element.replace(/-/g, " ") : "-";
        return (
          <div className="flex flex-nowrap items-center justify-center capitalize">
            {formattedState || <span className="text-sm text-gray-400">-</span>}
          </div>
        );
      },
    },
  ];

  return (
    <div className="h-[calc(100vh-175px)] w-full">
      <div className="flex flex-col px-6 sm:flex sm:flex-row h-full">
        <div className="h-full w-full border-r border-borderheader px-1 py-2 lg:w-[30%] overflow-y-auto">
          {updatedStages.map((stage, index) => (
            <div key={index}>
              <div className="flex items-center gap-5">
                <div
                  className={`flex min-h-8 min-w-8 items-center justify-center rounded-full text-white ${
                    stage.isCompleted
                      ? "bg-primary"
                      : "border border-[#A1AEBE] text-[#242E39]"
                  }`}
                >
                  {stage.isCompleted ? (
                    <IoCheckmark size={15} />
                  ) : (
                    <span className="text-black">{index + 1}</span>
                  )}
                </div>
                <div className="mt-2">
                  <h1
                    className={`font-lato text-[16px] capitalize ${
                      index === activeIndex
                        ? "text-primary font-bold"
                        : stage.isCompleted
                        ? "text-primary/90"
                        : "text-[#242E39]"
                    }`}
                  >
                    {stage.stage_name}
                  </h1>
                  <p className="text-sm font-medium text-[#595959]">
                    {stage.stage_name === "notifying"
                      ? "Notify"
                      : "" || stage.stage_name === "closure"
                      ? "Closure"
                      : stage.steps?.length
                      ? stage.steps?.length + " Steps"
                      : ""}
                  </p>
                </div>
              </div>

              {index < updatedStages.length - 1 && (
                <div
                  className={`ml-4 h-6 w-0 outline-dashed outline-[1.3px] ${
                    index < activeIndex
                      ? "outline-primary"
                      : "outline-[#6B7280]"
                  }`}
                />
              )}
            </div>
          ))}
        </div>

        <div className="flex-1 p-4 flex flex-col h-full">
          <div className="flex-1 overflow-y-auto mb-4">
            <h2 className="text-xl font-bold mb-6 text-[#242E39] capitalize">
              {currentStage.stage_name}
            </h2>
            <div className="space-y-4">
              {currentStage.stage_name?.toLowerCase() === "notifying" ? (
                <div>
                  <div className="flex items-center border border-gray-300 p-2 mb-2">
                    <div className="w-[80%]">
                      Affected Data Elements
                      <div className="flex gap-2">
                        {breachData?.data_element?.map((element, index) => (
                          <div
                            className="flex items-center gap-2 border text-sm bg-gray-50 border-gray-300 p-2"
                            key={index}
                          >
                            <div>{element}</div>
                          </div>
                        ))}
                      </div>
                    </div>
                    <div className="w-[20%]">
                      <div className="flex items-center gap-2">
                        <span>Affected Users</span>
                        <Button
                          variant="icon"
                          onClick={() => setShowAffectedPopulation(true)}
                        >
                          <RxArrowTopRight size={16} />
                        </Button>
                      </div>
                      <div className="flex items-center gap-2 border text-sm bg-gray-50 border-gray-300 p-2">
                        {breachData?.affected_population}
                      </div>
                    </div>
                  </div>
                  {mitigationSteps.length > 0 ? (
                    mitigationSteps.map((step, sIdx) => (
                      <div
                        key={sIdx}
                        className="p-4 border border-borderheader bg-white hover:shadow-sm transition-shadow"
                      >
                        <h3 className="font-base text-lg text-[#242E39] mb-1">
                          Mitigation Step {sIdx + 1}
                        </h3>
                        <p className="text-gray-600 text-base">{step}</p>
                      </div>
                    ))
                  ) : (
                    <p className="text-gray-500 italic">
                      No mitigation steps available.
                    </p>
                  )}
                </div>
              ) : currentStage?.stage_name?.toLowerCase() === "closure" ? (
                <div className="p-4 border border-borderheader bg-white">
                  <p className="text-gray-600 text-sm">
                    This breach incident has been closed now and below is the
                    notification that has been sent to the users.
                  </p>
                </div>
              ) : (
                <>
                  {currentStage?.steps?.map((step, sIdx) => (
                    <div
                      key={sIdx}
                      className="p-4 border border-borderheader bg-white hover:shadow-sm transition-shadow"
                    >
                      <h3 className="font-semibold text-lg text-[#242E39] mb-1">
                        {step.step_name}
                      </h3>
                      <p className="text-gray-600 text-sm">
                        {step.step_description}
                      </p>
                    </div>
                  ))}
                  {(!currentStage.steps || currentStage.steps.length === 0) && (
                    <p className="text-gray-500 italic">
                      No steps defined for this stage.
                    </p>
                  )}
                </>
              )}
            </div>
          </div>

          <div className="flex items-center justify-between gap-3 border-t border-borderheader pt-4">
            <div className="flex items-center gap-4 text-sm text-[#4B5563]">
              <span className="inline-flex items-center gap-1">
                <MdOutlineTimer /> Stage {activeIndex + 1} of {workflow.length}
              </span>
              {!isLast ? (
                <span className="inline-flex items-center gap-1">
                  <VscDebugRestart /> Next:{" "}
                  {workflow[activeIndex + 1].stage_name}
                </span>
              ) : (
                <span className="inline-flex items-center gap-1">
                  <IoCheckmark /> Workflow Completed
                </span>
              )}
            </div>

            <div className="flex gap-2">
              <Button
                variant="secondary"
                className="w-40"
                onClick={() => setIsManageWorkflowOpen(true)}
              >
                Manage Workflow
              </Button>
              {!isLast && (
                <Button
                  variant="primary"
                  className="w-40"
                  onClick={handleNextStage}
                  title="Move to next stage"
                >
                  Next Stage
                </Button>
              )}
              {isLast && (
                <Button
                  variant="primary"
                  className="w-40"
                  onClick={handleSendNotification}
                  title="Send Notifications"
                >
                  Send Notifications
                </Button>
              )}
            </div>
          </div>
        </div>
      </div>
      <Modal
        isOpen={showAffectedPopulation}
        onClose={() => setShowAffectedPopulation(false)}
        title="Affected Population"
        width="1000px"
      >
        <DataTable
          tableHeight={"213.5px"}
          columns={userColumns}
          data={dpData}
          loading={loading}
          hidePagination={true}
          hideSearchBar={true}
          hasSerialNumber={false}
          illustrationText="No Data Principal Found"
          illustrationImage="/assets/illustrations/no-data-find.png"
          noDataText="No Data Principal Found"
          noDataImage="/assets/illustrations/no-data-find.png"
        />
      </Modal>

      <Modal
        isOpen={isManageWorkflowOpen}
        onClose={() => setIsManageWorkflowOpen(false)}
        title="Manage Workflow"
        width="600px"
      >
        <div className="flex flex-col gap-4">
         
          {manageTab === "addStep" && (
            <div className="flex flex-col gap-4">
              <SelectInput
                label="Select Stage"
                options={workflow.map((s) => ({
                  label: s.stage_name,
                  value: s.stage_name,
                }))}
                value={
                  stepData.stage_name
                    ? {
                        label: stepData.stage_name,
                        value: stepData.stage_name,
                      }
                    : null
                }
                onChange={(opt) =>
                  setStepData((prev) => ({ ...prev, stage_name: opt.value }))
                }
                placeholder="Select a stage"
              />
              <InputField
                label="Step Name"
                placeholder="Enter step name"
                value={stepData.step_name}
                onChange={(e) =>
                  setStepData((prev) => ({
                    ...prev,
                    step_name: e.target.value,
                  }))
                }
              />
              <TextareaField
                label="Step Description"
                placeholder="Enter step description"
                value={stepData.step_description}
                onChange={(e) =>
                  setStepData((prev) => ({
                    ...prev,
                    step_description: e.target.value,
                  }))
                }
              />
              <Button onClick={handleAddStep}>Add Step</Button>
            </div>
          )}
        </div>
      </Modal>
    </div>
  );
};

export default Steps;
