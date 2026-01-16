import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useToastContext } from './Toast';
import apiService from '../services/apiService';

const LoginModal = ({ isOpen, onClose }) => {
  const navigate = useNavigate();
  const toast = useToastContext();

  const [step, setStep] = useState("login");
  const [isLoading, setIsLoading] = useState(false);
  const [errors, setErrors] = useState({});

  const [userId, setUserId] = useState(null);
  const [returnedOtps, setReturnedOtps] = useState({ emailOtp: "", smsOtp: "" });

  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    password: '',
    confirmPassword: '',
    digilockerConsent: false
  });

  const [otpData, setOtpData] = useState({
    emailOtp: '',
    smsOtp: ''
  });

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData({
      ...formData,
      [name]: type === 'checkbox' ? checked : value
    });
    if (errors[name]) {
      setErrors({ ...errors, [name]: '' });
    }
  };

  const handleOtpChange = (e) => {
    const { name, value } = e.target;
    setOtpData({
      ...otpData,
      [name]: value
    });
    if (errors[name]) {
      setErrors({ ...errors, [name]: '' });
    }
  };

  const validatePassword = (password) => {
    const minLength = password.length >= 8;
    const hasUpperCase = /[A-Z]/.test(password);
    const hasLowerCase = /[a-z]/.test(password);
    const hasNumber = /[0-9]/.test(password);
    const hasSpecialChar = /[!@#$%^&*(),.?":{}|<>]/.test(password);

    return {
      isValid: minLength && hasUpperCase && hasLowerCase && hasNumber && hasSpecialChar,
      message: !minLength ? 'Password must be at least 8 characters long' :
        !hasUpperCase ? 'Password must contain an uppercase letter' :
          !hasLowerCase ? 'Password must contain a lowercase letter' :
            !hasNumber ? 'Password must contain a number' :
              !hasSpecialChar ? 'Password must contain a special character' : ''
    };
  };

  const validateSignupForm = () => {
    const newErrors = {};

    if (!formData.name.trim()) newErrors.name = 'Name is required';
    if (!formData.email.trim()) newErrors.email = 'Email is required';
    else if (!/\S+@\S+\.\S+/.test(formData.email)) newErrors.email = 'Email is invalid';
    if (!formData.phone.trim()) newErrors.phone = 'Phone number is required';
    else if (!/^\d{10}$/.test(formData.phone.replace(/\D/g, ''))) {
      newErrors.phone = 'Phone number must be 10 digits';
    }

    const passwordValidation = validatePassword(formData.password);
    if (!passwordValidation.isValid) newErrors.password = passwordValidation.message;

    if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match';
    }

    if (!formData.digilockerConsent) {
      newErrors.digilockerConsent = 'Please provide consent to access your documents';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const validateLoginForm = () => {
    const newErrors = {};

    if (!formData.email.trim()) newErrors.email = 'Email is required';
    if (!formData.password.trim()) newErrors.password = 'Password is required';

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const validateOtpForm = () => {
    const newErrors = {};

    if (!otpData.emailOtp.trim()) newErrors.emailOtp = 'Email OTP is required';
    if (!otpData.smsOtp.trim()) newErrors.smsOtp = 'SMS OTP is required';

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      // ---------------- SIGNUP ----------------
      if (step === "signup") {
        if (!validateSignupForm()) {
          setIsLoading(false);
          return;
        }

        const res = await apiService.signupRequest(
          formData.name,
          formData.email,
          formData.phone,
          formData.password
        );

        console.log("Signup result:", res);

        // Check for both user_id and message to confirm success
        if (res.success && (res.user_id || res.message)) {
          toast.success("Registration successful! Please verify OTPs sent to your email and phone.");
          setUserId(res.user_id);
          setReturnedOtps({
            emailOtp: res.email_otp || "",
            smsOtp: res.sms_otp || ""
          });
          console.log("Email OTP:", res.email_otp);
          console.log("SMS OTP:", res.sms_otp);
          setStep("otp");
        } else {
          toast.error(res.detail || "Signup failed");
        }
      }

      // ---------------- OTP VERIFY ----------------
      else if (step === "otp") {
        if (!validateOtpForm()) {
          setIsLoading(false);
          return;
        }

        const res = await apiService.verifyOtpRequest(
          userId,
          otpData.emailOtp,
          otpData.smsOtp
        );

        console.log("OTP verify result:", res);

        if (res.success && res.message) {
          toast.success("Account verified successfully! Please login.");
          resetForm();
          setStep("login");
        } else {
          toast.error(res.detail || "OTP verification failed");
        }
      }

      // ---------------- LOGIN ----------------
      else {
        if (!validateLoginForm()) {
          setIsLoading(false);
          return;
        }

        const res = await apiService.loginRequest(
          formData.email,
          formData.password
        );

        console.log("Login result:", res);

        if (!res.success || !res.access_token) {
          toast.error(res.detail || "Invalid credentials");
          setIsLoading(false);
          return;
        }

        apiService.storeSession({
          token: res.access_token,
          userId: res.user.id,
          sessionStartTime: new Date().toISOString(),
          userData: {
            id: res.user.id,
            email: res.user.email,
            username: res.user.username  // Backend returns username, not name
          }
        });

        toast.success("Logged in successfully!");
        onClose();
        navigate("/profile");
      }
    } catch (err) {
      console.error("Error:", err);
      toast.error("Something went wrong. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  const resetForm = () => {
    setFormData({
      name: '',
      email: '',
      phone: '',
      password: '',
      confirmPassword: '',
      digilockerConsent: false
    });
    setOtpData({
      emailOtp: '',
      smsOtp: ''
    });
    setUserId(null);
    setReturnedOtps({ emailOtp: "", smsOtp: "" });
    setErrors({});
  };

  const toggleMode = () => {
    if (step === "login") {
      setStep("signup");
    } else {
      setStep("login");
    }
    resetForm();
  };

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 animate-fadeIn overflow-y-auto"
      style={{ backgroundColor: 'rgba(12, 32, 75, 0.6)' }}
      onClick={onClose}
    >
      <div
        className="relative w-full max-w-md rounded-[20px] p-8 shadow-2xl animate-slideUp my-8"
        style={{
          backgroundColor: 'var(--secondary-background)',
          minHeight: step === "signup" ? '700px' : 'auto'
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Close button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 w-8 h-8 flex items-center justify-center rounded-full hover:bg-gray-100 transition-all duration-300 cursor-pointer"
          style={{ color: 'var(--text-muted)' }}
        >
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
            <path
              d="M15 5L5 15M5 5L15 15"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </button>

        {/* Logo */}
        <div className="flex justify-center mb-4">
          <img
            src="/images/img_68b9b823a50348f.png"
            alt="Sureva Logo"
            className="w-[114px] h-[30px]"
          />
        </div>

        {/* Title */}
        <h2
          className="font-['Roboto_Serif'] font-normal text-center mb-2"
          style={{
            fontSize: 'var(--font-size-xl)',
            lineHeight: 'var(--line-height-2xl)',
            color: 'var(--text-primary)'
          }}
        >
          {step === "signup" ? 'Create Account' : step === "otp" ? 'Verify OTP' : 'Welcome Back'}
        </h2>

        <p
          className="font-['Inter'] font-normal text-center mb-6"
          style={{
            fontSize: 'var(--font-size-sm)',
            lineHeight: 'var(--line-height-base)',
            color: 'var(--text-muted)'
          }}
        >
          {step === "signup"
            ? 'Sign up to get started with your insurance'
            : step === "otp"
              ? 'Enter the OTPs sent to your email and phone'
              : 'Sign in to access your account'}
        </p>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* SIGNUP FORM */}
          {step === "signup" && (
            <>
              {/* Name field */}
              <div className="space-y-1.5">
                <label
                  htmlFor="name"
                  className="block font-['Inter'] font-normal"
                  style={{
                    fontSize: 'var(--font-size-sm)',
                    color: 'var(--text-secondary)'
                  }}
                >
                  Name
                </label>
                <input
                  type="text"
                  id="name"
                  name="name"
                  value={formData.name}
                  onChange={handleChange}
                  className="w-full px-4 py-2.5 rounded-[12px] border font-['Inter'] font-normal focus:outline-none focus:ring-2 transition-all duration-300"
                  style={{
                    fontSize: 'var(--font-size-sm)',
                    borderColor: errors.name ? '#ef4444' : '#e5e7eb',
                    backgroundColor: 'var(--secondary-background)',
                    color: 'var(--text-primary)'
                  }}
                  placeholder="Enter your full name"
                />
                {errors.name && (
                  <p className="text-red-500 text-xs mt-1">{errors.name}</p>
                )}
              </div>

              {/* Email field */}
              <div className="space-y-4">
                {/* Email field */}
                <div className="space-y-1.5">
                  <label
                    htmlFor="email"
                    className="block font-['Inter'] font-normal"
                    style={{
                      fontSize: 'var(--font-size-sm)',
                      color: 'var(--text-secondary)'
                    }}
                  >
                    Email
                  </label>
                  <input
                    type="email"
                    id="email"
                    name="email"
                    value={formData.email}
                    onChange={handleChange}
                    className="w-full px-4 py-2.5 rounded-[12px] border font-['Inter'] font-normal focus:outline-none focus:ring-2 transition-all duration-300"
                    style={{
                      fontSize: 'var(--font-size-sm)',
                      borderColor: errors.email ? '#ef4444' : '#e5e7eb',
                      backgroundColor: 'var(--secondary-background)',
                      color: 'var(--text-primary)'
                    }}
                    placeholder="Enter your email"
                  />
                  {errors.email && (
                    <p className="text-red-500 text-xs mt-1">{errors.email}</p>
                  )}
                </div>

                {/* Phone field */}
                <div className="space-y-1.5">
                  <label
                    htmlFor="phone"
                    className="block font-['Inter'] font-normal"
                    style={{
                      fontSize: 'var(--font-size-sm)',
                      color: 'var(--text-secondary)'
                    }}
                  >
                    Phone Number
                  </label>
                  <input
                    type="tel"
                    id="phone"
                    name="phone"
                    value={formData.phone}
                    onChange={handleChange}
                    className="w-full px-4 py-2.5 rounded-[12px] border font-['Inter'] font-normal focus:outline-none focus:ring-2 transition-all duration-300"
                    style={{
                      fontSize: 'var(--font-size-sm)',
                      borderColor: errors.phone ? '#ef4444' : '#e5e7eb',
                      backgroundColor: 'var(--secondary-background)',
                      color: 'var(--text-primary)'
                    }}
                    placeholder="Enter your phone number"
                  />
                  {errors.phone && (
                    <p className="text-red-500 text-xs mt-1">{errors.phone}</p>
                  )}
                </div>
                
              </div>

              {/* Password field */}
              <div className="space-y-1.5">
                <label
                  htmlFor="password"
                  className="block font-['Inter'] font-normal"
                  style={{
                    fontSize: 'var(--font-size-sm)',
                    color: 'var(--text-secondary)'
                  }}
                >
                  Password
                </label>
                <input
                  type="password"
                  id="password"
                  name="password"
                  value={formData.password}
                  onChange={handleChange}
                  className="w-full px-4 py-2.5 rounded-[12px] border font-['Inter'] font-normal focus:outline-none focus:ring-2 transition-all duration-300"
                  style={{
                    fontSize: 'var(--font-size-sm)',
                    borderColor: errors.password ? '#ef4444' : '#e5e7eb',
                    backgroundColor: 'var(--secondary-background)',
                    color: 'var(--text-primary)'
                  }}
                  placeholder="Enter your password"
                />
                {errors.password && (
                  <p className="text-red-500 text-xs mt-1">{errors.password}</p>
                )}
                <p className="text-xs" style={{ color: 'var(--text-muted)' }}>
                  Must contain: 8+ characters, uppercase, lowercase, number, special character
                </p>
              </div>

              {/* Confirm Password field */}
              <div className="space-y-1.5">
                <label
                  htmlFor="confirmPassword"
                  className="block font-['Inter'] font-normal"
                  style={{
                    fontSize: 'var(--font-size-sm)',
                    color: 'var(--text-secondary)'
                  }}
                >
                  Confirm Password
                </label>
                <input
                  type="password"
                  id="confirmPassword"
                  name="confirmPassword"
                  value={formData.confirmPassword}
                  onChange={handleChange}
                  className="w-full px-4 py-2.5 rounded-[12px] border font-['Inter'] font-normal focus:outline-none focus:ring-2 transition-all duration-300"
                  style={{
                    fontSize: 'var(--font-size-sm)',
                    borderColor: errors.confirmPassword ? '#ef4444' : '#e5e7eb',
                    backgroundColor: 'var(--secondary-background)',
                    color: 'var(--text-primary)'
                  }}
                  placeholder="Re-enter your password"
                />
                {errors.confirmPassword && (
                  <p className="text-red-500 text-xs mt-1">{errors.confirmPassword}</p>
                )}
              </div>

              {/* DigiLocker Consent Checkbox */}
              <div className="space-y-2 pt-2">
                <label className="flex items-start gap-3 cursor-pointer group">
                  <div className="relative flex items-center justify-center mt-0.5">
                    <input
                      type="checkbox"
                      name="digilockerConsent"
                      checked={formData.digilockerConsent}
                      onChange={handleChange}
                      className="w-5 h-5 rounded border-2 cursor-pointer transition-all duration-300 appearance-none checked:bg-blue-500 checked:border-blue-500"
                      style={{
                        borderColor: errors.digilockerConsent ? '#ef4444' : '#d1d5db'
                      }}
                    />
                    {formData.digilockerConsent && (
                      <svg
                        className="absolute w-3 h-3 text-white pointer-events-none"
                        viewBox="0 0 12 12"
                        fill="none"
                      >
                        <path
                          d="M10 3L4.5 8.5L2 6"
                          stroke="currentColor"
                          strokeWidth="2"
                          strokeLinecap="round"
                          strokeLinejoin="round"
                        />
                      </svg>
                    )}
                  </div>
                  <div className="flex-1">
                    <span
                      className="font-['Inter'] font-normal block"
                      style={{
                        fontSize: 'var(--font-size-sm)',
                        color: 'var(--text-secondary)',
                        lineHeight: '1.5'
                      }}
                    >
                      I consent to access my Aadhaar Card, PAN Card, and other documents from DigiLocker for verification purposes
                    </span>
                    {errors.digilockerConsent && (
                      <p className="text-red-500 text-xs mt-1">{errors.digilockerConsent}</p>
                    )}
                  </div>
                </label>
              </div>

              {/* Submit button */}
              <button
                type="submit"
                disabled={isLoading}
                className="w-full py-3 px-6 rounded-[12px] font-['Inter'] font-normal hover:opacity-80 transition-all duration-300 cursor-pointer mt-4 disabled:opacity-50"
                style={{
                  fontSize: 'var(--font-size-base)',
                  lineHeight: 'var(--line-height-base)',
                  backgroundColor: 'var(--primary-background)',
                  color: 'var(--primary-foreground)'
                }}
              >
                {isLoading ? 'Creating Account...' : 'Create Account'}
              </button>
            </>
          )}

          {/* OTP VERIFICATION FORM */}
          {step === "otp" && (
            <>
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
                <p className="text-sm text-blue-800">
                  <strong>For testing:</strong> Check console for OTP values
                </p>
                {returnedOtps.emailOtp && (
                  <p className="text-xs text-blue-600 mt-1">Email OTP: {returnedOtps.emailOtp}</p>
                )}
                {returnedOtps.smsOtp && (
                  <p className="text-xs text-blue-600">SMS OTP: {returnedOtps.smsOtp}</p>
                )}
              </div>

              {/* Email OTP field */}
              <div className="space-y-1.5">
                <label
                  htmlFor="emailOtp"
                  className="block font-['Inter'] font-normal"
                  style={{
                    fontSize: 'var(--font-size-sm)',
                    color: 'var(--text-secondary)'
                  }}
                >
                  Email OTP
                </label>
                <input
                  type="text"
                  id="emailOtp"
                  name="emailOtp"
                  value={otpData.emailOtp}
                  onChange={handleOtpChange}
                  maxLength="6"
                  className="w-full px-4 py-2.5 rounded-[12px] border font-['Inter'] font-normal focus:outline-none focus:ring-2 transition-all duration-300"
                  style={{
                    fontSize: 'var(--font-size-sm)',
                    borderColor: errors.emailOtp ? '#ef4444' : '#e5e7eb',
                    backgroundColor: 'var(--secondary-background)',
                    color: 'var(--text-primary)'
                  }}
                  placeholder="Enter 6-digit email OTP"
                />
                {errors.emailOtp && (
                  <p className="text-red-500 text-xs mt-1">{errors.emailOtp}</p>
                )}
              </div>

              {/* SMS OTP field */}
              <div className="space-y-1.5">
                <label
                  htmlFor="smsOtp"
                  className="block font-['Inter'] font-normal"
                  style={{
                    fontSize: 'var(--font-size-sm)',
                    color: 'var(--text-secondary)'
                  }}
                >
                  SMS OTP
                </label>
                <input
                  type="text"
                  id="smsOtp"
                  name="smsOtp"
                  value={otpData.smsOtp}
                  onChange={handleOtpChange}
                  maxLength="6"
                  className="w-full px-4 py-2.5 rounded-[12px] border font-['Inter'] font-normal focus:outline-none focus:ring-2 transition-all duration-300"
                  style={{
                    fontSize: 'var(--font-size-sm)',
                    borderColor: errors.smsOtp ? '#ef4444' : '#e5e7eb',
                    backgroundColor: 'var(--secondary-background)',
                    color: 'var(--text-primary)'
                  }}
                  placeholder="Enter 6-digit SMS OTP"
                />
                {errors.smsOtp && (
                  <p className="text-red-500 text-xs mt-1">{errors.smsOtp}</p>
                )}
              </div>

              {/* Submit button */}
              <button
                type="submit"
                disabled={isLoading}
                className="w-full py-3 px-6 rounded-[12px] font-['Inter'] font-normal hover:opacity-80 transition-all duration-300 cursor-pointer disabled:opacity-50"
                style={{
                  fontSize: 'var(--font-size-base)',
                  lineHeight: 'var(--line-height-base)',
                  backgroundColor: 'var(--primary-background)',
                  color: 'var(--primary-foreground)'
                }}
              >
                {isLoading ? 'Verifying...' : 'Verify Account'}
              </button>

              {/* Back to signup button */}
              <button
                type="button"
                onClick={() => {
                  setStep("signup");
                  setOtpData({ emailOtp: '', smsOtp: '' });
                  setErrors({});
                }}
                className="w-full py-2 px-6 rounded-[12px] font-['Inter'] font-normal hover:opacity-80 transition-all duration-300 cursor-pointer border"
                style={{
                  fontSize: 'var(--font-size-sm)',
                  color: 'var(--text-secondary)',
                  borderColor: '#e5e7eb'
                }}
              >
                Back to Signup
              </button>
            </>
          )}

          {/* LOGIN FORM */}
          {step === "login" && (
            <>
              {/* Email field */}
              <div className="space-y-1.5">
                <label
                  htmlFor="email"
                  className="block font-['Inter'] font-normal"
                  style={{
                    fontSize: 'var(--font-size-sm)',
                    color: 'var(--text-secondary)'
                  }}
                >
                  Email
                </label>
                <input
                  type="email"
                  id="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  className="w-full px-4 py-2.5 rounded-[12px] border font-['Inter'] font-normal focus:outline-none focus:ring-2 transition-all duration-300"
                  style={{
                    fontSize: 'var(--font-size-sm)',
                    borderColor: errors.email ? '#ef4444' : '#e5e7eb',
                    backgroundColor: 'var(--secondary-background)',
                    color: 'var(--text-primary)'
                  }}
                  placeholder="Enter your email"
                />
                {errors.email && (
                  <p className="text-red-500 text-xs mt-1">{errors.email}</p>
                )}
              </div>

              {/* Password field */}
              <div className="space-y-1.5">
                <label
                  htmlFor="password"
                  className="block font-['Inter'] font-normal"
                  style={{
                    fontSize: 'var(--font-size-sm)',
                    color: 'var(--text-secondary)'
                  }}
                >
                  Password
                </label>
                <input
                  type="password"
                  id="password"
                  name="password"
                  value={formData.password}
                  onChange={handleChange}
                  className="w-full px-4 py-2.5 rounded-[12px] border font-['Inter'] font-normal focus:outline-none focus:ring-2 transition-all duration-300"
                  style={{
                    fontSize: 'var(--font-size-sm)',
                    borderColor: errors.password ? '#ef4444' : '#e5e7eb',
                    backgroundColor: 'var(--secondary-background)',
                    color: 'var(--text-primary)'
                  }}
                  placeholder="Enter your password"
                />
                {errors.password && (
                  <p className="text-red-500 text-xs mt-1">{errors.password}</p>
                )}
              </div>

              {/* Forgot password link */}
              <div className="text-right">
                <a
                  href="/forgot-password"
                  className="font-['Inter'] font-normal hover:opacity-70 transition-all duration-300 cursor-pointer"
                  style={{
                    fontSize: 'var(--font-size-sm)',
                    color: 'var(--text-accent)'
                  }}
                >
                  Forgot password?
                </a>
              </div>

              {/* Submit button */}
              <button
                type="submit"
                disabled={isLoading}
                className="w-full py-3 px-6 rounded-[12px] font-['Inter'] font-normal hover:opacity-80 transition-all duration-300 cursor-pointer disabled:opacity-50"
                style={{
                  fontSize: 'var(--font-size-base)',
                  lineHeight: 'var(--line-height-base)',
                  backgroundColor: 'var(--primary-background)',
                  color: 'var(--primary-foreground)'
                }}
              >
                {isLoading ? 'Signing in...' : 'Sign In'}
              </button>
            </>
          )}
        </form>

        {/* Toggle between login and signup - Only show when not on OTP step */}
        {step !== "otp" && (
          <div className="mt-6 text-center">
            <p
              className="font-['Inter'] font-normal"
              style={{
                fontSize: 'var(--font-size-sm)',
                color: 'var(--text-muted)'
              }}
            >
              {step === "signup" ? 'Already have an account?' : "Don't have an account?"}{' '}
              <button
                onClick={toggleMode}
                className="font-['Inter'] font-semibold hover:opacity-70 transition-all duration-300 cursor-pointer"
                style={{
                  fontSize: 'var(--font-size-sm)',
                  color: 'var(--text-accent)'
                }}
              >
                {step === "signup" ? 'Sign in' : 'Create one'}
              </button>
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default LoginModal;