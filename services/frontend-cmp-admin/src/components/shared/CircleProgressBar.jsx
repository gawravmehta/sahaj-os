const CircleProgressBar = ({ score }) => (
    <div className="relative flex items-center justify-center pt-12 ">
      <div
        className="absolute w-[133px] h-[133px] rounded-full border-2 border-gray-300"
      ></div>
      <div
        className="absolute w-[133px] h-[133px] rounded-full"
        style={{
          background: `conic-gradient(primary 0% ${score}%, #f3f3f3 ${score}% 10%)`,
        }}
      ></div>
      <div className="absolute w-[86px] h-[86px] flex items-center justify-center rounded-full bg-[#f9f9f9]">
        <p
          className={`text-xl font-semibold ${
            score === 0 ? "text-[#f34848]" : "text-primary"
          }`}
        >
          {score || 0}%
        </p>
      </div>
    </div>
  );
  
  export default CircleProgressBar;