'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Room, User, getRooms, getCurrentUser, logout } from '@/lib/api';
import { useRooms } from '@/hooks/useRooms';
import { useChat } from '@/hooks/useChat';
import { ChatSidebar } from '@/components/ChatSidebar';
import { ChatArea } from '@/components/ChatArea';
import { CreateRoomDialog } from '@/components/CreateRoomDialog';
import { PasswordDialog } from '@/components/PasswordDialog';

export default function ChatPage() {
  const router = useRouter();
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [showCreateRoomDialog, setShowCreateRoomDialog] = useState(false);
  const [showPasswordDialog, setShowPasswordDialog] = useState(false);
  const [passwordRoom, setPasswordRoom] = useState<Room | null>(null);
  const [error, setError] = useState<string | null>(null);

  const {
    rooms,
    selectedRoom,
    createdRoomIds,
    handleRoomSelect,
    handleCreateRoom,
    handleJoinRoom,
    updateRooms
  } = useRooms();

  const {
    messages,
    isConnected,
    newMessage,
    setNewMessage,
    sendMessage
  } = useChat({ room: selectedRoom, onError: setError });

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [roomsResponse, userResponse] = await Promise.all([
          getRooms(),
          getCurrentUser()
        ]);

        if (roomsResponse.success) {
          updateRooms(roomsResponse.data);
        }

        if (userResponse.success) {
          setCurrentUser(userResponse.data);
        } else {
          router.push('/auth/login');
        }
      } catch (error) {
        console.error('Error fetching data:', error);
        router.push('/auth/login');
      }
    };

    fetchData();
  }, []);

  const handleLogout = async () => {
    try {
      await logout();
      router.push('/auth/login');
    } catch (error) {
      console.error('Error logging out:', error);
    }
  };

  const handleRoomSelectWithPassword = (room: Room) => {
    if (room.has_password && !createdRoomIds.includes(room.id)) {
      setPasswordRoom(room);
      setShowPasswordDialog(true);
    } else {
      handleRoomSelect(room);
    }
  };

  const handleCreateRoomSubmit = async (name: string, password?: string): Promise<boolean> => {
    const success = await handleCreateRoom(name, password);
    if (success) {
      setShowCreateRoomDialog(false);
    }
    return success;
  };

  const handlePasswordSubmit = async (room: Room, password: string): Promise<boolean> => {
    const success = await handleJoinRoom(room, password);
    if (success) {
      setShowPasswordDialog(false);
      setPasswordRoom(null);
      handleRoomSelect(room);
    }
    return success;
  };

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (newMessage.trim()) {
      await sendMessage(newMessage);
    }
  };

  return (
    <div className="flex h-screen bg-gray-100">
      <ChatSidebar
        rooms={rooms}
        selectedRoom={selectedRoom}
        currentUser={currentUser}
        createdRoomIds={createdRoomIds}
        onRoomSelect={handleRoomSelectWithPassword}
        onCreateRoomClick={() => setShowCreateRoomDialog(true)}
        onLogout={handleLogout}
      />

      <div className="flex-1 flex flex-col">
        <ChatArea
          room={selectedRoom}
          messages={messages}
          currentUser={currentUser}
          newMessage={newMessage}
          onNewMessageChange={setNewMessage}
          onSendMessage={handleSendMessage}
        />
      </div>

      <CreateRoomDialog
        isOpen={showCreateRoomDialog}
        onClose={() => setShowCreateRoomDialog(false)}
        onCreateRoom={handleCreateRoomSubmit}
      />

      <PasswordDialog
        isOpen={showPasswordDialog}
        onClose={() => {
          setShowPasswordDialog(false);
          setPasswordRoom(null);
        }}
        onJoinRoom={handlePasswordSubmit}
        room={passwordRoom!}
      />

      {error && (
        <div className="fixed bottom-4 right-4 bg-red-500 text-white px-4 py-2 rounded shadow-lg">
          {error}
        </div>
      )}
    </div>
  );
} 