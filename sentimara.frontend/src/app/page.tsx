"use client";

import { useState, useEffect, useRef } from 'react';
import { Send, Bot, User, Loader2 } from 'lucide-react';

interface Message {
  id: string | number | null;
  content: string;
  role: 'user' | 'assistant';
  timestamp: Date;
  isError?: boolean;
}

export default function SentimaraChat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [currentStreamingMessage, setCurrentStreamingMessage] = useState('');
  const [conversationId, setConversationId] = useState<string | null>(null);
  const messagesEndRef = useRef(null);
  const eventSourceRef = useRef(null);

  
  // Create a new conversation
  const createConversation = async (): Promise<string | null> => {
    try {
      const response = await fetch('http://localhost:8000/api/conversation/', {
        method: 'POST',
        headers: {
          'accept': 'application/json',
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          document_ids: []
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      const newConversationId = data.id;
      
      setConversationId(newConversationId);
      console.log('New conversation created:', newConversationId);
      
      return newConversationId;
    } catch (error) {
      console.error('Error creating conversation:', error);
      
      // Add error message to chat
      setMessages(prev => [...prev, {
        id: Date.now(),
        content: 'Failed to create conversation. Please check your connection and try again.',
        role: 'assistant',
        timestamp: new Date(),
        isError: true
      }]);
      
      return null;
    }
  };

  const scrollToBottom = () => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  };

  const closeEventSource = () => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }
  };


  // Initialize conversation on component mount
  useEffect(() => {
    createConversation();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, currentStreamingMessage]);


  const sendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    // Ensure we have a conversation ID
    let currentConversationId = conversationId;
    if (!currentConversationId) {
      currentConversationId = await createConversation();
      if (!currentConversationId) {
        return; // Error already handled in createConversation
      }
    }

    const userMessage = inputValue.trim();
    setInputValue('');
    setIsLoading(true);
    setCurrentStreamingMessage('');

    // Add user message to chat
    setMessages(prev => [...prev, {
      id: Date.now(),
      content: userMessage,
      role: 'user',
      timestamp: new Date()
    }]);

    try {
      // Close any existing connection
      closeEventSource();

      // Encode the message for URL
      const encodedMessage = encodeURIComponent(userMessage);
      const streamUrl = `http://localhost:8000/api/conversation/${currentConversationId}/message?user_message=${encodedMessage}&temperature=0.7`;

      // Start SSE connection
      const eventSource = new EventSource(streamUrl);
      eventSourceRef.current = eventSource;

      let assistantMessageId: string | number | null = null;

      eventSource.onmessage = (event) => {
        try {
          // Skip ping messages
          if (event.data.includes('ping -')) {
            return;
          }

          const data = JSON.parse(event.data);
          
          // Handle the streaming response structure
          if (data.role === 'assistant') {
            assistantMessageId = data.id;
            
            // Update streaming content with the full content
            if (data.content) {
              setCurrentStreamingMessage(data.content);
            }

            // Check if message is complete (SUCCESS status means it's finished)
            if (data.status === 'SUCCESS') {
              // Add complete message to chat
              setMessages(prev => [...prev, {
                id: assistantMessageId || Date.now(),
                content: data.content,
                role: 'assistant',
                timestamp: new Date()
              }]);
              
              setCurrentStreamingMessage('');
              setIsLoading(false);
              closeEventSource();
            }
          }
        } catch (error) {
          console.error('Error parsing SSE data:', error);
          console.log('Raw event data:', event.data);
        }
      };

      eventSource.onerror = (error) => {
        console.error('SSE connection error:', error);
        setIsLoading(false);
        setCurrentStreamingMessage('');
        closeEventSource();
        
        // Add error message
        setMessages(prev => [...prev, {
          id: Date.now(),
          content: 'Sorry, there was an error processing your message. Please try again.',
          role: 'assistant',
          timestamp: new Date(),
          isError: true
        }]);
      };

      eventSource.onopen = () => {
        console.log('SSE connection opened');
      };

    } catch (error) {
      console.error('Error sending message:', error);
      setIsLoading(false);
      setCurrentStreamingMessage('');
      
      setMessages(prev => [...prev, {
        id: Date.now(),
        content: 'Failed to send message. Please check your connection and try again.',
        role: 'assistant',
        timestamp: new Date(),
        isError: true
      }]);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      closeEventSource();
    };
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-emerald-100">
      <div className="container mx-auto max-w-4xl px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl text-gray-800 font-bold mb-2">Sentimara</h1>
          <p className="text-gray-800">Your Old Mutual intelligent assistant</p>
        </div>

        {/* Chat Container */}
        <div className="bg-white rounded-2xl shadow-xl border border-green-200 h-[600px] flex flex-col">
          {/* Messages Area */}
          <div className="flex-1 overflow-y-auto p-6 space-y-4">
            {messages.length === 0 && !currentStreamingMessage && (
              <div className="text-center text-green-600 mt-20">
                <Bot className="mx-auto mb-4 w-12 h-12 text-green-500" />
                <p className="text-lg">Welcome to Sentimara!</p>
                <p className="text-sm mt-2">Your Old Mutual assistant is ready to help you.</p>
              </div>
            )}

            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex items-start gap-3 ${
                  message.role === 'user' ? 'flex-row-reverse' : 'flex-row'
                }`}
              >
                <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                  message.role === 'user' 
                    ? 'bg-green-600 text-white' 
                    : message.isError 
                    ? 'bg-red-500 text-white'
                    : 'bg-green-100 text-green-800'
                }`}>
                  {message.role === 'user' ? (
                    <User className="w-4 h-4" />
                  ) : (
                    <Bot className="w-4 h-4" />
                  )}
                </div>
                
                <div className={`max-w-[80%] p-3 rounded-2xl ${
                  message.role === 'user'
                    ? 'bg-green-600 text-white'
                    : message.isError
                    ? 'bg-red-50 text-red-800 border border-red-200'
                    : 'bg-green-50 text-green-900 border border-green-200'
                }`}>
                  <p className="whitespace-pre-wrap">{message.content}</p>
                  <div className={`text-xs mt-1 opacity-70 ${
                    message.role === 'user' ? 'text-green-100' : 'text-green-600'
                  }`}>
                    {message.timestamp.toLocaleTimeString()}
                  </div>
                </div>
              </div>
            ))}

            {/* Streaming Message */}
            {currentStreamingMessage && (
              <div className="flex items-start gap-3">
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-green-100 text-green-800 flex items-center justify-center">
                  <Bot className="w-4 h-4" />
                </div>
                <div className="max-w-[80%] p-3 rounded-2xl bg-green-50 text-green-900 border border-green-200">
                  <p className="whitespace-pre-wrap">{currentStreamingMessage}</p>
                  <div className="flex items-center gap-1 mt-2">
                    <Loader2 className="w-3 h-3 animate-spin text-green-600" />
                    <span className="text-xs text-green-600">Typing...</span>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <div className="border-t border-green-200 p-4">
            <div className="flex gap-3">
              <div className="flex-1 relative">
                <textarea
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Type your message here..."
                  className="w-full p-3 pr-12 border border-green-300 text-gray-800 rounded-xl focus:ring-2 focus:ring-green-500 focus:border-transparent resize-none min-h-[50px] max-h-32"
                  rows={1}
                  disabled={isLoading}
                />
              </div>
              <button
                onClick={sendMessage}
                disabled={!inputValue.trim() || isLoading}
                className={`px-6 py-3 rounded-xl font-medium transition-all duration-200 flex items-center gap-2 ${
                  !inputValue.trim() || isLoading
                    ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                    : 'bg-green-600 hover:bg-green-700 text-white shadow-lg hover:shadow-xl'
                }`}
              >
                {isLoading ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <Send className="w-4 h-4" />
                )}
                Send
              </button>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="text-center mt-6 text-gray-800 text-sm">
          <p>Team 6 - Hackstation </p>
        </div>
      </div>
    </div>
  );
}