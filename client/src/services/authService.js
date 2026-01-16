/**
 * Authentication Service
 * This is a JSON-based service layer that can be easily swapped with a real backend API
 * To integrate with backend: Replace fetch calls with actual API endpoints
 */

import usersData from '../data/users.json';
import otpsData from '../data/otps.json';

// Simulating a database with in-memory storage
let users = [...usersData.users];
let emailOtps = [...otpsData.emailOtps];
let phoneOtps = [...otpsData.phoneOtps];

/**
 * Generate a random 6-digit OTP
 */
const generateOTP = () => {
  return Math.floor(100000 + Math.random() * 900000).toString();
};

/**
 * Send OTP to email (simulated)
 * To integrate with backend: Call actual email service API
 */
export const sendEmailOTP = async (email) => {
  try {
    // Check if OTP already sent and not expired
    const existingOTP = emailOtps.find(o => o.email === email);
    
    if (existingOTP && new Date(existingOTP.expiresAt) > new Date()) {
      throw new Error('OTP already sent. Please wait before requesting a new one.');
    }

    const otp = generateOTP();
    const now = new Date();
    const expiryTime = new Date(now.getTime() + 10 * 60000); // 10 minutes

    const newOTP = {
      id: `email_otp_${Date.now()}`,
      email,
      otp,
      type: 'email',
      createdAt: now.toISOString(),
      expiresAt: expiryTime.toISOString(),
      verified: false
    };

    // Remove old OTPs for this email
    emailOtps = emailOtps.filter(o => o.email !== email);
    // Add new OTP
    emailOtps.push(newOTP);

    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 500));

    // In production, send actual email here
    console.log(`Email OTP sent to ${email}: ${otp}`);

    return {
      success: true,
      message: `OTP sent to ${email}`,
      data: { email }
    };
  } catch (error) {
    return {
      success: false,
      message: error.message || 'Failed to send OTP',
      data: null
    };
  }
};

/**
 * Send OTP to phone (simulated)
 * To integrate with backend: Call actual SMS service API
 */
export const sendPhoneOTP = async (phone) => {
  try {
    // Check if OTP already sent and not expired
    const existingOTP = phoneOtps.find(o => o.phone === phone);
    
    if (existingOTP && new Date(existingOTP.expiresAt) > new Date()) {
      throw new Error('OTP already sent. Please wait before requesting a new one.');
    }

    const otp = generateOTP();
    const now = new Date();
    const expiryTime = new Date(now.getTime() + 10 * 60000); // 10 minutes

    const newOTP = {
      id: `phone_otp_${Date.now()}`,
      phone,
      otp,
      type: 'phone',
      createdAt: now.toISOString(),
      expiresAt: expiryTime.toISOString(),
      verified: false
    };

    // Remove old OTPs for this phone
    phoneOtps = phoneOtps.filter(o => o.phone !== phone);
    // Add new OTP
    phoneOtps.push(newOTP);

    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 500));

    // In production, send actual SMS here
    console.log(`Phone OTP sent to ${phone}: ${otp}`);

    return {
      success: true,
      message: `OTP sent to ${phone}`,
      data: { phone }
    };
  } catch (error) {
    return {
      success: false,
      message: error.message || 'Failed to send OTP',
      data: null
    };
  }
};

/**
 * Verify Email OTP
 * To integrate with backend: Call actual OTP verification API
 */
export const verifyEmailOTP = async (email, otp) => {
  try {
    const otpRecord = emailOtps.find(o => o.email === email);

    if (!otpRecord) {
      throw new Error('OTP not found. Please request a new OTP.');
    }

    if (new Date(otpRecord.expiresAt) < new Date()) {
      throw new Error('OTP has expired. Please request a new one.');
    }

    if (otpRecord.otp !== otp) {
      throw new Error('Invalid OTP. Please try again.');
    }

    // Mark as verified
    otpRecord.verified = true;

    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 500));

    return {
      success: true,
      message: 'Email verified successfully',
      data: { email }
    };
  } catch (error) {
    return {
      success: false,
      message: error.message || 'Failed to verify email OTP',
      data: null
    };
  }
};

/**
 * Verify Phone OTP
 * To integrate with backend: Call actual OTP verification API
 */
export const verifyPhoneOTP = async (phone, otp) => {
  try {
    const otpRecord = phoneOtps.find(o => o.phone === phone);

    if (!otpRecord) {
      throw new Error('OTP not found. Please request a new OTP.');
    }

    if (new Date(otpRecord.expiresAt) < new Date()) {
      throw new Error('OTP has expired. Please request a new one.');
    }

    if (otpRecord.otp !== otp) {
      throw new Error('Invalid OTP. Please try again.');
    }

    // Mark as verified
    otpRecord.verified = true;

    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 500));

    return {
      success: true,
      message: 'Phone verified successfully',
      data: { phone }
    };
  } catch (error) {
    return {
      success: false,
      message: error.message || 'Failed to verify phone OTP',
      data: null
    };
  }
};

/**
 * Register new user
 * To integrate with backend: Call actual registration API
 */
export const registerUser = async (email, password, name, phone) => {
  try {
    // Check if user already exists
    if (users.some(u => u.email === email)) {
      throw new Error('User already exists with this email');
    }

    // Check if both email and phone were verified
    const emailOtpRecord = emailOtps.find(o => o.email === email);
    const phoneOtpRecord = phoneOtps.find(o => o.phone === phone);

    if (!emailOtpRecord || !emailOtpRecord.verified) {
      throw new Error('Please verify email first');
    }

    if (!phoneOtpRecord || !phoneOtpRecord.verified) {
      throw new Error('Please verify phone number first');
    }

    const newUser = {
      id: `user_${Date.now()}`,
      email,
      password,
      name,
      phone,
      profileCompletion: 50,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };

    users.push(newUser);

    // Remove OTPs after successful registration
    emailOtps = emailOtps.filter(o => o.email !== email);
    phoneOtps = phoneOtps.filter(o => o.phone !== phone);

    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 500));

    return {
      success: true,
      message: 'User registered successfully',
      data: { userId: newUser.id, email: newUser.email }
    };
  } catch (error) {
    return {
      success: false,
      message: error.message || 'Registration failed',
      data: null
    };
  }
};

/**
 * Login user
 * To integrate with backend: Call actual login API
 */
export const loginUser = async (email, password) => {
  try {
    const user = users.find(u => u.email === email);

    if (!user) {
      throw new Error('User not found');
    }

    if (user.password !== password) {
      throw new Error('Invalid password');
    }

    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 500));

    return {
      success: true,
      message: 'Logged in successfully',
      data: {
        userId: user.id,
        email: user.email,
        name: user.name,
        phone: user.phone,
        profileCompletion: user.profileCompletion
      }
    };
  } catch (error) {
    return {
      success: false,
      message: error.message || 'Login failed',
      data: null
    };
  }
};

/**
 * Get user by ID
 * To integrate with backend: Call actual user fetch API
 */
export const getUserById = async (userId) => {
  try {
    const user = users.find(u => u.id === userId);

    if (!user) {
      throw new Error('User not found');
    }

    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 300));

    return {
      success: true,
      data: user
    };
  } catch (error) {
    return {
      success: false,
      message: error.message || 'Failed to fetch user',
      data: null
    };
  }
};

/**
 * Update user profile
 * To integrate with backend: Call actual update API
 */
export const updateUserProfile = async (userId, updates) => {
  try {
    const user = users.find(u => u.id === userId);

    if (!user) {
      throw new Error('User not found');
    }

    Object.assign(user, updates, { updatedAt: new Date().toISOString() });

    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 500));

    return {
      success: true,
      message: 'Profile updated successfully',
      data: user
    };
  } catch (error) {
    return {
      success: false,
      message: error.message || 'Failed to update profile',
      data: null
    };
  }
};

export default {
  sendEmailOTP,
  sendPhoneOTP,
  verifyEmailOTP,
  verifyPhoneOTP,
  registerUser,
  loginUser,
  getUserById,
  updateUserProfile
};
