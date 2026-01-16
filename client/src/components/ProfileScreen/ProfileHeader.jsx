import { ChevronRight, Check } from 'lucide-react';
import { useState } from 'react';

export default function ProfileHeader({ userName = 'User', profileCompletion = 80 }) {
  const [isHovered, setIsHovered] = useState(false);
  const completionColor = profileCompletion >= 50 ? '#3DB68A' : '#EF4444'; // Green if >= 50%, Red otherwise

  return (
    <div className="bg-white rounded-3xl shadow-sm p-6 md:p-8 relative overflow-hidden">
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
        <div className="flex items-center gap-4 md:gap-6">
          <div className="relative shrink-0">
            <div className="w-20 h-20 md:w-24 md:h-24 rounded-full bg-gray-300" />
            <div className="absolute bottom-0 right-0 w-8 h-8 md:w-10 md:h-10 rounded-full border-4 border-white flex items-center justify-center" style={{ backgroundColor: completionColor }}>
              <span className="text-white text-xs md:text-sm font-bold" style={{ fontFamily: "'Outfit', sans-serif" }}>{profileCompletion}%</span>
            </div>
          </div>
          <div className="flex flex-col gap-2">
            <h1 style={{ fontFamily: "'Outfit', sans-serif", fontSize: '24px', fontWeight: 'bold', color: '#0C204B' }}>
              Welcome Back, {userName}!
            </h1>
            <p style={{ fontFamily: "'Inter', sans-serif", fontSize: '14px', color: '#999999' }}>
              Your Profile is {profileCompletion}% complete. Finish it for faster claim approvals
            </p>
          </div>
        </div>
        <button 
          style={{ 
            backgroundColor: '#dbf4ff', 
            borderRadius: '12px', 
            padding: '12px 24px', 
            display: 'flex', 
            alignItems: 'center', 
            gap: '8px', 
            cursor: 'pointer', 
            border: 'none', 
            transition: 'all 0.3s ease-in-out',
            transform: isHovered ? 'scale(1.05)' : 'scale(1)',
            boxShadow: isHovered ? '0 4px 12px rgba(0, 0, 0, 0.1)' : '0 2px 4px rgba(0, 0, 0, 0.05)'
          }} 
          onMouseEnter={() => setIsHovered(true)}
          onMouseLeave={() => setIsHovered(false)}
        >
          <span style={{ fontFamily: "'Outfit', sans-serif", fontSize: '16px', fontWeight: '500', color: '#0C204B' }}>
            Complete Profile
          </span>
          <ChevronRight 
            className="w-5 h-5" 
            style={{ 
              color: '#0C204B',
              transform: isHovered ? 'translateX(4px)' : 'translateX(0)',
              transition: 'transform 0.3s'
            }} 
          />
        </button>
      </div>

      {/* Green arrow decoration - bottom left of profile section */}
      <div className="hidden lg:block absolute bottom-0 left-0 transform rotate-180 pointer-events-none">
        {/* <svg width="60" height="60" viewBox="0 0 60 60" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M10 50C15 40 25 30 40 20M40 20L35 25M40 20L40 10" stroke="#3DB68A" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" fill="none"/>
        </svg> */}
        <img src="../../public/images/img_component_1_teal_400_80x92.png" alt="arrow" style={{ width: '80px', height: 'auto' }} />
      </div>

      {/* Pink arrow decoration - top right - original position */}
      <div className="hidden lg:block absolute top-0 right-60 pointer-events-none">
        <svg width="129" height="116" viewBox="0 0 129 116" fill="none" xmlns="http://www.w3.org/2000/svg" className="opacity-60">
          <g clipPath="url(#clip0_arrow)">
            <path d="M49.7296 10.5099C52.8252 32.4413 61.9544 63.2146 83.9945 74.2609C89.1749 76.8572 109.299 79.9081 112.429 72.1396C116.4 62.2845 106.892 52.3354 97.8781 49.2727C84.9643 44.885 65.2274 47.5114 53.014 52.6159C43.2496 56.6968 35.4309 62.1649 26.5918 67.6183C22.2164 70.3179 17.692 75.4188 12.8969 77.1541C6.79819 79.3616 27.8942 80.2829 32.0406 79.1778C32.8525 78.9615 17.5996 79.7844 13.3132 82.523C11.1777 83.8872 13.1572 73.7796 13.2949 72.8086C14.2757 65.8974 13.8025 58.8062 13.2671 51.8892" stroke="#FFC0CB" strokeWidth="4.78829" strokeLinecap="round"/>
          </g>
          <defs>
            <clipPath id="clip0_arrow">
              <rect width="86.1892" height="106.3" fill="white" transform="translate(128.377 34.1976) rotate(108.766)"/>
            </clipPath>
          </defs>
        </svg>
      </div>
    </div>
  );
}
