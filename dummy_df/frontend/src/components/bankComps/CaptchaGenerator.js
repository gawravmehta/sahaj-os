"use client";
import { useState, useEffect } from "react";
import { IoMdRefresh } from "react-icons/io";

const CaptchaGenerator = () => {
  const [captcha, setCaptcha] = useState("");
  const [userInput, setUserInput] = useState("");
  const [message, setMessage] = useState("");

  useEffect(() => {
    setCaptcha(generateCaptcha());
  }, []);

  function generateCaptcha() {
    const chars =
      "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ";
    let captcha = "";
    for (let i = 0; i < 6; i++) {
      captcha += chars[Math.floor(Math.random() * chars.length)];
    }
    return captcha;
  }

  const handleRefreshCaptcha = () => {
    setCaptcha(generateCaptcha());
    setUserInput("");
    setMessage("");
  };

  return (
    <div className="mt-12">
      <p className="text-gray-300 text-lg font-semibold">
        Type the code shown (Case Sensitive)
      </p>
      <div className="captcha-box flex items-center gap-2 mb-4 ">
        <span className="text-lg font-bold tracking-widest w-16">
          {captcha}
         
        </span>
        <button onClick={handleRefreshCaptcha} className="ml-2">
          <IoMdRefresh size={20} />
        </button>
        <input
          type="text"
          placeholder="Enter Code"
          value={userInput}
          onChange={(e) => setUserInput(e.target.value)}
          className="w-1/4 py-2 border-b border-gray-300 outline-none mb-4"
        />
      </div>
    </div>
  );
};

export default CaptchaGenerator;
