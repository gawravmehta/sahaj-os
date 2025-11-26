"use client";

import { useEffect, useState } from "react";
import { RxCross2 } from "react-icons/rx";
import { AiOutlineCheck } from "react-icons/ai";
import { apiCall } from "@/hooks/apiCall";
import toast from "react-hot-toast";
import Image from "next/image";
import Button from "@/components/ui/Button";
import { getErrorMessage } from "@/utils/errorHandler";
import Loader from "@/components/ui/Loader";

const PermissionsModal = ({ roleId, onClose }) => {
  const [routes, setRoutes] = useState([]);
  const [selectedRoutes, setSelectedRoutes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);

  const fetchRoutes = async () => {
    setLoading(true);
    try {
      const response = await apiCall("/roles/get-all-frontend-routes");
      setRoutes(response?.data || []);
    } catch (error) {
      toast.error("Failed to fetch routes");
    } finally {
      setLoading(false);
    }
  };

  const fetchSelectedRole = async () => {
    try {
      const response = await apiCall(`/roles/get-one-role/${roleId}`);
      setSelectedRoutes(response?.routes_accessible || []);
    } catch (error) {
      toast.error(getErrorMessage(error));
      console.error("Failed to fetch role details:", error);
    }
  };

  useEffect(() => {
    fetchRoutes();
    fetchSelectedRole();
  }, []);

  const togglePermission = (path, action) => {
    setSelectedRoutes((prev) => {
      const existing = prev.find((r) => r.path === path);
      if (existing) {
        const newActions = existing.actions.includes(action)
          ? existing.actions.filter((a) => a !== action)
          : [...existing.actions, action];

        if (newActions.length === 0) {
          return prev.filter((r) => r.path !== path);
        }

        return prev.map((r) =>
          r.path === path ? { ...r, actions: newActions } : r
        );
      } else {
        return [...prev, { path, actions: [action] }];
      }
    });
  };

  const hasPermission = (path, action) => {
    const found = selectedRoutes.find((r) => r.path === path);
    return found?.actions?.includes(action);
  };

  const handleUpdate = async () => {
    setSaving(true);
    try {
      await apiCall(`/roles/update-role-permissions/${roleId}`, {
        method: "PATCH",
        data: {
          routes_accessible: selectedRoutes,
        },
      });
      toast.success("Permissions updated successfully!");
      onClose();
    } catch (error) {
      toast.error(getErrorMessage(error));
    } finally {
      setSaving(false);
    }
  };

  return (
    <div
      onClick={onClose}
      className="fixed inset-0 z-50 flex items-center justify-center bg-[#f2f9ff]/50"
    >
      <div
        className=" w-180 relative shadow-lg border-[#c7cfe2] bg-white "
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex justify-between items-center border-b px-4 py-2">
          <h2 className="font-semibold text-lg">Permissions :</h2>
          <Button
            variant="close"
            className="flex  justify-end"
            onClick={onClose}
          >
            <RxCross2 size={20} className="flex w-full items-end justify-end" />
          </Button>
        </div>

        <div className="p-4 max-h-[500px] min-h-[300px] medium-scrollbar overflow-y-auto grid grid-cols-2 gap-2">
          {loading ? (
            <Loader height="h-[250px] w-full mx-auto" />
          ) : (
            routes.map((route, index) => {
              const isReadChecked = hasPermission(route.href, "read");
              const isWriteChecked = hasPermission(route.href, "write");

              return (
                <div
                  key={index}
                  className="border p-3 flex flex-col gap-3 relative"
                >
                  <div className="flex items-center gap-2">
                    <Image
                      src={route.icon}
                      alt={route.label}
                      width={45}
                      height={45}
                      className="object-contain bg-primary px-2 py-1"
                    />
                    <span className="text-sm font-medium">{route.label}</span>
                  </div>

                  <div className="flex flex-col gap-3 absolute right-3 top-1/2 -translate-y-1/2">
                    <label className="flex items-center cursor-pointer relative">
                      <span className="text-sm text-gray-800 w-10">
                        Read
                      </span>
                      <input
                        type="checkbox"
                        checked={isReadChecked}
                        onChange={() => togglePermission(route.href, "read")}
                        className="w-4 h-4 accent-primary border border-gray-400 cursor-pointer appearance-none checked:bg-primary checked:border-primary"
                      />
                      {isReadChecked && (
                        <AiOutlineCheck className="absolute right-0 top-0.5 w-4 h-4 text-white pointer-events-none" />
                      )}
                    </label>

                    <label className="flex items-center cursor-pointer relative">
                      <span className="text-sm text-gray-800 w-10">
                        Write
                      </span>
                      <input
                        type="checkbox"
                        checked={isWriteChecked}
                        onChange={() => togglePermission(route.href, "write")}
                        className="w-4 h-4 accent-primary border border-gray-400 cursor-pointer appearance-none checked:bg-primary checked:border-primary"
                      />
                      {isWriteChecked && (
                        <AiOutlineCheck className="absolute right-0 top-0.5 w-4 h-4 text-white pointer-events-none" />
                      )}
                    </label>
                  </div>
                </div>
              );
            })
          )}
        </div>

        <div className="flex justify-end border-t px-4 py-2">
          <Button
            variant="primary"
            onClick={handleUpdate}
            disabled={saving}
            className="mr-2"
          >
            {saving ? "Updating..." : "Update"}
          </Button>
        </div>
      </div>
    </div>
  );
};

export default PermissionsModal;
