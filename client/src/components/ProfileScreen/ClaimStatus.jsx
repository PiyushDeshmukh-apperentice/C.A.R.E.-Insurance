import { Check, AlertCircle } from 'lucide-react';

function StatusStep({ label, sublabel, isCompleted, isLast }) {
  return (
    <div className="flex flex-col items-center relative flex-1" style={{ paddingTop: '60px' }}>
      {/* Status icon with elevation and glow */}
      <div 
        className="rounded-full flex items-center justify-center shrink-0 absolute"
        style={{ 
          backgroundColor: isCompleted ? '#3DB68A' : '#999999', 
          zIndex: 5,
          width: '64px',
          height: '64px',
          top: '0',
          left: '50%',
          transform: 'translateX(-50%)',
          boxShadow: isCompleted 
            ? '0 4px 15px rgba(61, 182, 138, 0.4), 0 8px 25px rgba(61, 182, 138, 0.2)' 
            : '0 4px 15px rgba(153, 153, 153, 0.3), 0 8px 25px rgba(153, 153, 153, 0.15)'
        }}
      >
        {isCompleted ? (
          <Check className="w-8 h-8 md:w-10 md:h-10 text-white" strokeWidth={3} />
        ) : (
          <AlertCircle className="w-8 h-8 md:w-10 md:h-10 text-white" strokeWidth={3} />
        )}
      </div>
      
      {/* Labels - shifted down */}
      <div className="text-center pt-8" style={{ fontFamily: "'Outfit', sans-serif" }}>
        <p style={{ fontWeight: 'bold', fontSize: '14px', marginBottom: '4px', color: '#0C204B', fontFamily: "'Outfit', sans-serif" }}>
          {label}
        </p>
        {sublabel && (
          <p style={{ fontSize: '12px', color: '#999999', fontFamily: "'Outfit', sans-serif" }}>
            {sublabel}
          </p>
        )}
      </div>
    </div>
  );
}

export default function ClaimStatus({ claims = [] }) {
  // Get the most recent claim
  const mostRecentClaim = claims.length > 0 ? claims[0] : null;
  
  // Map claim statuses to timeline steps
  const getStatusSteps = () => {
    if (!mostRecentClaim) {
      return [
        { label: 'Submitted', sublabel: 'Date', isCompleted: false },
        { label: 'Under Review', sublabel: 'Expected Completion Date', isCompleted: false },
        { label: 'Decision Pending', sublabel: '', isCompleted: false }
      ];
    }

    const statusMap = {
      'submitted': 0,
      'under_review': 1,
      'pending': 2,
      'approved': 3,
      'rejected': 3
    };

    const currentStatus = statusMap[mostRecentClaim.status] || 0;

    return [
      { label: 'Submitted', sublabel: 'Claim filed', isCompleted: currentStatus >= 0 },
      { label: 'Under Review', sublabel: 'In progress', isCompleted: currentStatus >= 1 },
      { label: 'Decision Pending', sublabel: 'Awaiting decision', isCompleted: currentStatus >= 2 }
    ];
  };

  const statusSteps = getStatusSteps();

  return (
    <div className="bg-white rounded-3xl shadow-sm p-6 md:p-8">
      <h2 style={{ fontFamily: "'Outfit', sans-serif", fontWeight: 'bold', fontSize: '20px', color: '#0C204B', marginBottom: '32px' }}>
        Active claim status: {mostRecentClaim ? `#${mostRecentClaim.claimNumber}` : 'No claims'}
      </h2>
      
      {mostRecentClaim ? (
        <div className="relative">
          {/* Horizontal line - positioned at center of circles */}
          <div 
            className="absolute left-0 right-0"
            style={{ 
              backgroundColor: '#D3D3D3',
              height: '1px',
              top: '32px',
              zIndex: 0
            }}
          />
          
          <div className="flex justify-between gap-0 relative z-10">
            {statusSteps.map((step, index) => (
              <StatusStep
                key={index}
                label={step.label}
                sublabel={step.sublabel}
                isCompleted={step.isCompleted}
                isLast={index === statusSteps.length - 1}
              />
            ))}
          </div>
        </div>
      ) : (
        <div style={{ 
          padding: '24px', 
          textAlign: 'center', 
          color: '#999999',
          fontFamily: "'Inter', sans-serif"
        }}>
          No active claims
        </div>
      )}
    </div>
  );
}
