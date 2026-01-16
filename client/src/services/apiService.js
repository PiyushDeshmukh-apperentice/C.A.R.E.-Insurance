const API_BASE = "http://localhost:8000";

// ---------------- AUTH ----------------

export const signupRequest = async (name, email, mobile, password) => {
  try {
    const formData = new FormData();
    formData.append("username", name);  // Backend expects 'username', not 'name'
    formData.append("email", email);
    formData.append("mobile", mobile);
    formData.append("password", password);

    const res = await fetch(`${API_BASE}/auth/signup`, {
      method: "POST",
      body: formData
    });

    const data = await res.json();
    
    // Log for debugging
    console.log("Signup response status:", res.status);
    console.log("Signup response data:", data);

    // Check if request was successful
    if (!res.ok) {
      return { 
        success: false, 
        detail: data.detail || "Signup failed" 
      };
    }

    return { success: true, ...data };
  } catch (error) {
    console.error("Signup request error:", error);
    return { 
      success: false, 
      detail: "Network error. Please try again." 
    };
  }
};

export const verifyOtpRequest = async (userId, emailOtp, smsOtp) => {
  try {
    const formData = new FormData();
    formData.append("user_id", userId);
    formData.append("email_otp", emailOtp);
    formData.append("sms_otp", smsOtp);

    const res = await fetch(`${API_BASE}/auth/verify`, {
      method: "POST",
      body: formData
    });

    const data = await res.json();
    
    console.log("OTP verify response status:", res.status);
    console.log("OTP verify response data:", data);

    if (!res.ok) {
      return { 
        success: false, 
        detail: data.detail || "Verification failed" 
      };
    }

    return { success: true, ...data };
  } catch (error) {
    console.error("OTP verify request error:", error);
    return { 
      success: false, 
      detail: "Network error. Please try again." 
    };
  }
};

export const loginRequest = async (email, password) => {
  try {
    const formData = new FormData();
    formData.append("email", email);
    formData.append("password", password);

    const res = await fetch(`${API_BASE}/auth/login`, {
      method: "POST",
      body: formData
    });

    const data = await res.json();
    
    console.log("Login response status:", res.status);
    console.log("Login response data:", data);

    if (!res.ok) {
      return { 
        success: false, 
        detail: data.detail || "Login failed" 
      };
    }

    return { success: true, ...data };
  } catch (error) {
    console.error("Login request error:", error);
    return { 
      success: false, 
      detail: "Network error. Please try again." 
    };
  }
};

// ---------------- CLAIMS ----------------

export const submitClaimRequest = async (email, policyName, files, token) => {
  try {
    const formData = new FormData();
    formData.append("email", email);
    formData.append("policy_name", policyName);

    files.forEach(file => {
      formData.append("files", file);
    });

    const res = await fetch(`${API_BASE}/claims/submit`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`
      },
      body: formData
    });

    const data = await res.json();

    if (!res.ok) {
      return { 
        success: false, 
        detail: data.detail || "Claim submission failed" 
      };
    }

    return { success: true, ...data };
  } catch (error) {
    console.error("Claim submit error:", error);
    return { 
      success: false, 
      detail: "Network error. Please try again." 
    };
  }
};

export const getPoliciesRequest = async (token) => {
  try {
    const res = await fetch(`${API_BASE}/policies`, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    });

    const data = await res.json();

    if (!res.ok) {
      return { 
        success: false, 
        detail: data.detail || "Failed to fetch policies" 
      };
    }

    return { success: true, data: data.policies || [] };
  } catch (error) {
    console.error("Get policies error:", error);
    return { 
      success: false, 
      detail: "Network error. Please try again.",
      data: []
    };
  }
};

export const getClaimsRequest = async (token) => {
  try {
    const res = await fetch(`${API_BASE}/claims`, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    });

    const data = await res.json();

    if (!res.ok) {
      return { 
        success: false, 
        detail: data.detail || "Failed to fetch claims" 
      };
    }

    return { success: true, data: data.claims || [] };
  } catch (error) {
    console.error("Get claims error:", error);
    return { 
      success: false, 
      detail: "Network error. Please try again.",
      data: []
    };
  }
};

// ---------------- SESSION ----------------

export const storeSession = (data) => {
  localStorage.setItem("auth", JSON.stringify(data));
};

export const getSession = () => {
  const data = localStorage.getItem("auth");
  return data ? JSON.parse(data) : null;
};

export const clearSession = () => {
  localStorage.removeItem("auth");
};

export const isLoggedIn = () => {
  return !!localStorage.getItem("auth");
};

export default {
  signupRequest,
  verifyOtpRequest,
  loginRequest,
  submitClaimRequest,
  getPoliciesRequest,
  getClaimsRequest,
  storeSession,
  getSession,
  clearSession,
  isLoggedIn
};