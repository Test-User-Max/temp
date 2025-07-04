import { useState, useEffect, useRef } from 'react';

interface StreamingState {
  isStreaming: boolean;
  streamedContent: string;
  currentToken: string;
  progress: number;
  error: string | null;
}

export const useStreaming = () => {
  const [streamingState, setStreamingState] = useState<StreamingState>({
    isStreaming: false,
    streamedContent: '',
    currentToken: '',
    progress: 0,
    error: null
  });

  const eventSourceRef = useRef<EventSource | null>(null);

  const startStreaming = (sessionId: string) => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }

    const eventSource = new EventSource(`http://localhost:8000/stream/${sessionId}`);
    eventSourceRef.current = eventSource;

    setStreamingState({
      isStreaming: true,
      streamedContent: '',
      currentToken: '',
      progress: 0,
      error: null
    });

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        
        switch (data.type) {
          case 'stream_start':
            setStreamingState(prev => ({
              ...prev,
              isStreaming: true,
              streamedContent: '',
              error: null
            }));
            break;
            
          case 'token':
            setStreamingState(prev => ({
              ...prev,
              currentToken: data.token,
              streamedContent: data.accumulated,
              progress: data.progress
            }));
            break;
            
          case 'agent_progress':
            // Handle agent progress updates
            break;
            
          case 'complete':
            setStreamingState(prev => ({
              ...prev,
              isStreaming: false,
              streamedContent: data.full_response,
              progress: 1
            }));
            eventSource.close();
            break;
            
          case 'error':
            setStreamingState(prev => ({
              ...prev,
              isStreaming: false,
              error: data.error
            }));
            eventSource.close();
            break;
            
          case 'stream_end':
            setStreamingState(prev => ({
              ...prev,
              isStreaming: false
            }));
            eventSource.close();
            break;
        }
      } catch (error) {
        console.error('Error parsing stream data:', error);
      }
    };

    eventSource.onerror = (error) => {
      console.error('EventSource error:', error);
      setStreamingState(prev => ({
        ...prev,
        isStreaming: false,
        error: 'Streaming connection failed'
      }));
      eventSource.close();
    };
  };

  const stopStreaming = () => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }
    
    setStreamingState(prev => ({
      ...prev,
      isStreaming: false
    }));
  };

  useEffect(() => {
    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
    };
  }, []);

  return {
    ...streamingState,
    startStreaming,
    stopStreaming
  };
};