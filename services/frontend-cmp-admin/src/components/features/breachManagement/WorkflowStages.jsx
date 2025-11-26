import Button from "@/components/ui/Button";
import {
  CreatableInputs,
  InputField,
  TextareaField,
} from "@/components/ui/Inputs";
import { stageOptions } from "@/constants/breachManagementOptions";
import React from "react";
import { FaTrash } from "react-icons/fa";
import { FiPlus } from "react-icons/fi";

const WorkflowStages = ({
  formData,
  setFormData,
  handleInputChange,
  missingFields,
}) => {
  const handleStageChange = (newValue) => {
    const currentStages = formData.workflow || [];

    const updatedWorkflow = newValue.map((v) => {
      const existing = currentStages.find((s) => s.stage_name === v.value);
      return existing || { stage_name: v.value, steps: [] };
    });

    handleInputChange("workflow", updatedWorkflow);
  };

  const handleAddStep = (stageIndex) => {
    const updatedWorkflow = [...formData.workflow];
    updatedWorkflow[stageIndex].steps.push({
      step_name: "",
      step_description: "",
    });
    handleInputChange("workflow", updatedWorkflow);
  };

  const handleRemoveStep = (stageIndex, stepIndex) => {
    const updatedWorkflow = [...formData.workflow];
    updatedWorkflow[stageIndex].steps.splice(stepIndex, 1);
    handleInputChange("workflow", updatedWorkflow);
  };

  const handleStepChange = (stageIndex, stepIndex, field, value) => {
    const updatedWorkflow = [...formData.workflow];
    updatedWorkflow[stageIndex].steps[stepIndex][field] = value;
    handleInputChange("workflow", updatedWorkflow);
  };

  if (
    formData.workflow?.some((stage) => stage.stage_name === "notifying") ||
    formData.workflow?.some((stage) => stage.stage_name === "closure")
  ) {
    const updatedWorkflow = formData.workflow.filter(
      (stage) =>
        stage.stage_name !== "notifying" && stage.stage_name !== "closure"
    );
    handleInputChange("workflow", updatedWorkflow);
  }

  return (
    <div className="w-[600px] p-4">
      <h2 className="font-lato text-[22px] text-[#000000]">Workflow Stages</h2>
      <p className="text-[12px] text-[#000000] opacity-70">
        Define the stages of the breach management workflow and add steps for
        each stage.
      </p>

      <div className="mt-6">
        <CreatableInputs
          label="Select or Create Stages"
          name="workflow_stages"
          options={stageOptions}
          value={formData.workflow?.map((stage) => ({
            label: stage.stage_name,
            value: stage.stage_name,
          }))}
          onChange={handleStageChange}
          isMulti
          placeholder="Select or type to create stages..."
          tooltipText="Add stages to your workflow. You can select from the list or create new ones."
        />
      </div>

      <div className="mt-6 flex flex-col gap-6">
        {formData.workflow?.map((stage, stageIndex) => (
          <div
            key={stageIndex}
            className=" border border-gray-200 bg-gray-50 p-4"
          >
            <h3 className="mb-4 text-lg font-semibold text-gray-800 capitalize">
              {stage.stage_name}
            </h3>

            <div className="flex flex-col gap-4">
              {stage.steps.map((step, stepIndex) => (
                <div
                  key={stepIndex}
                  className="relative flex flex-col gap-3 border border-gray-200 bg-white p-3"
                >
                  <div className="absolute right-2 top-2">
                    <button
                      onClick={() => handleRemoveStep(stageIndex, stepIndex)}
                      className="text-red-500 hover:text-red-700"
                    >
                      <FaTrash size={14} />
                    </button>
                  </div>

                  <InputField
                    label={`Step ${stepIndex + 1} Name`}
                    placeholder="Enter step name"
                    value={step.step_name}
                    onChange={(e) =>
                      handleStepChange(
                        stageIndex,
                        stepIndex,
                        "step_name",
                        e.target.value
                      )
                    }
                  />

                  <TextareaField
                    label="Description"
                    placeholder="Enter step description"
                    value={step.step_description}
                    onChange={(e) =>
                      handleStepChange(
                        stageIndex,
                        stepIndex,
                        "step_description",
                        e.target.value
                      )
                    }
                    className="h-20"
                  />
                </div>
              ))}

              <Button
                variant="secondary"
                onClick={() => handleAddStep(stageIndex)}
                className="mt-2 flex items-center justify-center gap-2 self-start"
              >
                <FiPlus /> Add Step
              </Button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default WorkflowStages;
