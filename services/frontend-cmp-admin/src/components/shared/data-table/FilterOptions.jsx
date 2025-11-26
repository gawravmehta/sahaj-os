import React from "react";
import PropTypes from "prop-types";
import Select from "react-select";
import { customStyles } from "@/utils/selectCustomStyles";

const FilterOptions = ({
  filters,
  selectedFilters,
  onFilterChange,
  onClearFilters,
}) => {
  return (
    <div className="flex gap-4 px-2">
      {filters.map((filter) => (
        <div key={filter.name} className="w-44">
          <label htmlFor={filter.name} className="sr-only">
            {filter.label}
          </label>
          <Select
            id={filter.name}
            name={filter.name}
            value={
              filter.options.find(
                (option) => option.value === selectedFilters[filter.name]
              ) || null
            }
            onChange={(selectedOption) =>
              onFilterChange(
                filter.name,
                selectedOption ? selectedOption.value : ""
              )
            }
            options={filter.options}
            isClearable
            placeholder={`Select ${filter.label}`}
            className="text-sm"
            styles={customStyles}
            classNames={{
              menuList: () => "medium-scrollbar",
            }}
          />
        </div>
      ))}
      <button
        onClick={onClearFilters}
        className="flex w-20 cursor-pointer items-center text-sm font-medium text-primary"
      >
        Clear All
      </button>
    </div>
  );
};

FilterOptions.propTypes = {
  filters: PropTypes.arrayOf(
    PropTypes.shape({
      name: PropTypes.string.isRequired,
      label: PropTypes.string.isRequired,
      options: PropTypes.arrayOf(
        PropTypes.shape({
          value: PropTypes.string.isRequired,
          label: PropTypes.string.isRequired,
        })
      ).isRequired,
    })
  ).isRequired,
  selectedFilters: PropTypes.object.isRequired,
  onFilterChange: PropTypes.func.isRequired,
  onClearFilters: PropTypes.func.isRequired,
};

export default React.memo(FilterOptions);
