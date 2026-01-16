export default function PolicyCard({ 
  title, 
  policyNumber, 
  validity, 
  isActive = false,
  variant = 'green' 
}) {
  const bgColor = variant === 'green' ? '#E8F8F3' : '#FFF4EB';
  
  return (
    <div style={{ 
      backgroundColor: bgColor, 
      borderRadius: '24px', 
      padding: '24px', 
      boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
      position: 'relative',
      overflow: 'hidden',
      minHeight: '200px',
      display: 'flex',
      flexDirection: 'column'
    }}>
      {/* Background decoration */}
      <div style={{ position: 'absolute', left: '-176px', top: '-96px', width: '502px', height: '245px', pointerEvents: 'none' }}>
        <svg width="502" height="245" viewBox="0 0 502 245" fill="none" xmlns="http://www.w3.org/2000/svg">
          <ellipse cx="251" cy="122.5" rx="251" ry="122.5" fill={variant === 'green' ? '#3DB68A' : '#F99853'} fillOpacity="0.22"/>
        </svg>
      </div>
      
      {/* Header with title and badge */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '8px', marginBottom: '16px', position: 'relative', zIndex: 1 }}>
        <h3 style={{ fontFamily: "'Outfit', sans-serif", fontSize: '18px', fontWeight: 'bold', color: '#0C204B', margin: 0 }}>
          {title}
        </h3>
        {isActive && (
          <div style={{ 
            backgroundColor: '#3DB68A', 
            borderRadius: '20px', 
            paddingLeft: '12px', 
            paddingRight: '12px', 
            paddingTop: '4px', 
            paddingBottom: '4px',
            flexShrink: 0,
            minWidth: 'fit-content'
          }}>
            <span style={{ fontFamily: "'Outfit', sans-serif", fontSize: '12px', fontWeight: 'bold', color: 'white', margin: 0 }}>
              Active
            </span>
          </div>
        )}
      </div>

      {/* Content area with icon and policy info */}
      <div style={{ display: 'flex', gap: '16px', flex: 1, alignItems: 'center', position: 'relative', zIndex: 1 }}>
        {/* Icon placeholder */}
        <div style={{ width: '64px', height: '64px', borderRadius: '16px', backgroundColor: 'rgba(255, 255, 255, 0.3)', flexShrink: 0 }} />
        
        {/* Policy info - centered in middle area */}
        <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
          <p style={{ fontFamily: "'Outfit', sans-serif", fontSize: '12px', color: '#999999', margin: '0 0 4px 0' }}>
            Policy Number
          </p>
          <p style={{ fontFamily: "'Outfit', sans-serif", fontSize: '16px', fontWeight: 'bold', color: '#0C204B', margin: 0 }}>
            {policyNumber}
          </p>
        </div>
      </div>

      {/* Validity date at bottom right */}
      {validity && (
        <p style={{ fontFamily: "'Outfit', sans-serif", fontSize: '12px', color: '#999999', margin: 0, textAlign: 'right', position: 'absolute', bottom: '24px', right: '24px', zIndex: 1 }}>
          Validity: {validity}
        </p>
      )}
    </div>
  );
}
