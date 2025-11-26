"use client";

import Button from "@/components/ui/Button";
import SearchBar from "@/components/data-table/SearchBar";
import Header from "@/components/ui/Header";
import { apiCall } from "@/hooks/apiCall";
import { useEffect, useState } from "react";
import { FiFilter } from "react-icons/fi";
import { LuFilterX } from "react-icons/lu";
import { IoCloseOutline } from "react-icons/io5";
import { getErrorMessage } from "@/utils/errorHandler";
import toast from "react-hot-toast";
import IncidentCard from "../components/IncidentCard";
import Filter from "../../../principal-management/persona-management/explore/Filter";

const breadcrumbsProps = {
  path: "/user/incident-management/pdba/find Template",
  skip: "/user/incident-management",
};

const Page = () => {
  const [searchQuery, setSearchQuery] = useState("");
  const [incidentData, setIncidentData] = useState(null);
  const [category, setCategory] = useState("");
  const [selectedRiskLevel, setSelectedRiskLevel] = useState("");
  const [filterVisible, setFilterVisible] = useState(null);
  const [incidentDetail, setIncidentDetail] = useState();
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getAllIncidentTemplates(category, selectedRiskLevel);
  }, [searchQuery]);

  const handleSearch = (query) => {
    setSearchQuery(query);
  };

  const SidBarVisible = (e) => {
    setFilterVisible(e);
  };

  const getIncidentById = async (incidentId) => {
    try {
      const response = await apiCall(`/templates/incident/${incidentId}`);
      setFilterVisible(incidentId);
      setIncidentDetail(response);
    } catch (error) {
      toast.error(getErrorMessage(error));
      console.error("Error fetching incident data:", error);
    }
  };

  const getAllIncidentTemplates = async (category, selectedRiskLevel) => {
    try {
      const response = await apiCall(`/templates/incident`);
      setIncidentData(response);
      setLoading(false);
    } catch (error) {
      console.error(error, "Error fetching all incident templates:");
      const message = getErrorMessage(error);
      toast.error(message);
      setLoading(false);
    }
  };

  const clearFilters = () => {
    setCategory("");
    setSelectedRiskLevel("");
    getAllIncidentTemplates("", "");
  };

  return (
    <div className="flex">
      <div className="mb-2 w-full">
        <div className="border-b border-borderheader">
          <Header
            title="Explore Template"
            breadcrumbsProps={breadcrumbsProps}
            subtitle="Browse through the available incident templates"
          />
        </div>
        <div className="sticky top-0 z-40 mb-1 flex justify-between gap-4 bg-background p-0 pr-4 sm:py-2 md:flex-row">
          <span></span>
          <div className="flex items-center justify-between gap-2">
            <div>
              <SearchBar onSearch={handleSearch} />
            </div>
            <button
              className="flex items-center text-gray-600 focus:outline-none"
              aria-label="Toggle Filters"
              onClick={() => {
                filterVisible === "filter"
                  ? (SidBarVisible(null), clearFilters())
                  : SidBarVisible("filter");
              }}
            >
              {filterVisible === "filter" ? (
                <LuFilterX className="size-5 text-lg text-primary" />
              ) : (
                <FiFilter className="mr-2 size-5 text-lg text-primary hover:text-hover" />
              )}
            </button>
          </div>
        </div>
        <div className="flex h-[calc(100vh-209px)] w-full px-6">
          <div className="custom-scrollbar flex h-[calc(100vh-201px)] w-full flex-col overflow-auto">
            <IncidentCard
              incidentData={incidentData}
              getIncidentById={getIncidentById}
              setFilterVisible={setFilterVisible}
              filterVisible={filterVisible}
              loading={loading}
            />
          </div>
          <div className="">
            {filterVisible && (
              <Filter
                setFilterVisible={setFilterVisible}
                setCategory={setCategory}
                category={category}
                selectedRiskLevel={selectedRiskLevel}
                handleFilter={getAllIncidentTemplates}
                setSelectedRiskLevel={setSelectedRiskLevel}
                filterVisible={filterVisible}
                data={incidentDetail}
                clearFilters={clearFilters}
              />
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Page;
