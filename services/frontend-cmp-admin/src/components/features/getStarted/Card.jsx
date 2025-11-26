import { useRouter } from "next/navigation";
import { IoIosCheckmarkCircle } from "react-icons/io";
import { IoCloseCircleSharp } from "react-icons/io5";

const Card = ({ step, checkedSteps, index }) => {
  const router = useRouter();

  const handleStepClick = () => {
    router.push(`/apps/get-started/${step?.step_id}`);
  };

  return (
    <div
      key={index}
      className={`flex items-center cursor-pointer border border-[#E6E6E6] p-3 hover:border-primary focus:border-primary focus:outline-none ${
        checkedSteps[index] ? "gap-3" : "gap-3"
      }`}
      tabIndex="0"
    >
      {step.is_section_completed || checkedSteps[index] ? (
        <div className="flex h-12 w-12 cursor-pointer items-center justify-center bg-white">
          <IoIosCheckmarkCircle className="h-9 w-9 text-primary" />
        </div>
      ) : (
        <div className="flex h-12 w-12 cursor-pointer items-center justify-center">
          <IoCloseCircleSharp className="h-9 w-9 text-[#EE5656]" />
        </div>
      )}

      <div
        className="flex w-[95%] cursor-pointer gap-x-5 justify-between"
        onClick={handleStepClick}
      >
        <div>
          <h1 className="text-base font-medium">{step.step_title}</h1>

          <p className="overflow-hidden text-sm  text-subHeading">
            {step.description}
          </p>
        </div>

        <div className="flex h-full flex-col items-center justify-center">
          <div className="text-xl text-primary">
            {step.completed_action_count}/{step.action_count}
          </div>
          <div className="text-xs  text-subHeading">Actions</div>
        </div>
      </div>
    </div>
  );
};

export default Card;
