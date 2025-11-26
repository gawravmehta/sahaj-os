import Button from "@/components/ui/Button";
import { InputField } from "@/components/ui/Inputs";
import { useState } from "react";
import toast from "react-hot-toast";
import { RxCross2 } from "react-icons/rx";

const DeleteModal = ({
  inputStatus = false,
  closeModal,
  title,
  variant,
  buttonClass,
  onConfirm,
  typeTitle,
  isArchive = false,
}) => {
  const [confirmationText, setConfirmationText] = useState("");
  const handleConfirmationChange = (e) => {
    setConfirmationText(e.target.value);
  };

  const isConfirmationCorrect = confirmationText === typeTitle;

  return (
    <>
      <div
        onClick={closeModal}
        className="fixed inset-0 z-50 flex items-center justify-center bg-[#f2f9ff]/50"
      >
        <div
          className="relative flex h-[300px] w-136 flex-col items-center border border-[#c7cfe2] bg-white p-8"
          onClick={(e) => e.stopPropagation()}
        >
          <div>
            <Button
              variant="close"
              className="flex w-full justify-end"
              onClick={closeModal}
            >
              <RxCross2
                size={20}
                className="flex w-full items-end justify-end"
              />
            </Button>
            <h1 className="text-center text-2xl">{title}</h1>

            <div className="my-6 text-center text-base">
              <p className="text-subHeading">
                This action will {isArchive ? "archive" : "permanently delete"}{" "}
                the &ldquo;
                <strong className="text-black">{typeTitle}</strong>&ldquo; data.
                Please confirm your action.
              </p>
            </div>
          </div>

          {!inputStatus && (
            <div className="w-[60%]">
              <InputField
                type="text"
                placeholder={`Type '${typeTitle}' to confirm`}
                value={confirmationText}
                onChange={handleConfirmationChange}
                onPaste={(e) => e.preventDefault()}
                onContextMenu={(e) => e.preventDefault()}
                className="text-center"
              />
            </div>
          )}
          {isConfirmationCorrect && (
            <div className="mt-5 flex justify-center gap-4">
              <Button
                variant="no"
                onClick={closeModal}
                className="px-9 py-2 text-sm"
              >
                No
              </Button>
              <Button
                className={buttonClass}
                variant={variant ? variant : "yes"}
                onClick={() => {
                  if (isConfirmationCorrect) {
                    onConfirm();
                  } else {
                    toast.error(`Please type '${typeTitle}' to confirm.`);
                  }
                }}
              >
                Yes
              </Button>
            </div>
          )}
        </div>
      </div>
    </>
  );
};

export default DeleteModal;
