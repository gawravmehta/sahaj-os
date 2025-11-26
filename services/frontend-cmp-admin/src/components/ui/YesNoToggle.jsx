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
  showNone = false,
}) => {
  return (
    <div className="flex  flex-col gap-2">
      {label && (
        <label className="block text-sm text-heading">
          <div className={`flex w-full items-center ${tooltipCss}`}>
            <span>
              {label}{" "}
              {required && <span className="text-lg text-red-500">*</span>}
            </span>
            {tooltipText && (
              <Tooltip tooltipText={tooltipText} tooltipWidth={tooltipWidth} />
            )}
          </div>
        </label>
      )}

      <div
        className={`inline-flex overflow-hidden border border-[#C7CFE2] ${
          showNone ? "w-[110px]" : "w-[74px]"
        }`}
      >
        <button
          type="button"
          className={`px-2 py-1 text-xs flex-1 border-r border-[#C7CFE2] ${
            value === true ? "bg-[#D5D5EC]" : "bg-[#fdfdfd]"
          }`}
          onClick={() => onChange(name, true)}
        >
          Yes
        </button>

        <button
          type="button"
          className={`px-2 py-1 text-xs flex-1  ${
            value === false ? "bg-[#D5D5EC]" : "bg-[#fdfdfd]"
          }`}
          onClick={() => onChange(name, false)}
        >
          No
        </button>

        {showNone && (
          <button
            type="button"
            className={`px-2 py-1 text-xs flex-1 border-l border-[#C7CFE2] ${
              value === null || value === undefined
                ? "bg-[#D5D5EC]"
                : "bg-[#fdfdfd]"
            }`}
            onClick={() => onChange(name, null)}
          >
            None
          </button>
        )}
      </div>
    </div>
  );
};

export default YesNoToggle;
