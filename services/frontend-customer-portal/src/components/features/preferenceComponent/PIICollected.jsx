"use client";

function PIICollected({ dataElements }) {
  return (
    <div>
      <div>
        <div className="w-full p-2 border border-[#C7CFE2]">
          <div className="flex items-center gap-1 py-2 px-1">
            <h4>Data Collected</h4>
          </div>

          <ul className="flex flex-wrap gap-2 px-2 text-white w-full text-center">
            {dataElements?.map((element, index) => (
              <li
                key={index}
                className="flex items-center gap-2 px-3 py-1 bg-[#1D478E] rounded-full  "
              >
                {element?.data_element_title}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}

export default PIICollected;
