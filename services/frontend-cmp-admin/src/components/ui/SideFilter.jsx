"use client";

import Button from "@/components/ui/Button";
import { customStyles } from "@/utils/selectCustomStyles";
import { usePathname } from "next/navigation";
import { useState } from "react";
import { RxCross2 } from "react-icons/rx";
import Select from "react-select";
import DatePicker from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";
import { LuDownload } from "react-icons/lu";
import YesNoToggle from "./YesNoToggle";

const SideFilter = ({
  sideFilterVisible,
  setSideFilterVisible,
  filterDetails,
  onApplyFilters,
  isFilter,
  clearFilter,
  selectedFilters,
  setSelectedFilters,
  filterWithDateRange = false,
  tableHeight,
  handleDownloadCSV,
  downloadCSV = false,
}) => {
  const pathname = usePathname();

  const [startDate, setStartDate] = useState(null);
  const [endDate, setEndDate] = useState(null);

  const handleSelectChange = (name, selectedOption, isMulti) => {
    if (isMulti) {
      setSelectedFilters((prev) => ({
        ...prev,
        [name]: selectedOption ? selectedOption.map((opt) => opt.value) : [],
      }));
    } else {
      setSelectedFilters((prev) => ({
        ...prev,
        [name]: selectedOption ? selectedOption.value : null,
      }));
    }
  };

  const handleDateChange = (dates) => {
    const [start, end] = dates;
    setStartDate(start);
    setEndDate(end);

    setSelectedFilters((prev) => ({
      ...prev,
      start_date: start ? start.toISOString() : null,
      end_date: end ? end.toISOString() : null,
    }));
  };

  const isApplyDisabled = !Object.values(selectedFilters).some(
    (val) => val !== null && val !== "" && val !== undefined
  );

  return (
    <div
      className={`h-[calc(100vh - ${tableHeight})] absolute right-0 top-0 z-10 w-76 border-l border-borderheader bg-[#F9FCFF]`}
    >
      <div className="flex justify-between border-b border-borderheader px-5 pb-2 pt-3">
        <p className="text-lg">Filter</p>
        <RxCross2
          className="cursor-pointer text-red-500"
          size={25}
          onClick={() => setSideFilterVisible(false)}
        />
      </div>

      <div
        className={`custom-scrollbar flex flex-col overflow-y-auto bg-[#F9FCFF] p-3.5`}
        style={{ height: `calc(100vh - ${tableHeight})` }}
      >
        {filterWithDateRange && (
          <div className="mb-4 w-full">
            <label className="mb-2 block">Date Range</label>
            <DatePicker
              selectsRange
              startDate={startDate}
              endDate={endDate}
              onChange={handleDateChange}
              isClearable
              placeholderText="Select Date Range"
              className="min-h-8 w-[17.2rem] rounded-none border border-gray-300 bg-[#fdfdfd] px-2 py-1.5 text-[12px] text-[#333] placeholder-[#8a8a8a] focus:border-[#012FA6] focus:outline-none focus:ring-0"
              calendarClassName="!rounded-none !text-[12px] !border-[#ccc] !z-[9999]"
              dayClassName={(date) =>
                "text-[12px] px-1 py-1 hover:bg-[#F2F9FF] hover:text-[#012FA6] cursor-pointer " +
                (date >= startDate && date <= endDate
                  ? "bg-[#012FA6] text-white"
                  : "")
              }
            />
          </div>
        )}
        {filterDetails.map((item) => (
          <div key={item.name} className="mb-4">
            <label htmlFor={item.name} className="mb-2 block font-medium">
              {item.label}
            </label>

            {item.type === "toggle" ? (
              <YesNoToggle
                name={item.name}
                value={selectedFilters[item.name]}
                onChange={(name, val) => {
                  setSelectedFilters((prev) => ({
                    ...prev,
                    [name]: val,
                  }));
                }}
                tooltipText={item.tooltipText}
                showNone={true}
              />
            ) : (
              <Select
                id={item.name}
                options={item.options}
                value={
                  item.isMultiSelect
                    ? item.options?.filter((option) =>
                        (selectedFilters[item.name] || []).includes(
                          option.value
                        )
                      )
                    : item.options?.find(
                        (opt) => opt.value === selectedFilters[item.name]
                      ) || null
                }
                onChange={(selected) => {
                  handleSelectChange(item.name, selected, item.isMultiSelect);
                  if (item.onChange) {
                    item.onChange(selected?.value);
                  }
                }}
                placeholder={`Select ${item.label}`}
                styles={customStyles}
                menuPlacement="auto"
                isMulti={item.isMultiSelect}
                isClearable
              />
            )}
          </div>
        ))}
      </div>
      <div className="-mt-1 flex h-10 w-full items-center justify-between border border-t border-borderheader bg-[#F9FCFF] px-3.5">
        {Object.values(selectedFilters).some((val) => val !== null) && (
          <Button
            onClick={() => {
              const resetFilters = {};
              filterDetails.forEach((item) => {
                resetFilters[item.name] = null;
              });

              if (filterWithDateRange) {
                setStartDate(null);
                setEndDate(null);
                resetFilters.start_date = null;
                resetFilters.end_date = null;
              }

              setSelectedFilters(resetFilters);
              clearFilter(isFilter);
            }}
            variant="cancel"
            className="h-7"
          >
            Clear Filter
          </Button>
        )}

        <div className="flex items-center gap-2">
          {downloadCSV && (
            <Button
              variant="secondary"
              onClick={handleDownloadCSV}
              className="flex items-center text-xs text-primary focus:outline-none"
              aria-label="Download CSV"
            >
              <LuDownload className="size-4" />
              CSV
            </Button>
          )}
          <Button
            onClick={() => onApplyFilters(selectedFilters)}
            type="button"
            variant={isApplyDisabled ? "ghost" : "primary"}
            className="ml-auto h-7 px-4"
            disabled={isApplyDisabled}
          >
            Apply
          </Button>
        </div>
      </div>
    </div>
  );
};

export default SideFilter;
