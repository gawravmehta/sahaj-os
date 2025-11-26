import { useEffect } from "react";
import {
  IoIosArrowBack,
  IoIosArrowDown,
  IoIosArrowForward,
} from "react-icons/io";

const Pagination = ({
  currentPage,
  totalPages,
  onPageChange,
  rowsPerPage,
  setRowsPerPage,
  PaginationView,
}) => {
  useEffect(() => {
    if (totalPages && currentPage > totalPages) {
      onPageChange(totalPages);
    }
  }, [currentPage, totalPages, onPageChange]);

  if (totalPages === 0) return null;

  const handleRowsPerPageChange = (value) => {
    setRowsPerPage(Number(value));
    onPageChange(1);
  };

  const paginate = (page) => {
    if (page >= 1 && page <= totalPages) {
      onPageChange(page);
    }
  };

  const getPageNumbers = () => {
    const pages = [];
    const visiblePages = 3;
    const startPage = Math.max(currentPage - Math.floor(visiblePages / 2), 1);
    const endPage = Math.min(startPage + visiblePages - 1, totalPages);

    if (startPage > 1) {
      pages.push(1);
      if (startPage > 2) pages.push("...");
    }

    for (let i = startPage; i <= endPage; i++) {
      pages.push(i);
    }

    if (endPage < totalPages) {
      if (endPage < totalPages - 1) pages.push("...");
      pages.push(totalPages);
    }

    return pages;
  };

  return (
    <div className="relative m-auto flex h-10 items-center justify-between border-t px-4 py-2">
      {!PaginationView && (
        <div className="flex items-center pl-2">
          <span className="mr-2 text-[13px] text-gray-600">Show Per Page</span>

          <div className="relative mt-1 inline-block text-sm text-[#6682CA]">
            <select
              value={rowsPerPage}
              onChange={(e) => handleRowsPerPageChange(e.target.value)}
              className="appearance-none border border-[#C0C0C0] bg-white px-2 py-1 pr-6 outline-none"
            >
              <option value={10}>10</option>
              <option value={20}>20</option>
              <option value={50}>50</option>
              <option value={100}>100</option>
            </select>
            <div className="pointer-events-none absolute inset-y-0 right-2 flex items-center">
              <IoIosArrowDown />
            </div>
          </div>
        </div>
      )}

      <div className="absolute right-3 flex items-center space-x-2">
        <button
          disabled={currentPage === 1}
          onClick={() => paginate(currentPage - 1)}
          className="flex items-center gap-2 px-1 py-1 text-primary disabled:opacity-50 sm:px-2"
        >
          <IoIosArrowBack />
        </button>

        {getPageNumbers().map((page, index) => {
          return (
            <button
              key={index}
              onClick={() => {
                if (page !== "...") paginate(page);
              }}
              className={`px-2 py-1 text-[13px] ${
                currentPage === page
                  ? "bg-primary font-bold text-white"
                  : "bg-[#eee] text-primary"
              }`}
            >
              {page}
            </button>
          );
        })}

        <button
          disabled={currentPage === totalPages}
          onClick={() => paginate(currentPage + 1)}
          className="flex items-center gap-2 px-1 py-1 text-primary disabled:opacity-50 sm:px-2"
        >
          <IoIosArrowForward />
        </button>
      </div>
    </div>
  );
};

export default Pagination;
