import { useState } from 'react';
import ClaimTypeSelector from '../ClaimSubmission/ClaimTypeSelector';
import HealthClaimForm from '../ClaimSubmission/HealthClaimForm';
import VehicleClaimForm from '../ClaimSubmission/VehicleClaimForm';

export default function ActionButtons() {
  const [isFileHovered, setIsFileHovered] = useState(false);
  const [isUploadHovered, setIsUploadHovered] = useState(false);
  const [showClaimModal, setShowClaimModal] = useState(false);
  const [selectedClaimType, setSelectedClaimType] = useState(null);

  const handleClaimTypeSelect = (claimType) => {
    setSelectedClaimType(claimType);
  };

  const handleCloseClaimForm = () => {
    setShowClaimModal(false);
    setSelectedClaimType(null);
  };

  return (
    <>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 md:gap-6">
        {/* File a New Claim Button */}
        <button 
          className="rounded-2xl px-8 py-4" 
          style={{ 
            backgroundColor: '#0C204B',
            cursor: 'pointer',
            transition: 'all 0.3s ease-in-out',
            transform: isFileHovered ? 'scale(1.05)' : 'scale(1)',
            boxShadow: isFileHovered ? '0 4px 12px rgba(12, 32, 75, 0.3)' : '0 2px 4px rgba(0, 0, 0, 0.1)'
          }}
          onMouseEnter={() => setIsFileHovered(true)}
          onMouseLeave={() => setIsFileHovered(false)}
          onClick={() => setShowClaimModal(true)}
        >
          <span className="text-lg md:text-xl text-white font-bold" style={{ fontFamily: "'Outfit', sans-serif" }}>
            + File a New Claim
          </span>
        </button>
        
        {/* Upload Documents Button */}
        <button 
          className="border-2 rounded-2xl px-8 py-4" 
          style={{ 
            borderColor: '#0C204B',
            backgroundColor: 'white',
            cursor: 'pointer',
            transition: 'all 0.3s ease-in-out',
            transform: isUploadHovered ? 'scale(1.05)' : 'scale(1)',
            boxShadow: isUploadHovered ? '0 4px 12px rgba(12, 32, 75, 0.3)' : '0 2px 4px rgba(0, 0, 0, 0.05)'
          }}
          onMouseEnter={() => setIsUploadHovered(true)}
          onMouseLeave={() => setIsUploadHovered(false)}
        >
          <span className="text-lg md:text-xl font-bold" style={{ 
            fontFamily: "'Outfit', sans-serif", 
            color: '#0C204B',
            transition: 'color 0.3s ease-in-out'
          }}>
            View Claim History
          </span>
        </button>
      </div>

      {/* Claim Type Selector Modal */}
      <ClaimTypeSelector 
        isOpen={showClaimModal}
        onClose={() => setShowClaimModal(false)}
        onSelect={handleClaimTypeSelect}
      />

      {/* Health Claim Form - shown after selecting health claim */}
      {selectedClaimType === 'health' && (
        <HealthClaimForm onClose={handleCloseClaimForm} />
      )}

      {/* Vehicle Claim Form - shown after selecting vehicle claim */}
      {selectedClaimType === 'vehicle' && (
        <VehicleClaimForm onClose={handleCloseClaimForm} />
      )}
    </>
  );
}
