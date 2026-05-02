import { useEffect, useRef, useState, useCallback } from 'react';
import { WS_URL } from '../config/api';

interface WSMessage {
  type: string;
  data: Record<string, unknown>;
}

/**
 * WebSocket hook for real-time updates.
 *
 * @param filter - Optional message type filter (e.g., 'fraud_alert', 'new_transaction').
 *                 When set, only messages matching this type will be added to the messages array.
 *                 When not set, all messages are included.
 */
export function useWebSocket(filter?: string) {
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
          const parsed: WSMessage = JSON.parse(event.data);

          // Apply type filter if specified
          if (filter && parsed.type !== filter) {
            return;
          }

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
  }, [filter]);

  useEffect(() => {
    connect();
    return () => {
      clearTimeout(reconnectTimeout.current);
      wsRef.current?.close();
    };
  }, [connect]);

  return { messages, isConnected };
}
