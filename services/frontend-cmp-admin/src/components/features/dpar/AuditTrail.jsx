import { formatDistanceToNow } from "date-fns";
import {
  FiDatabase,
  FiEdit3,
  FiLock,
  FiTrash2,
  FiUnlock,
  FiUserPlus,
} from "react-icons/fi";

const iconMap = {
  create: <FiUserPlus size={20} />,
  update: <FiEdit3 size={20} />,
  delete: <FiTrash2 size={20} />,
  login: <FiUnlock size={20} />,
  logout: <FiLock size={20} />,
  default: <FiDatabase size={20} />,
};

const actionBgColors = {
  create: "bg-green-100",
  update: "bg-blue-100",
  delete: "bg-red-100",
  login: "bg-purple-100",
  logout: "bg-orange-100",
  default: "bg-gray-100",
};

const statusTagColor = {
  success: "border-green-500 text-green-500",
  failed: "border-red-500 text-red-500",
  pending: "border-yellow-500 text-yellow-500",
  new: "border-primary text-primary",
};

const auditLogs = [
  {
    _id: "1",
    action_type: "create",
    status: "success",
    user_id: "john.doe@example.com",
    timestamp: "2023-05-15T10:30:00Z",
    description: "Created a new user account for jane.smith@example.com",
  },
  {
    _id: "2",
    action_type: "update",
    status: "success",
    user_id: "admin@example.com",
    timestamp: "2023-05-15T11:45:00Z",
    description: "Updated user permissions for marketing team",
  },
  {
    _id: "3",
    action_type: "delete",
    status: "success",
    user_id: "system",
    timestamp: "2023-05-15T12:20:00Z",
    description: "Deleted inactive user accounts older than 1 year",
  },
  {
    _id: "4",
    action_type: "login",
    status: "failed",
    user_id: "unknown@example.com",
    timestamp: "2023-05-15T13:10:00Z",
    description: "Failed login attempt with incorrect password",
  },
  {
    _id: "5",
    action_type: "logout",
    status: "success",
    user_id: "jane.smith@example.com",
    timestamp: "2023-05-15T14:30:00Z",
    description: "User logged out after 2 hours of activity",
  },
];

const AuditTrail = () => {
  return (
    <>
      {auditLogs.length === 0 ? (
        <>"No audit logs found."</>
      ) : (
        <div className="custom-scrollbar flex h-[calc(100vh-180px)] w-full justify-center overflow-auto px-4">
          <div className="mt-8 w-[40%]">
            {auditLogs.map((log, index) => (
              <div
                key={log._id || log.id || Date.now()}
                className={`relative ${
                  index === auditLogs.length - 1
                    ? ""
                    : "border-l-2 border-blue-500"
                } pb-10 pl-10`}
              >
                <div className="absolute -left-[17.5px] top-0">
                  <div
                    className={`rounded-full p-2 ${
                      actionBgColors[log.action_type] || "bg-white"
                    }`}
                  >
                    {iconMap[log.action_type] || iconMap.default}
                  </div>
                </div>

                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <p className="font-lato text-[14px] text-[#000000]">
                      {log.user_id || "System"}
                    </p>
                    <span
                      className={`rounded-full border px-2 py-0.5 text-xs ${
                        statusTagColor[log.status] ||
                        "border-primary text-primary"
                      }`}
                    >
                      {log.status === "success"
                        ? "New"
                        : log.status || "Unknown"}
                    </span>
                  </div>

                  <span className="text-xs text-gray-500">
                    {log.timestamp
                      ? formatDistanceToNow(new Date(log.timestamp), {
                          addSuffix: true,
                          includeSeconds: false,
                        }).replace("about ", "")
                      : "Recently"}
                  </span>
                </div>

                <div className="mt-2 bg-[#F0F8FF] px-2 py-3 text-sm font-light text-[#000000] text-opacity-75">
                  <p>{log.description || "No description available"}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </>
  );
};

export default AuditTrail;
