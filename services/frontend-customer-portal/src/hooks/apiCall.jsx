import Cookies from "js-cookie";

const baseURL = process.env.NEXT_PUBLIC_CUSTOMER_URL || "";

const DF_ID = process.env.NEXT_PUBLIC_DF_ID || "";

const defaultHeaders = {
  "Content-Type": "application/json",
  Accept: "application/json",
  "df-id": DF_ID,
};

export const apiCall = async (endpoint, options = {}) => {
  const {
    method = "GET",
    data = null,
    params = {},
    headers = {},
    returnFullResponse = false,
    responseType = null, // Add responseType option
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

    // Handle blob response type for file downloads
    if (responseType === "blob") {
      if (!res.ok) {
        // Try to parse error as JSON if possible
        const contentType = res.headers.get("content-type");
        let errorData = null;
        if (contentType && contentType.includes("application/json")) {
          errorData = await res.json();
        } else {
          errorData = await res.text();
        }
        throw {
          status: res.status,
          message: errorData?.message || res.statusText,
          data: errorData,
        };
      }
      return await res.blob();
    }

    const contentType = res.headers.get("content-type");

    let responseData = null;
    if (contentType && contentType.includes("application/json")) {
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
      ? { data: responseData, status: res.status }
      : responseData;
  } catch (error) {
    throw error;
  }
};

export const uploadFile = async (endpoint, formData) => {
  const token = Cookies.get("access_token");

  try {
    const response = await fetch(`${baseURL}${endpoint}`, {
      method: formData.method || "PUT",
      headers: {
        Authorization: `Bearer ${token}`,
        "df-id": DF_ID,
      },
      body: formData.data,
    });

    const responseData = await response.json();

    if (!response.ok) {
      throw {
        status: response.status,
        message: responseData?.message || response.statusText,
        data: responseData,
      };
    }

    return responseData;
  } catch (error) {
    throw error;
  }
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
