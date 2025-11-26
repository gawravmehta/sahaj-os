import Sidebar from "@/components/shared/Sidebar";
import { PermissionProvider } from "@/contexts/PermissionContext";

const layout = ({ children }) => {
  return (
    <PermissionProvider>
      <Sidebar>
        <div className="pt-12">{children}</div>
      </Sidebar>
    </PermissionProvider>
  );
};

export default layout;
