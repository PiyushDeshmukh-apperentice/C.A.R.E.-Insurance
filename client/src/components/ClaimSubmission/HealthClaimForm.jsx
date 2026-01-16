import React, { useState } from 'react';
import './HealthClaimForm.css';
import ClaimTypeStep from './steps/ClaimTypeStep';
import DocumentUploadStep from './steps/DocumentUploadStep';
import ReviewStep from './steps/ReviewStep';
import SuccessStep from './steps/SuccessStep';

/**
 * HealthClaimForm Component
 * Multi-step form for submitting health insurance claims
 * 
 * Steps:
 * 1. Claim Type Selection (Cashless/Reimbursement) + Accident Confirmation
 * 2. Document Upload
 * 3. Review
 * 4. Success
 */
export default function HealthClaimForm({ onClose, onSuccess }) {
  const [currentStep, setCurrentStep] = useState(1);
  const [formData, setFormData] = useState({
    claimType: '',              // 'cashless' or 'reimbursement'
    isAccident: false,          // whether it was an accident
    policyName: '',             // policy name
    documents: {},              // uploaded files
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

      // If accident, simulate processing on frontend
      if (formData.isAccident) {
        const simulatedResult = {
          claim_id: `HEALTH_CLAIM_${Date.now()}`,
          decision: 'PENDING_REVIEW',
          confidence: 0.0,
          summary: 'Accident claim submitted for manual review',
          diagnosis: 'Manual review required',
          decision_reasons: ['Accident claims require manual verification'],
          applied_clauses: [],
          ignored_exclusions: [],
          audit_reference_id: `AUD_ACC_${Math.random().toString(36).substr(2, 6).toUpperCase()}`
        };

        setFormData(prev => ({ ...prev, claimResult: simulatedResult }));
        setCurrentStep(4); // Go to success step
        return;
      }

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
      uploadFormData.append('policy_name', formData.policyName);

      // Append documents with correct names
      const documentMapping = {
        admission_note: formData.documents.admission_note,
        prescription: formData.documents.prescription,
        imaging_report: formData.documents.imaging_report,
        pathology_report: formData.documents.pathology_report,
        discharge_summary: formData.documents.discharge_summary,
        bill: formData.documents.bill,
        insurance: formData.documents.insurance
      };

      Object.entries(documentMapping).forEach(([key, file]) => {
        if (file) {
          uploadFormData.append(key, file);
        }
      });

      // Submit to backend
      const response = await fetch('http://localhost:8000/health-claims/submit', {
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
      setCurrentStep(4); // Go to success step
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
          <ClaimTypeStep
            formData={formData}
            onNext={handleNextStep}
            onCancel={onClose}
          />
        );
      case 2:
        return (
          <DocumentUploadStep
            formData={formData}
            onNext={handleNextStep}
            onPrevious={handlePreviousStep}
            isAccident={formData.isAccident}
          />
        );
      case 3:
        return (
          <ReviewStep
            formData={formData}
            onNext={handleSubmit}
            onPrevious={handlePreviousStep}
            loading={loading}
            error={error}
          />
        );
      case 4:
        return (
          <SuccessStep
            claimResult={formData.claimResult}
            isAccident={formData.isAccident}
            onClose={onClose}
          />
        );
      default:
        return null;
    }
  };

  return (
    <div className="claim-modal-overlay">
      <div className="health-claim-form-container">
        {/* Close Button */}
        {currentStep !== 4 && (
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
            {[1, 2, 3, 4].map(step => (
              <div
                key={step}
                className={`progress-step ${step <= currentStep ? 'active' : ''} ${step === currentStep ? 'current' : ''}`}
              >
                <span className="step-number">{step}</span>
                <span className="step-label">
                  {step === 1 ? 'Claim Type' : step === 2 ? 'Documents' : step === 3 ? 'Review' : 'Success'}
                </span>
              </div>
            ))}
          </div>
          <div className="progress-fill" style={{ width: `${((currentStep - 1) / 3) * 100}%` }}></div>
        </div>

        {/* Step Content */}
        <div className="claim-step-content">
          {renderStep()}
        </div>
      </div>
    </div>
  );
}
