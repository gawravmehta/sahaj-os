import { FaCheck, FaTimes } from "react-icons/fa";

const ConsentStatusBar = ({ consent }) => {
  const start = new Date(consent.timestamp).getTime();
  const end = new Date(consent.expiry).getTime();
  const now = Date.now();

  let progress = Math.min(
    100,
    Math.max(0, ((now - start) / (end - start)) * 100)
  );

  const isExpired = now >= end;
  const isExpiringSoon = !isExpired && progress >= 80;

  if (isExpired) progress = 100;

  const barColor = isExpired
    ? "bg-red-500"
    : isExpiringSoon
    ? "bg-yellow-500"
    : "bg-green-500";

  const icon = isExpired ? (
    <FaTimes className="text-white h-3 w-3" />
  ) : (
    <FaCheck className="text-white h-3 w-3" />
  );

  const iconBg = isExpired ? "bg-red-500" : "bg-green-500";

  return (
    <div className="py-2 text-xs text-gray-600">
      <div className="flex justify-between">
        <div>
          <p className="font-semibold">Consent</p>
          <p>{new Date(consent.timestamp).toLocaleString("en-GB")}</p>
        </div>
        <div className="text-right">
          <p className="font-semibold">Expiry</p>
          <p>{new Date(consent.expiry).toLocaleString("en-GB")}</p>
        </div>
      </div>

      <div className="flex items-center mt-3 gap-2">
        <div
          className={`w-5 h-5 flex items-center justify-center rounded-full ${iconBg}`}
        >
          {icon}
        </div>

        <div className="w-full h-2 bg-gray-300 rounded-full overflow-hidden">
          <div
            className={`h-2 ${barColor} transition-all duration-500`}
            style={{ width: `${progress}%` }}
          ></div>
        </div>
      </div>
    </div>
  );
};

export default ConsentStatusBar;
