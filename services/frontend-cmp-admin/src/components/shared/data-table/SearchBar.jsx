import React from "react";
import { FiSearch } from "react-icons/fi";
import { IoClose } from "react-icons/io5";

const SearchBar = ({ onSearch, searchQuery }) => {
  const handleInputChange = (e) => {
    onSearch(e.target.value);
  };

  return (
    <div className="flex items-center gap-2 border border-[#c7cfe2] bg-[#fafafa]">
      <div className="relative flex w-48 items-center rounded-sm pl-9 pr-7 text-gray-500 transition-all duration-300">
        <span className="absolute left-3 top-1/2 -translate-y-1/2 transform text-placeholder">
          <FiSearch />
        </span>

        <input
          type="text"
          value={searchQuery}
          className="h-7 w-32 border-none bg-transparent text-xs text-gray-700 placeholder outline-none transition-colors duration-300 placeholder:text-xs"
          placeholder="Search"
          onChange={(e) => handleInputChange(e)}
        />
        {searchQuery && (
          <span
            onClick={() => onSearch("")}
            className="absolute right-2 top-1/2 -translate-y-1/2 transform cursor-pointer text-red-400"
          >
            <IoClose />
          </span>
        )}
      </div>
    </div>
  );
};

export default SearchBar;
