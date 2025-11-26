import DataTable from "@/components/shared/data-table/DataTable";
import React from "react";

const DepartmentAdmin = ({ selectedDept }) => {
  return (
    <div className="mb-6 border-b">
      <div className="flex w-full items-center justify-between pl-6">
        <h3 className="text-base text-primary">Department Admins</h3>
      </div>
      {selectedDept.department_admins_data?.length > 0 ? (
        <DataTable
          columns={[
            {
              header: "Name",
              accessor: "first_name",
              headerClassName: " text-start  w-80",
              render: (name, row) => (
                <span>
                  {name} {row.last_name || ""}
                </span>
              ),
            },
            {
              header: "Email",
              accessor: "email",
              headerClassName: " text-start  w-70",
            },
            {
              header: "Designation",
              accessor: "designation",
              headerClassName: " text-start  ",
              render: (designation) => designation || "N/A",
            },
          ]}
          data={selectedDept.department_admins_data}
          tableHeight="750px"
          totalPages={1}
          currentPage={1}
          rowsPerPageState={5}
          setRowsPerPageState={() => {}}
          setCurrentPage={() => {}}
          hasSerialNumber
          searchable={false}
          hasFilterOption={false}
        />
      ) : (
        <div className="flex items-center justify-center rounded-lg border border-dashed border-gray-300 p-4">
          <p className="text-gray-500">No department admins found.</p>
        </div>
      )}
    </div>
  );
};

export default DepartmentAdmin;
