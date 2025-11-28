import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import Navbar from '@/components/Navbar';
import Snowfall from '@/components/Snowfall';
import AdventBox from '@/components/AdventBox';

// Mock daily limit - replace with backend later
const DAILY_LIMIT = 3;

// Fixed positions for each box (percentage-based, carefully spaced to avoid overlap)
const boxPositions = [
  { top: '5%', left: '3%' },     // 1
  { top: '5%', left: '18%' },    // 2
  { top: '5%', left: '33%' },    // 3
  { top: '5%', left: '48%' },    // 4
  { top: '5%', left: '63%' },    // 5
  { top: '5%', left: '78%' },    // 6
  { top: '25%', left: '8%' },    // 7
  { top: '25%', left: '23%' },   // 8
  { top: '25%', left: '38%' },   // 9
  { top: '25%', left: '53%' },   // 10
  { top: '25%', left: '68%' },   // 11
  { top: '25%', left: '83%' },   // 12
  { top: '45%', left: '3%' },    // 13
  { top: '45%', left: '18%' },   // 14
  { top: '45%', left: '33%' },   // 15
  { top: '45%', left: '48%' },   // 16
  { top: '45%', left: '63%' },   // 17
  { top: '45%', left: '78%' },   // 18
  { top: '65%', left: '8%' },    // 19
  { top: '65%', left: '23%' },   // 20
  { top: '65%', left: '38%' },   // 21
  { top: '65%', left: '53%' },   // 22
  { top: '65%', left: '68%' },   // 23
  { top: '65%', left: '83%' },   // 24
];

// Placeholder images - these can be replaced with actual gift images
const getImageForDay = (day: number) => {
  const images = [
    'https://images.unsplash.com/photo-1512909006721-3d6018887383?w=200&h=200&fit=crop',
    'https://images.unsplash.com/photo-1513885535751-8b9238bd345a?w=200&h=200&fit=crop',
    'https://images.unsplash.com/photo-1482517967863-00e15c9b44be?w=200&h=200&fit=crop',
    'https://images.unsplash.com/photo-1543934638-bd2e138430c4?w=200&h=200&fit=crop',
    'https://images.unsplash.com/photo-1576919228236-a097c32a5cd4?w=200&h=200&fit=crop',
    'https://images.unsplash.com/photo-1544816155-12df9643f363?w=200&h=200&fit=crop',
    'https://images.unsplash.com/photo-1511895426328-dc8714191300?w=200&h=200&fit=crop',
    'https://images.unsplash.com/photo-1514923995763-768e52f5af87?w=200&h=200&fit=crop',
    'https://images.unsplash.com/photo-1545048702-79362596cdc9?w=200&h=200&fit=crop',
    'https://images.unsplash.com/photo-1482517967863-00e15c9b44be?w=200&h=200&fit=crop',
    'https://images.unsplash.com/photo-1512909006721-3d6018887383?w=200&h=200&fit=crop',
    'https://images.unsplash.com/photo-1513885535751-8b9238bd345a?w=200&h=200&fit=crop',
    'https://images.unsplash.com/photo-1543934638-bd2e138430c4?w=200&h=200&fit=crop',
    'https://images.unsplash.com/photo-1576919228236-a097c32a5cd4?w=200&h=200&fit=crop',
    'https://images.unsplash.com/photo-1544816155-12df9643f363?w=200&h=200&fit=crop',
    'https://images.unsplash.com/photo-1511895426328-dc8714191300?w=200&h=200&fit=crop',
    'https://images.unsplash.com/photo-1514923995763-768e52f5af87?w=200&h=200&fit=crop',
    'https://images.unsplash.com/photo-1545048702-79362596cdc9?w=200&h=200&fit=crop',
    'https://images.unsplash.com/photo-1482517967863-00e15c9b44be?w=200&h=200&fit=crop',
    'https://images.unsplash.com/photo-1512909006721-3d6018887383?w=200&h=200&fit=crop',
    'https://images.unsplash.com/photo-1513885535751-8b9238bd345a?w=200&h=200&fit=crop',
    'https://images.unsplash.com/photo-1543934638-bd2e138430c4?w=200&h=200&fit=crop',
    'https://images.unsplash.com/photo-1576919228236-a097c32a5cd4?w=200&h=200&fit=crop',
    'https://images.unsplash.com/photo-1544816155-12df9643f363?w=200&h=200&fit=crop',
  ];
  return images[(day - 1) % images.length];
};

const Calendar = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [openedToday, setOpenedToday] = useState(0);

  const canOpenMore = openedToday < DAILY_LIMIT;
  const remaining = DAILY_LIMIT - openedToday;

  useEffect(() => {
    if (!user) {
      navigate('/login');
    }
  }, [user, navigate]);

  const handleBoxOpen = () => {
    setOpenedToday(prev => prev + 1);
  };

  if (!user) return null;

  return (
    <div className="h-screen relative overflow-hidden flex flex-col">
      <Snowfall />
      <Navbar />
      
      {/* Header */}
      <div className="relative z-10 pt-20 pb-2 text-center flex-shrink-0">
        <h1 className="font-display text-2xl md:text-3xl font-bold text-gradient-gold">
          Your Advent Calendar
        </h1>
        <p className="text-muted-foreground mt-1 text-sm md:text-base">
          {canOpenMore ? (
            <>You can open <span className="text-christmas-gold font-semibold">{remaining}</span> more box{remaining !== 1 ? 'es' : ''} today, {user.username}! 🎁</>
          ) : (
            <>Come back tomorrow for more surprises, {user.username}! 🌟</>
          )}
        </p>
      </div>
      
      {/* Calendar Grid */}
      <div className="relative z-10 flex-1 w-full px-2 sm:px-4 md:px-8">
        {Array.from({ length: 24 }, (_, i) => i + 1).map((day) => (
          <AdventBox
            key={day}
            day={day}
            imageUrl={getImageForDay(day)}
            style={boxPositions[day - 1]}
            canOpen={canOpenMore}
            onOpen={handleBoxOpen}
          />
        ))}
      </div>
    </div>
  );
};

export default Calendar;
