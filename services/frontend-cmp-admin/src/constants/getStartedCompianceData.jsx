
import { BiSupport } from "react-icons/bi";
import { AiOutlineMail } from "react-icons/ai";
import { TbFileInvoice } from "react-icons/tb";
import { AiOutlineYoutube } from "react-icons/ai";

export const getStartedComplianceData =  [
  {
    title: "Support",
    description: "Get help with all your DPDPA compliance requirements.",
    icon: <BiSupport size={30} />,
    url: "https://saas-bahu.vercel.app/support",
  },
  {
    title: "Knowledge",
    description: "Access detailed articles and guides on privacy compliance.",
    icon: <AiOutlineMail size={30} />,
    url: "https://saas-bahu.vercel.app/knowledge-base",
  },
  {
    title: "Email",
    description: "Connect with our experts for tailored support.",
    icon: <TbFileInvoice size={30} />,
    url: "info@concur.live",
  },
  {
    title: "YouTube",
    description: "Watch tutorials and insights to streamline your journey.",
    icon: <AiOutlineYoutube size={30} />,
    url: "https://www.youtube.com/@concurlive",
  },
];