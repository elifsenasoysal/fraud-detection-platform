import { useEffect, useRef, useState, useCallback } from 'react';
import { WS_URL } from '../config/api';

interface WSMessage {
  type: string;
  data: Record<string, unknown>;
}

export function useWebSocket() {
  const [messages, setMessages] = useState<WSMessage[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeout = useRef<number>();

  const connect = useCallback(() => {
    try {
      const ws = new WebSocket(WS_URL);

      ws.onopen = () => {
        setIsConnected(true);
        console.log('🔌 WebSocket connected');
      };

      ws.onmessage = (event) => {
        try {
          const parsed = JSON.parse(event.data);
          setMessages((prev) => [parsed, ...prev].slice(0, 100));
        } catch {
          // ignore non-JSON messages
        }
      };

      ws.onclose = () => {
        setIsConnected(false);
        console.log('🔌 WebSocket disconnected, reconnecting...');
        reconnectTimeout.current = window.setTimeout(connect, 3000);
      };

      ws.onerror = () => {
        ws.close();
      };

      wsRef.current = ws;
    } catch {
      reconnectTimeout.current = window.setTimeout(connect, 3000);
    }
  }, []);

  useEffect(() => {
    connect();
    return () => {
      clearTimeout(reconnectTimeout.current);
      wsRef.current?.close();
    };
  }, [connect]);

  return { messages, isConnected };
}
