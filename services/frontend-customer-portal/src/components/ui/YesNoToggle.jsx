import { Tooltip } from "./Inputs";

const YesNoToggle = ({
  name,
  label,
  value,
  onChange,
  required,
  tooltipText,
  tooltipWidth,
  tooltipCss = "gap-2",
}) => {
  return (
    <div className="flex w-full flex-col gap-2 ">
      {label && (
        <label className="block text-sm text-heading">
          <div className={`flex w-full items-center ${tooltipCss}`}>
            <span className="">
              {label}{" "}
              {required && <span className="text-lg text-red-500">*</span>}
            </span>
            {tooltipText && (
              <Tooltip tooltipText={tooltipText} tooltipWidth={tooltipWidth} />
            )}
          </div>
        </label>
      )}
      <div className="inline-flex w-[155px] overflow-hidden border border-[#C7CFE2] ">
        <button
          type="button"
          className={`w-1/2 py-2 text-xs ${
            value ? "bg-[#D1E7FF]" : "bg-[#fdfdfd]"
          }`}
          onClick={() => onChange(name, true)}
        >
          Yes
        </button>
        <button
          type="button"
          className={`w-1/2 py-2 text-xs ${
            value === false ? "bg-[#D1E7FF]" : "bg-[#fdfdfd]"
          }`}
          onClick={() => onChange(name, false)}
        >
          No
        </button>
      </div>
    </div>
  );
};

export default YesNoToggle;
