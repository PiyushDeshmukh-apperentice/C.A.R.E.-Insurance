/**
 * Data Service
 * Handles retrieval of policies, claims, and other user data
 * To integrate with backend: Replace with actual API calls
 */

import policiesData from '../data/policies.json';

// Simulating a database with in-memory storage
let policies = [...policiesData.policies];
let claims = [...policiesData.claims];

/**
 * Get all policies for a user
 * To integrate with backend: Call actual policies API
 */
export const getUserPolicies = async (userId) => {
  try {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 300));

    const userPolicies = policies.filter(p => p.userId === userId);

    return {
      success: true,
      data: userPolicies
    };
  } catch (error) {
    return {
      success: false,
      message: error.message || 'Failed to fetch policies',
      data: []
    };
  }
};

/**
 * Get all claims for a user
 * To integrate with backend: Call actual claims API
 */
export const getUserClaims = async (userId) => {
  try {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 300));

    const userClaims = claims.filter(c => c.userId === userId);
    
    // Sort by created date (newest first)
    return {
      success: true,
      data: userClaims.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt))
    };
  } catch (error) {
    return {
      success: false,
      message: error.message || 'Failed to fetch claims',
      data: []
    };
  }
};

/**
 * Get single policy details
 * To integrate with backend: Call actual policy detail API
 */
export const getPolicyById = async (policyId) => {
  try {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 300));

    const policy = policies.find(p => p.id === policyId);

    if (!policy) {
      throw new Error('Policy not found');
    }

    return {
      success: true,
      data: policy
    };
  } catch (error) {
    return {
      success: false,
      message: error.message || 'Failed to fetch policy',
      data: null
    };
  }
};

/**
 * Get single claim details
 * To integrate with backend: Call actual claim detail API
 */
export const getClaimById = async (claimId) => {
  try {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 300));

    const claim = claims.find(c => c.id === claimId);

    if (!claim) {
      throw new Error('Claim not found');
    }

    return {
      success: true,
      data: claim
    };
  } catch (error) {
    return {
      success: false,
      message: error.message || 'Failed to fetch claim',
      data: null
    };
  }
};

/**
 * File a new claim
 * To integrate with backend: Call actual claim creation API
 */
export const fileNewClaim = async (userId, policyId, amount, description) => {
  try {
    // Verify policy exists and belongs to user
    const policy = policies.find(p => p.id === policyId && p.userId === userId);
    if (!policy) {
      throw new Error('Policy not found or does not belong to user');
    }

    const newClaim = {
      id: `claim_${Date.now()}`,
      userId,
      policyId,
      claimNumber: `CLM${Date.now().toString().slice(-8)}`,
      status: 'submitted',
      amount,
      description,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };

    claims.push(newClaim);

    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 500));

    return {
      success: true,
      message: 'Claim filed successfully',
      data: newClaim
    };
  } catch (error) {
    return {
      success: false,
      message: error.message || 'Failed to file claim',
      data: null
    };
  }
};

/**
 * Upload documents for a claim
 * To integrate with backend: Call actual file upload API
 */
export const uploadClaimDocuments = async (claimId, documents) => {
  try {
    const claim = claims.find(c => c.id === claimId);

    if (!claim) {
      throw new Error('Claim not found');
    }

    // Simulate document upload and API delay
    await new Promise(resolve => setTimeout(resolve, 1000));

    // Update claim with documents
    claim.documents = documents;
    claim.updatedAt = new Date().toISOString();

    return {
      success: true,
      message: 'Documents uploaded successfully',
      data: claim
    };
  } catch (error) {
    return {
      success: false,
      message: error.message || 'Failed to upload documents',
      data: null
    };
  }
};

/**
 * Get claim status history (timeline)
 * To integrate with backend: Call actual timeline API
 */
export const getClaimStatusTimeline = async (claimId) => {
  try {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 300));

    const claim = claims.find(c => c.id === claimId);

    if (!claim) {
      throw new Error('Claim not found');
    }

    // Simulate timeline data based on claim status
    const timeline = [];

    // All claims start as submitted
    timeline.push({
      status: 'submitted',
      timestamp: claim.createdAt,
      completed: true
    });

    if (['under_review', 'approved', 'rejected', 'pending'].includes(claim.status)) {
      timeline.push({
        status: 'under_review',
        timestamp: new Date(new Date(claim.createdAt).getTime() + 24 * 60 * 60 * 1000).toISOString(),
        completed: ['approved', 'rejected'].includes(claim.status)
      });
    }

    if (['pending'].includes(claim.status)) {
      timeline.push({
        status: 'decision_pending',
        timestamp: new Date(new Date(claim.createdAt).getTime() + 48 * 60 * 60 * 1000).toISOString(),
        completed: false
      });
    }

    return {
      success: true,
      data: timeline
    };
  } catch (error) {
    return {
      success: false,
      message: error.message || 'Failed to fetch timeline',
      data: []
    };
  }
};

export default {
  getUserPolicies,
  getUserClaims,
  getPolicyById,
  getClaimById,
  fileNewClaim,
  uploadClaimDocuments,
  getClaimStatusTimeline
};
