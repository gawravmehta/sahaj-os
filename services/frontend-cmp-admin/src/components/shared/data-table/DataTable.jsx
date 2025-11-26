"use client";

import NoDataFound from "@/components/ui/NoDataFound";
import SideFilter from "@/components/ui/SideFilter";
import Skeleton from "@/components/ui/Skeleton";
import Image from "next/image";
import { useRouter } from "next/navigation";
import PropTypes from "prop-types";
import React, { useMemo, useState } from "react";
import { FiFilter } from "react-icons/fi";
import { LuFilterX, LuTable } from "react-icons/lu";
import Pagination from "./Pagination";
import SearchBar from "./SearchBar";

const DataTable = ({
  tableHeight,
  columns,
  data,
  loading,
  totalPages,
  currentPage,
  setCurrentPage,
  rowsPerPageState,
  setRowsPerPageState,
  PaginationView,
  hidePagination = false,
  searchable = true,
  search,
  setSearch,
  hideSearchBar = false,

  isFilter = false,
  clearFilter,
  filterDetails = [],
  isFilterQuery = "",
  onApplyFilters,

  getRowRoute,
  getRowFunction,
  hasSerialNumber = true,
  hasFilterOption = true,
  tabs = [],

  fixedHeight,
  tableWidth,
  totalCount = 0,
  totalCountText = "Total Count",
  filterWithDateRange = false,

  illustrationText = "No Data Available",
  illustrationImage = "/assets/illustrations/no-data-find.png",
  noDataText = "No Data Found",
  noDataImage = "/assets/illustrations/no-data-find.png",
  downloadCSV = false,
  handleDownloadCSV = () => {},
}) => {
  const router = useRouter();
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedFilters, setSelectedFilters] = useState({});
  const [sideFilterVisible, setSideFilterVisible] = useState(false);
  const [activeTabIndex, setActiveTabIndex] = useState(-1);

  const handelApiSearch = (query) => {
    setSearch(query);
    setCurrentPage(1);
  };

  const handleTabClick = (index) => {
    if (activeTabIndex !== index) {
      setActiveTabIndex(index);
    }
  };

  return (
    <>
      {data?.length < 1 &&
      !isFilterQuery &&
      !searchQuery &&
      !loading &&
      !isFilter ? (
        <NoDataFound
          height={"250px"}
          label={illustrationText}
          imageUrl={illustrationImage}
        />
      ) : (
        <>
          <div
            className={`relative flex w-full items-center border-borderheader px-4 ${
              (searchable || isFilter) && "py-[9.12px]"
            }  shadow-sm`}
          >
            {totalCount != 0 && (
              <div className="flex w-full items-center justify-between pl-2">
                <span className="text-sm">
                  {totalCount} : {totalCountText}
                </span>
              </div>
            )}

            {isFilter && sideFilterVisible && (
              <div>
                <SideFilter
                  sideFilterVisible={sideFilterVisible}
                  setSideFilterVisible={setSideFilterVisible}
                  filterDetails={filterDetails}
                  onApplyFilters={onApplyFilters}
                  filterWithDateRange={filterWithDateRange}
                  isFilter={isFilter}
                  clearFilter={clearFilter}
                  selectedFilters={selectedFilters}
                  setSelectedFilters={setSelectedFilters}
                  tableHeight={tableHeight}
                  handleDownloadCSV={handleDownloadCSV}
                  downloadCSV={downloadCSV}
                />
              </div>
            )}
            <div className="flex w-full justify-end gap-4">
              <div className="flex w-full justify-end gap-4 pr-2">
                {!hideSearchBar && (
                  <>
                    {searchable && (
                      <SearchBar
                        onSearch={handelApiSearch}
                        searchQuery={search}
                      />
                    )}
                  </>
                )}

                {tabs.length > 0 && (
                  <div className="flex cursor-pointer items-center gap-4">
                    <LuTable
                      className={`cursor-pointer text-lg ${
                        activeTabIndex === -1
                          ? "text-primary"
                          : "text-[#8a8a8a]"
                      }`}
                      onClick={() => setActiveTabIndex(-1)}
                    />
                    {tabs.map((tab, index) => (
                      <button
                        key={index}
                        onClick={() => handleTabClick(index)}
                        className={`${
                          activeTabIndex === index
                            ? "text-[#3C3D64]"
                            : "text-[#8a8a8a]"
                        }`}
                      >
                        {tab.icon}
                      </button>
                    ))}
                  </div>
                )}
              </div>

              {hasFilterOption && filterDetails.length > 0 && (
                <button
                  onClick={() => setSideFilterVisible(!sideFilterVisible)}
                  className="flex items-center cursor-pointer text-gray-600 focus:outline-none"
                  aria-label="Toggle Filters"
                >
                  {sideFilterVisible ? (
                    <LuFilterX className="mr-2 size-5 text-lg text-[#f7a6a6]" />
                  ) : (
                    <FiFilter className="mr-2 size-5 text-lg text-primary hover:text-hover" />
                  )}
                </button>
              )}
            </div>
          </div>

          {activeTabIndex === -1 ? (
            <div
              className="custom-scrollbar w-full overflow-auto"
              style={{
                height: fixedHeight
                  ? `${fixedHeight}`
                  : `calc(100vh - ${tableHeight})`,
              }}
            >
              <table
                className={`w-full ${
                  tableWidth ? `min-w-[${tableWidth}]` : "min-w-[1000px]"
                }`}
              >
                <thead>
                  <tr className="sticky top-0 border-gray-300 bg-[#f5f7fc]">
                    {hasSerialNumber && (
                      <th className="w-10 px-6 py-1 font-sans text-xs  font-medium text-heading sm:text-sm">
                        #
                      </th>
                    )}
                    {columns.map((col, index) => (
                      <th
                        key={index}
                        className={`text-nowrap py-3  font-sans text-xs font-medium text-heading sm:text-sm ${
                          col.headerClassName || ""
                        }`}
                      >
                        {col.header}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {loading ? (
                    Array.from({ length: 20 }).map((_, rowIndex) => (
                      <tr key={`skeleton-row-${rowIndex}`} className="border-b">
                        {hasSerialNumber && (
                          <td className="px-4 py-2">
                            <Skeleton
                              variant="single"
                              className="z-0 h-4 w-6 rounded-none"
                            />
                          </td>
                        )}
                        {columns.map((_, colIndex) => (
                          <td
                            key={`skeleton-col-${colIndex}`}
                            className="px-2 py-2"
                          >
                            <Skeleton
                              variant="single"
                              className="z-0 h-4 w-full rounded-none"
                            />
                          </td>
                        ))}
                      </tr>
                    ))
                  ) : data?.length > 0 ? (
                    data?.map((row, idx) => (
                      <tr
                        key={idx}
                        className={`border-b border-[#eeeeee] hover:bg-[#fefefe] ${
                          getRowRoute?.(row) || getRowFunction?.(row)
                            ? "cursor-pointer"
                            : ""
                        }`}
                        onClick={() => {
                          const route = getRowRoute?.(row);
                          const fn = getRowFunction?.(row);

                          if (route) {
                            router.push(route);
                          } else if (fn) {
                            fn();
                          }
                        }}
                      >
                        {hasSerialNumber && (
                          <td className="px-6 py-2.5 text-xs text-gray-600">
                            {String(
                              (currentPage - 1) * rowsPerPageState + idx + 1
                            )}
                          </td>
                        )}

                        {columns?.map((col, index) => (
                          <td
                            key={index}
                            className={` ${col?.tableDataClassName} text-left text-xs text-gray-600`}
                          >
                            {(() => {
                              const rawValue = col.render
                                ? col.render(row[col.accessor], row)
                                : row[col.accessor];

                              const isEmpty =
                                rawValue === null ||
                                rawValue === undefined ||
                                (typeof rawValue === "string" &&
                                  rawValue.trim() === "") ||
                                (Array.isArray(rawValue) &&
                                  rawValue.length === 0) ||
                                (typeof rawValue === "object" &&
                                  Object.keys(rawValue).length === 0);

                              return !isEmpty ? (
                                rawValue
                              ) : (
                                <span className="text-gray-400">-</span>
                              );
                            })()}
                          </td>
                        ))}
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td
                        colSpan={columns?.length + (hasSerialNumber ? 1 : 0)}
                        style={{ height: `calc(90vh - ${tableHeight})` }}
                        className="justify-center px-4 py-4 text-center text-sm text-gray-500"
                      >
                        <div className="flex flex-col items-center justify-center">
                          <div className="w-[250px]">
                            <Image
                              height={200}
                              width={200}
                              src={noDataImage}
                              alt="Circle Image"
                              className="h-full w-full object-cover"
                            />
                          </div>

                          <div className="mt-5">
                            <h1 className="text-xl">{noDataText}</h1>
                          </div>
                        </div>
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          ) : (
            tabs[activeTabIndex]?.component
          )}

          {activeTabIndex === -1 && !hidePagination && (
            <Pagination
              currentPage={currentPage}
              totalPages={totalPages}
              onPageChange={setCurrentPage}
              rowsPerPage={rowsPerPageState}
              setRowsPerPage={setRowsPerPageState}
              PaginationView={PaginationView}
            />
          )}
        </>
      )}
    </>
  );
};

DataTable.propTypes = {
  columns: PropTypes.arrayOf(
    PropTypes.shape({
      header: PropTypes.string.isRequired,
      accessor: PropTypes.string.isRequired,
      render: PropTypes.func,
    })
  ).isRequired,
  data: PropTypes.arrayOf(PropTypes.object).isRequired,
  rowsPerPageState: PropTypes.number,
  searchable: PropTypes.bool,
  hasSerialNumber: PropTypes.bool,
  hasFilterOption: PropTypes.bool,
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
  ),
  tabs: PropTypes.arrayOf(
    PropTypes.shape({
      icon: PropTypes.node.isRequired,
      component: PropTypes.node.isRequired,
    })
  ),
  hideSearchBar: PropTypes.bool,
  tableHeight: PropTypes.string,
  totalPages: PropTypes.number.isRequired,
  currentPage: PropTypes.number.isRequired,
  setCurrentPage: PropTypes.func.isRequired,
  setRowsPerPageState: PropTypes.func.isRequired,
};

export default React.memo(DataTable);
