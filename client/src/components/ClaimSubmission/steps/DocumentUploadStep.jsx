import React, { useState } from 'react';
import '../styles/StepStyles.css';
import '../styles/DocumentUpload.css';

/**
 * DocumentUploadStep - Step 2
 * Upload required documents for health claim
 */
export default function DocumentUploadStep({
  formData,
  onNext,
  onPrevious,
  isAccident
}) {
  const [documents, setDocuments] = useState(formData.documents || {});
  const [error, setError] = useState('');
  const [uploadProgress, setUploadProgress] = useState({});

  // List of required documents (without FIR for non-accident claims)
  const requiredDocuments = [
    {
      key: 'admission_note',
      label: 'Admission Note',
      description: 'Hospital admission document',
      icon: '📋'
    },
    {
      key: 'prescription',
      label: 'Prescription',
      description: 'Medical prescription document',
      icon: '💊'
    },
    {
      key: 'imaging_report',
      label: 'Imaging Report',
      description: 'X-ray, CT Scan, or MRI report',
      icon: '🖼️'
    },
    {
      key: 'pathology_report',
      label: 'Pathology Report',
      description: 'Lab test or pathology report',
      icon: '🔬'
    },
    {
      key: 'discharge_summary',
      label: 'Discharge Summary',
      description: 'Hospital discharge document',
      icon: '📄'
    },
    {
      key: 'bill',
      label: 'Hospital Bill',
      description: 'Itemized hospital bill',
      icon: '🧾'
    },
    {
      key: 'insurance',
      label: 'Insurance Card',
      description: 'Copy of insurance policy card',
      icon: '🎫'
    }
  ];

  // Add FIR if accident
  const accidentDocuments = isAccident ? [
    {
      key: 'fir_receipt',
      label: 'FIR Receipt',
      description: 'Police FIR receipt (will not be sent to backend)',
      icon: '🚨',
      required: true
    }
  ] : [];

  const allDocuments = [...requiredDocuments, ...accidentDocuments];

  const handleFileSelect = (documentKey, file) => {
    if (file) {
      // Validate file type (must be PDF)
      if (!file.type.includes('pdf')) {
        setError(`${documentKey}: Please upload a PDF file`);
        setTimeout(() => setError(''), 5000);
        return;
      }

      // Validate file size (max 10MB)
      const maxSize = 10 * 1024 * 1024; // 10MB
      if (file.size > maxSize) {
        setError(`${documentKey}: File size must be less than 10MB`);
        setTimeout(() => setError(''), 5000);
        return;
      }

      setDocuments(prev => ({
        ...prev,
        [documentKey]: file
      }));

      setUploadProgress(prev => ({
        ...prev,
        [documentKey]: 100
      }));
    }
  };

  const handleNext = () => {
    // Validate all required documents (except FIR for accident)
    const requiredKeys = requiredDocuments.map(doc => doc.key);
    const missingDocs = requiredKeys.filter(key => !documents[key]);

    if (missingDocs.length > 0) {
      setError(`Please upload the following documents: ${missingDocs.join(', ')}`);
      return;
    }

    // For accident claims, validate FIR receipt
    if (isAccident && !documents.fir_receipt) {
      setError('Please upload the FIR receipt for accident claims');
      return;
    }

    // Filter out FIR receipt before sending (only send required documents)
    const docsToSend = { ...documents };
    delete docsToSend.fir_receipt;

    onNext({
      documents: docsToSend
    });
  };

  return (
    <div className="step-container">
      <div className="step-header">
        <h2 className="step-title">Upload Documents</h2>
        <p className="step-description">
          Upload all required documents in PDF format (Max 10MB each)
          {isAccident && ' + FIR receipt for accident verification'}
        </p>
      </div>

      <div className="step-content">
        {/* Error Message */}
        {error && (
          <div className="alert alert-error">
            {/* <span className="alert-icon">❌</span> */}
            <span className="alert-text">{error}</span>
          </div>
        )}

        {/* Required Documents Section */}
        <div className="form-section">
          <label className="form-section-title">Required Documents</label>
          <div className="documents-grid">
            {requiredDocuments.map(doc => (
              <DocumentUploadCard
                key={doc.key}
                document={doc}
                uploadedFile={documents[doc.key]}
                progress={uploadProgress[doc.key]}
                onFileSelect={(file) => handleFileSelect(doc.key, file)}
              />
            ))}
          </div>
        </div>

        {/* Accident Documents Section */}
        {isAccident && (
          <div className="form-section">
            <label className="form-section-title">
              Accident Verification Documents
            </label>
            
            <div className="documents-grid">
              {accidentDocuments.map(doc => (
                <DocumentUploadCard
                  key={doc.key}
                  document={doc}
                  uploadedFile={documents[doc.key]}
                  progress={uploadProgress[doc.key]}
                  onFileSelect={(file) => handleFileSelect(doc.key, file)}
                />
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Step Footer */}
      <div className="step-footer">
        <button className="btn btn-secondary" onClick={onPrevious}>
          ← Previous
        </button>
        <button
          className="btn btn-primary"
          onClick={handleNext}
        >
          Review Claim
          <span className="btn-icon">→</span>
        </button>
      </div>
    </div>
  );
}

/**
 * DocumentUploadCard Component
 * Individual document upload card
 */
function DocumentUploadCard({ document, uploadedFile, progress, onFileSelect }) {
  const fileInputRef = React.useRef(null);

  return (
    <div className="document-upload-card">
      <div className="document-header">
        <span className="document-icon">{document.icon}</span>
        <div className="document-info">
          <h3 className="document-label">{document.label}</h3>
          <p className="document-desc">{document.description}</p>
        </div>
      </div>

      {uploadedFile ? (
        <div className="document-uploaded">
          <span className="check-icon">✓</span>
          <p className="uploaded-filename">{uploadedFile.name}</p>
          <p className="uploaded-size">{(uploadedFile.size / 1024 / 1024).toFixed(2)} MB</p>
          <button
            className="btn-replace"
            onClick={() => fileInputRef.current?.click()}
          >
            Replace
          </button>
        </div>
      ) : (
        <div
          className="document-upload-area"
          onClick={() => fileInputRef.current?.click()}
          onDragOver={(e) => e.preventDefault()}
          onDrop={(e) => {
            e.preventDefault();
            if (e.dataTransfer.files[0]) {
              onFileSelect(e.dataTransfer.files[0]);
            }
          }}
        >
          <span className="upload-icon">📤</span>
          <p className="upload-text">Click or drag to upload PDF</p>
          <p className="upload-hint">Max 10MB</p>
        </div>
      )}

      <input
        ref={fileInputRef}
        type="file"
        accept=".pdf"
        hidden
        onChange={(e) => onFileSelect(e.target.files?.[0])}
      />
    </div>
  );
}
