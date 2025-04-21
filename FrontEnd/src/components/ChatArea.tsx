import { useRef, useEffect } from 'react';
import { Message, Room, User } from '@/lib/api';

interface ChatAreaProps {
  room: Room | null;
  messages: Message[];
  currentUser: User | null;
  newMessage: string;
  onNewMessageChange: (message: string) => void;
  onSendMessage: (e: React.FormEvent) => Promise<void>;
}

export function ChatArea({
  room,
  messages,
  currentUser,
  newMessage,
  onNewMessageChange,
  onSendMessage
}: ChatAreaProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  if (!room) {
    return (
      <div className="flex-1 flex items-center justify-center text-gray-500">
        Select a room to start chatting
      </div>
    );
  }

  return (
    <>
      <div className="p-4 border-b">
        <h2 className="text-xl font-bold">{room.name}</h2>
      </div>

      <div className="flex-1 overflow-y-auto p-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`mb-4 ${
              message.user.id === currentUser?.id ? 'text-right' : ''
            }`}
          >
            <div
              className={`inline-block p-2 rounded-lg ${
                message.user.id === currentUser?.id
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-200'
              }`}
            >
              <div className="text-sm font-bold">
                {message.user.username}
              </div>
              <div>{message.content}</div>
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={onSendMessage} className="p-4 border-t">
        <div className="flex space-x-4">
          <input
            type="text"
            value={newMessage}
            onChange={(e) => onNewMessageChange(e.target.value)}
            placeholder="Type a message..."
            className="flex-1 p-2 border rounded-lg"
          />
          <button
            type="submit"
            className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
          >
            Send
          </button>
        </div>
      </form>
    </>
  );
} 