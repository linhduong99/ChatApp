import { useRef, useState, useEffect } from 'react';
import { Room, User } from '@/lib/api';

interface ChatSidebarProps {
  rooms: Room[];
  selectedRoom: Room | null;
  currentUser: User | null;
  createdRoomIds: number[];
  onRoomSelect: (room: Room) => void;
  onCreateRoomClick: () => void;
  onLogout: () => void;
}

export function ChatSidebar({
  rooms,
  selectedRoom,
  currentUser,
  createdRoomIds,
  onRoomSelect,
  onCreateRoomClick,
  onLogout
}: ChatSidebarProps) {
  const [showUserMenu, setShowUserMenu] = useState(false);
  const userMenuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (userMenuRef.current && !userMenuRef.current.contains(event.target as Node)) {
        setShowUserMenu(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  return (
    <div className="w-64 bg-gray-800 text-white p-4 flex flex-col">
      <div className="mb-4">
        <button
          onClick={onCreateRoomClick}
          className="w-full bg-blue-500 text-white py-2 px-4 rounded hover:bg-blue-600"
        >
          Create Room
        </button>
      </div>

      {/* Room List */}
      <div className="flex-1 space-y-2 overflow-y-auto">
        {rooms.map((room) => (
          <div
            key={room.id}
            className={`p-2 rounded cursor-pointer ${
              selectedRoom?.id === room.id ? 'bg-gray-700' : 'hover:bg-gray-700'
            }`}
            onClick={() => onRoomSelect(room)}
          >
            {room.name}
            {room.has_password && !createdRoomIds.includes(room.id) && (
              <span className="ml-2 text-yellow-500">🔒</span>
            )}
          </div>
        ))}
      </div>

      {/* User Menu in Sidebar */}
      <div className="mt-auto pt-4 border-t border-gray-700">
        <div className="relative" ref={userMenuRef}>
          <button
            onClick={() => setShowUserMenu(!showUserMenu)}
            className="w-full flex items-center space-x-3 p-2 rounded hover:bg-gray-700"
          >
            <div className="w-10 h-10 rounded-full bg-blue-500 flex items-center justify-center">
              {currentUser?.username?.[0]?.toUpperCase() || '?'}
            </div>
            <div className="flex-1 text-left">
              <div className="font-medium">{currentUser?.username}</div>
              <div className="text-sm text-gray-400">Online</div>
            </div>
            <span className="text-gray-400">▼</span>
          </button>
          {showUserMenu && (
            <div className="absolute bottom-full left-0 mb-2 w-full bg-gray-700 rounded shadow-lg">
              <button
                onClick={onLogout}
                className="w-full flex items-center space-x-2 px-4 py-3 text-left hover:bg-gray-600 text-white"
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M3 3a1 1 0 0 0-1 1v12a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1V4a1 1 0 0 0-1-1H3zm11.707 4.707a1 1 0 0 0-1.414-1.414L10 9.586 6.707 6.293a1 1 0 0 0-1.414 1.414L8.586 11l-3.293 3.293a1 1 0 1 0 1.414 1.414L10 12.414l3.293 3.293a1 1 0 0 0 1.414-1.414L11.414 11l3.293-3.293z" clipRule="evenodd" />
                </svg>
                <span>Logout</span>
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
} 