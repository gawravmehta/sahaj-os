import { BiSupport } from "react-icons/bi";
import { FiSettings } from "react-icons/fi";
import { LuBookOpen, LuLogs } from "react-icons/lu";
import { MdOutlineContactPhone } from "react-icons/md";
import { RiFeedbackLine, RiQuestionnaireLine } from "react-icons/ri";
import { AiOutlineApi } from "react-icons/ai";

export const menuItems = [
  {
    href: "/knowledge-base",
    label: "Knowledge Base",
    icon: <LuBookOpen size={18} />,
  },
  {
    href: "https://qna.concur.live",
    label: "QNA",
    icon: <RiQuestionnaireLine size={18} />,
    external: true,
  },
  { href: "/support", label: "Support", icon: <BiSupport size={18} /> },
  { href: "/feedback", label: "Feedback", icon: <RiFeedbackLine size={18} /> },
  {
    href: "/contact",
    label: "Contact Us",
    icon: <MdOutlineContactPhone size={18} />,
  },
  {
    href: "/logs",
    label: "Logs",
    icon: <LuLogs size={18} />,
  },

  { href: "/setting", label: "Settings", icon: <FiSettings size={18} /> },
];
