"use client";
import { apiCall } from "@/hooks/apiCall";
import React, { createContext, useContext, useEffect, useState } from "react";

const PermissionContext = createContext();

export const PermissionProvider = ({ children }) => {
  const [permissions, setPermissions] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchPermissions = async () => {
    try {
      const res = await apiCall(`/auth/get-my-permissions`);

      setPermissions(res.permissions || []);
    } catch (err) {
      console.error("Error fetching permissions:", err);
    } finally {
      setLoading(false);
    }
  };
  useEffect(() => {
    fetchPermissions();
  }, []);

  const hasPermission = (path, action) => {
    return permissions.some(
      (perm) =>
        perm.path === path &&
        (perm.action === action || perm.action === "write")
    );
  };

  const canRead = (path) => hasPermission(path, "read");
  const canWrite = (path) => hasPermission(path, "write");

  return (
    <PermissionContext.Provider
      value={{ permissions, canRead, canWrite, loading, fetchPermissions }}
    >
      {children}
    </PermissionContext.Provider>
  );
};

export const usePermissions = () => useContext(PermissionContext);
