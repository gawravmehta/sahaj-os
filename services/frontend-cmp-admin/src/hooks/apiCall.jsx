import Cookies from "js-cookie";

const baseURL = process.env.NEXT_PUBLIC_ADMIN_URL || "";

const defaultHeaders = {
  "Content-Type": "application/json",
  Accept: "application/json",
};

export const apiCall = async (endpoint, options = {}) => {
  const {
    method = "GET",
    data = null,
    params = {},
    headers = {},
    returnFullResponse = false,
  } = options;

  const token = Cookies.get("access_token");

  const queryString = new URLSearchParams(params).toString();
  const url = `${baseURL}${endpoint}${queryString ? `?${queryString}` : ""}`;

  const fetchOptions = {
    method,
    headers: {
      ...defaultHeaders,
      ...headers,
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
  };

  if (data) {
    fetchOptions.body = JSON.stringify(data);
  }

  try {
    const res = await fetch(url, fetchOptions);

    if (res.status === 204) {
      return returnFullResponse ? { data: null, status: 204 } : null;
    }

    const contentType = res.headers.get("content-type");

    let responseData = null;
    if (options.responseType === "blob") {
      responseData = await res.blob();
    } else if (contentType && contentType.includes("application/json")) {
      responseData = await res.json();
    } else {
      responseData = await res.text();
    }

    if (!res.ok) {
      throw {
        status: res.status,
        message: responseData?.message || res.statusText,
        data: responseData,
      };
    }

    return returnFullResponse
      ? { data: responseData, status: res.status, headers: res.headers }
      : responseData;
  } catch (error) {
    throw error;
  }
};

export const uploadFile = async (
  endpoint,
  formData,
  setUploadProgress,
  headers = {}
) => {
  const token = Cookies.get("access_token");

  const xhr = new XMLHttpRequest();
  const url = `${baseURL}${endpoint}`;

  return new Promise((resolve, reject) => {
    xhr.open("POST", url);
    if (token) xhr.setRequestHeader("Authorization", `Bearer ${token}`);

    for (const key in headers) {
      xhr.setRequestHeader(key, headers[key]);
    }

    xhr.upload.onprogress = function (event) {
      if (event.lengthComputable && setUploadProgress) {
        const progress = Math.round((event.loaded / event.total) * 100);

        setUploadProgress(progress - 1);
      }
    };

    xhr.onload = () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        try {
          resolve(JSON.parse(xhr.responseText));
        } catch {
          resolve(xhr.responseText);
        }
      } else {
        reject(xhr.responseText);
      }
    };

    xhr.onerror = () => reject("Upload failed");
    xhr.send(formData);
  });
};

export const addNewTags = async ({ newTags }) => {
  try {
    const response = await apiCall("/tags/add", {
      method: "POST",
      data: newTags,
    });
    return response;
  } catch (error) {
    console.error("Error adding new tags:", error);
    throw error;
  }
};
