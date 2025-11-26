import React from "react";
import { IoMdCheckmark } from "react-icons/io";
import { cn } from "@/utils/twMerge";

const Stepper = ({
  steps,
  activeStep,
  onStepClick,
  className = "max-w-[480px]",
}) => {
  return (
    <div className="mt-1 border-y-[1px] border-gray-200 py-2">
      <div className="flex h-7 items-center justify-center">
        <div
          className={`flex w-full ${className} items-center justify-between`}
        >
          {steps.map((step, index) => {
            const stepNumber = index + 1;
            const isActive = activeStep === stepNumber;
            const isCompleted = activeStep > stepNumber;

            return (
              <React.Fragment key={stepNumber}>
                <span
                  className={cn(
                    "flex h-6 w-6  items-center justify-center rounded-full text-xs",
                    isActive
                      ? "border-2 borderPrimary text-primary"
                      : "border-2 borderPrimary text-black",
                    isCompleted && "border-none bg-primary text-white"
                  )}
                >
                  {isCompleted ? (
                    <IoMdCheckmark size={20} />
                  ) : stepNumber < 10 ? (
                    `${stepNumber}`
                  ) : (
                    stepNumber
                  )}
                </span>
                {index < steps.length - 1 && (
                  <div
                    className={cn(
                      "mx-3 flex-1 border",
                      isCompleted ? "borderPrimary" : "border-borderSecondary"
                    )}
                  />
                )}
              </React.Fragment>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default Stepper;
