import React, { useState } from 'react';
import './VehicleClaimForm.css';
import VehicleTypeStep from './steps/VehicleTypeStep';
import VehicleDetailsStep from './steps/VehicleDetailsStep';
import IncidentDetailsStep from './steps/IncidentDetailsStep';
import DriverDetailsStep from './steps/DriverDetailsStep';
import ImageUploadStep from './steps/ImageUploadStep';
import VehicleReviewStep from './steps/VehicleReviewStep';
import SuccessStep from './steps/SuccessStep';

/**
 * VehicleClaimForm Component
 * Multi-step form for submitting vehicle insurance claims
 * 
 * Steps:
 * 1. Vehicle Type + Policy Name
 * 2. Vehicle Details
 * 3. Incident Details
 * 4. Driver Details
 * 5. Vehicle Image Upload
 * 6. Review
 * 7. Success
 */
export default function VehicleClaimForm({ onClose, onSuccess }) {
  const [currentStep, setCurrentStep] = useState(1);
  const [formData, setFormData] = useState({
    policyName: '',             // policy name
    vehicleType: '',            // 'car', 'bike', 'scooter', 'truck'
    vehicleImage: null,         // uploaded vehicle image
    vehicleModel: '',           // vehicle model
    vehicleNumber: '',          // vehicle registration number
    eventDate: '',              // event date
    eventTime: '',              // event time
    activity: '',               // activity type
    street: '',                 // street name
    city: '',                   // city
    state: '',                  // state
    driverName: '',             // driver name
    driverAge: '',              // driver age
    driverGender: '',           // driver gender
    licensed: false,            // is driver licensed
    experienceYears: '',        // driving experience
    underInfluence: false,      // was driver under influence
    claimResult: null           // result from backend
  });
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  // Handle step progression
  const handleNextStep = (stepData) => {
    setFormData(prev => ({ ...prev, ...stepData }));
    setError(null);
    setCurrentStep(prev => prev + 1);
  };

  const handlePreviousStep = () => {
    setCurrentStep(prev => prev - 1);
  };

  // Handle form submission
  const handleSubmit = async () => {
    try {
      setLoading(true);
      setError(null);

      // Get session token
      const session = JSON.parse(localStorage.getItem('auth'));
      console.log('Session data:', session);
      if (!session || !session.token) {
        throw new Error('Session expired. Please log in again.');
      }
      
      console.log('Using token:', session.token.substring(0, 20) + '...');
      console.log('Email:', session.userData?.email);

      // Prepare FormData for multipart upload
      const uploadFormData = new FormData();
      uploadFormData.append('email', session.userData.email);
      uploadFormData.append('event_date', formData.eventDate);
      uploadFormData.append('event_time', formData.eventTime);
      uploadFormData.append('activity', formData.activity);
      uploadFormData.append('street', formData.street);
      uploadFormData.append('city', formData.city);
      uploadFormData.append('state', formData.state);
      uploadFormData.append('driver_name', formData.driverName);
      uploadFormData.append('driver_age', parseInt(formData.driverAge));
      uploadFormData.append('driver_gender', formData.driverGender);
      uploadFormData.append('licensed', formData.licensed);
      uploadFormData.append('experience_years', parseInt(formData.experienceYears));
      uploadFormData.append('under_influence', formData.underInfluence);
      uploadFormData.append('policy_name', formData.policyName);
      uploadFormData.append('vehicle_type', formData.vehicleType);
      
      // Append vehicle image
      if (formData.vehicleImage) {
        uploadFormData.append('vehicle_image', formData.vehicleImage);
      }

      // Submit to backend
      const response = await fetch('http://localhost:8000/automobile-claims/submit', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${session.token}`
        },
        body: uploadFormData
      });

      if (!response.ok) {
        const errorData = await response.json();
        console.error('Backend error response:', errorData);
        console.error('Response status:', response.status);
        throw new Error(errorData.detail || `Failed to submit claim (${response.status})`);
      }

      const claimResult = await response.json();
      setFormData(prev => ({ ...prev, claimResult }));
      setCurrentStep(7); // Go to success step
    } catch (err) {
      setError(err.message);
      console.error('Claim submission error:', err);
    } finally {
      setLoading(false);
    }
  };

  // Render current step
  const renderStep = () => {
    switch (currentStep) {
      case 1:
        return (
          <VehicleTypeStep
            formData={formData}
            onNext={handleNextStep}
            onCancel={onClose}
          />
        );
      case 2:
        return (
          <VehicleDetailsStep
            formData={formData}
            onNext={handleNextStep}
            onPrevious={handlePreviousStep}
          />
        );
      case 3:
        return (
          <IncidentDetailsStep
            formData={formData}
            onNext={handleNextStep}
            onPrevious={handlePreviousStep}
          />
        );
      case 4:
        return (
          <DriverDetailsStep
            formData={formData}
            onNext={handleNextStep}
            onPrevious={handlePreviousStep}
          />
        );
      case 5:
        return (
          <ImageUploadStep
            formData={formData}
            onNext={handleNextStep}
            onPrevious={handlePreviousStep}
          />
        );
      case 6:
        return (
          <VehicleReviewStep
            formData={formData}
            onNext={handleSubmit}
            onPrevious={handlePreviousStep}
            loading={loading}
            error={error}
          />
        );
      case 7:
        return (
          <SuccessStep
            claimResult={formData.claimResult}
            claimType="vehicle"
            onClose={onClose}
          />
        );
      default:
        return null;
    }
  };

  return (
    <div className="claim-modal-overlay">
      <div className="vehicle-claim-form-container">
        {/* Close Button */}
        {currentStep !== 7 && (
          <button
            className="claim-modal-close"
            onClick={onClose}
            aria-label="Close form"
            style={{ position: 'absolute', top: '16px', right: '16px', zIndex: 10 }}
          >
            ✕
          </button>
        )}

        {/* Progress Bar */}
        <div className="claim-progress-bar">
          <div className="progress-steps">
            {[1, 2, 3, 4, 5, 6, 7].map(step => (
              <div
                key={step}
                className={`progress-step ${step <= currentStep ? 'active' : ''} ${step === currentStep ? 'current' : ''}`}
              >
                <span className="step-number">{step}</span>
                <span className="step-label">
                  {step === 1 ? 'Vehicle & Policy' : step === 2 ? 'Vehicle Details' : step === 3 ? 'Incident' : step === 4 ? 'Driver' : step === 5 ? 'Image' : step === 6 ? 'Review' : 'Success'}
                </span>
              </div>
            ))}
          </div>
          <div className="progress-fill" style={{ width: `${((currentStep - 1) / 6) * 100}%` }}></div>
        </div>

        {/* Step Content */}
        <div className="claim-step-content">
          {renderStep()}
        </div>
      </div>
    </div>
  );
}
