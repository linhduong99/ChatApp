import { useState } from 'react';
import { Room, createRoom, verifyRoomPassword } from '@/lib/api';

export function useRooms(initialRooms: Room[] = []) {
  const [rooms, setRooms] = useState<Room[]>(initialRooms);
  const [selectedRoom, setSelectedRoom] = useState<Room | null>(null);
  const [createdRoomIds, setCreatedRoomIds] = useState<number[]>([]);
  const [error, setError] = useState<string | null>(null);

  const handleRoomSelect = (room: Room) => {
    setSelectedRoom(room);
  };

  const handleCreateRoom = async (name: string, password?: string): Promise<boolean> => {
    if (!name.trim()) return false;
    
    try {
      const response = await createRoom(name, password?.trim() || undefined);
      
      if (response.success && response.data) {
        const newRoom = response.data;
        setRooms((prev) => [...prev, newRoom]);
        setSelectedRoom(newRoom);
        setCreatedRoomIds((prev) => [...prev, newRoom.id]);
        setError(null);
        return true;
      } else {
        setError('Failed to create room');
        return false;
      }
    } catch (error) {
      console.error('Error creating room:', error);
      setError('Error creating room');
      return false;
    }
  };

  const handleJoinRoom = async (room: Room, password: string): Promise<boolean> => {
    if (!room || !password) return false;

    try {
      const response = await verifyRoomPassword(room.id, password);

      if (response.success) {
        setCreatedRoomIds((prev) => [...prev, room.id]);
        setError(null);
        return true;
      } else {
        setError('Invalid password');
        return false;
      }
    } catch (error) {
      console.error('Error verifying password:', error);
      setError('Error verifying password');
      return false;
    }
  };

  const updateRooms = (newRooms: Room[]) => {
    setRooms(newRooms);
  };

  return {
    rooms,
    selectedRoom,
    createdRoomIds,
    error,
    setError,
    handleRoomSelect,
    handleCreateRoom,
    handleJoinRoom,
    updateRooms
  };
} 