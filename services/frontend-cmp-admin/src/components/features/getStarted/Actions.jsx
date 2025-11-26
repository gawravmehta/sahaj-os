import React from "react";

const Actions = ({ data, setData, updateActionStatus }) => {
  return (
    <div>
      <ul className="space-y-2">
        {data?.recommended_actions.map((actionItem, i) => (
          <li
            key={i}
            className="flex items-center justify-between  border border-borderthree bg-white p-4 "
          >
            <div className="flex-1">
              <h3 className="text-sm font-semibold">
                {actionItem?.action_title}
              </h3>
              <p className="text-xs text-gray-500">
                {actionItem?.action_description}
              </p>
            </div>

            <div
              className={`h-8 w-8 cursor-pointer  bg-white border border-[#1F2046]
               flex items-center justify-center`}
              onClick={() => {
                if (!actionItem?.is_action_completed) {
                  updateActionStatus(actionItem.action_number);

                  setData((prevData) => ({
                    ...prevData,
                    recommended_actions: prevData.recommended_actions.map((a) =>
                      a.action_number === String(actionItem.action_number)
                        ? { ...a, is_action_completed: true }
                        : a
                    ),
                  }));
                }
              }}
            >
              {actionItem?.is_action_completed && (
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="h-6 w-6 text-[#1F2046]"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M5 13l4 4L19 7"
                  />
                </svg>
              )}
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default Actions;
