import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import ProfileNavbar from '../components/ProfileScreen/ProfileNavbar';
import ProfileHeader from '../components/ProfileScreen/ProfileHeader';
import ActivePolicies from '../components/ProfileScreen/ActivePolicies';
import ClaimStatus from '../components/ProfileScreen/ClaimStatus';
import ActionButtons from '../components/ProfileScreen/ActionButtons';
import apiService from '../services/apiService';

export default function Profile() {
  const navigate = useNavigate();
  const [userData, setUserData] = useState(null);
  const [policies, setPolicies] = useState([]);
  const [claims, setClaims] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const initializeProfile = async () => {
      try {
        // Get user session from localStorage
        const session = apiService.getSession();
        
        console.log("Session data:", session);
        
        if (!session || !session.token) {
          // No session, redirect to home
          navigate('/');
          return;
        }

        // Set user data from session
        setUserData(session.userData || session.user);

        // Log session start time if available
        if (session.sessionStartTime) {
          console.log("Session started at:", new Date(session.sessionStartTime).toLocaleString());
        }

        // Fetch user-specific policies and claims using token
        console.log("Fetching policies...");
        const policiesResponse = await apiService.getPoliciesRequest(session.token);
        console.log("Policies response:", policiesResponse);
        if (policiesResponse.success) {
          setPolicies(policiesResponse.data || []);
        }

        console.log("Fetching claims...");
        const claimsResponse = await apiService.getClaimsRequest(session.token);
        console.log("Claims response:", claimsResponse);
        if (claimsResponse.success) {
          setClaims(claimsResponse.data || []);
        }
      } catch (error) {
        console.error('Failed to load profile:', error);
      } finally {
        setLoading(false);
      }
    };

    initializeProfile();
  }, [navigate]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ backgroundColor: 'var(--bg-highlight)' }}>
        <div style={{ color: 'var(--text-primary)', fontSize: '18px' }}>Loading...</div>
      </div>
    );
  }

  if (!userData) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ backgroundColor: 'var(--bg-highlight)' }}>
        <div style={{ color: 'var(--text-primary)', fontSize: '18px' }}>Please log in to view your profile</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen" style={{ backgroundColor: 'var(--bg-highlight)' }}>
      {/* Navbar */}
      <ProfileNavbar />

      {/* Main Content */}
      <div className="py-8 px-4 md:px-8 lg:px-16">
        <div className="max-w-7xl mx-auto">
          {/* Profile Header */}
          <div className="mb-8">
            <ProfileHeader userName={userData.username} profileCompletion={userData.profileCompletion || 50} />
          </div>

          {/* Action Buttons */}
          <div className="mb-8">
            <ActionButtons />
          </div>

          {/* Active Policies */}
          <div className="mb-8">
            <ActivePolicies policies={policies} />
          </div>

          {/* Claim Status */}
          <div className="mb-8">
            <ClaimStatus claims={claims} />
          </div>
        </div>
      </div>
    </div>
  );
}
