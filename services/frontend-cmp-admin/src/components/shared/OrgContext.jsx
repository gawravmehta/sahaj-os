"use client";
import { createContext, useContext, useEffect, useState } from "react";
import { apiCall } from "@/hooks/apiCall";
import { getErrorMessage } from "@/utils/errorHandler";
import toast from "react-hot-toast";
import Cookies from "js-cookie";

const OrgContext = createContext();

export const OrgProvider = ({ children }) => {
  const [orgName, setOrgName] = useState("");
  const [orgDetails, setOrgDetails] = useState(null);
  const [loadingOrg, setLoadingOrg] = useState(true);
  const token = Cookies.get("access_token");

  const fetchOrgName = async () => {
    if (!token) {
      setLoadingOrg(false);
      return;
    }
    try {
      const response = await apiCall("/data-fiduciary/data-fiduciary-details");

      const name = response?.org_info?.name || "";
      setOrgDetails(response || null);
      setOrgName(name);
    } catch (error) {
      toast.error(getErrorMessage(error));
    } finally {
      setLoadingOrg(false);
    }
  };

  useEffect(() => {
    fetchOrgName();
  }, []);

  return (
    <OrgContext.Provider
      value={{ orgName, setOrgName, fetchOrgName, loadingOrg, orgDetails }}
    >
      {children}
    </OrgContext.Provider>
  );
};

export const useOrg = () => useContext(OrgContext);
