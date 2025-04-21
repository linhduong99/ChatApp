import { useState } from 'react';
import { Room } from '@/lib/api';

interface PasswordDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onJoinRoom: (room: Room, password: string) => Promise<boolean>;
  room: Room;
}

export function PasswordDialog({ isOpen, onClose, onJoinRoom, room }: PasswordDialogProps) {
  const [password, setPassword] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const success = await onJoinRoom(room, password);
    if (success) {
      setPassword('');
      onClose();
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
      <div className="bg-white p-6 rounded-lg w-96">
        <h2 className="text-xl font-bold mb-4">Enter Room Password</h2>
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="block text-gray-700 text-sm font-bold mb-2">
              Password
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full p-2 border rounded"
              required
            />
          </div>
          <div className="flex justify-end space-x-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-gray-600 hover:text-gray-800"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
            >
              Join
            </button>
          </div>
        </form>
      </div>
    </div>
  );
} 