import { api, getCsrfToken } from "./api";
import { fetchWithTimeout } from "@/lib/fetchWithTimeout";

export interface DifyStreamData {
    type: 'chunk' | 'end' | 'error';
    content?: string;
    fullAnswer?: string;
    conversationId?: string;
    sessionId?: string;
    message?: string;
}

interface DifyPayload {
    query: string;
    session_id?: string;
}

export const sendMessageToDifyStreaming = async (
    query: string,
    userId: string,
    conversationId: string = "",
    onData: (data: DifyStreamData) => void
) => {
    const url = `/api/chat/stream/`;

    const payload: DifyPayload = {
        query: query,
        session_id: conversationId,
    };

    const csrfToken = getCsrfToken();

    try {
        const response = await fetchWithTimeout(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                ...(csrfToken ? { "X-CSRFToken": csrfToken } : {}),
            },
            credentials: "include",
            body: JSON.stringify(payload),
        }, 60000); // 60s timeout for streaming

        if (!response.ok) {
            throw new Error(`Dify API Error: ${response.status}`);
        }

        if (!response.body) {
            throw new Error('Response body is null');
        }

        // Handle streaming response
        const reader = response.body.getReader();
        const decoder = new TextDecoder('utf-8');
        let buffer = '';
        let fullAnswer = '';
        let conversationIdFromResponse = conversationId;

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n');
            buffer = lines.pop() || ''; // Keep unfinished part

            for (const line of lines) {
                if (line.trim() === '') continue;

                if (line.startsWith('data:')) {
                    const jsonStr = line.substring(5).trim();

                    try {
                        const data = JSON.parse(jsonStr);

                        // Handle Dify event types
                        switch (data.event) {
                            case 'message':
                                if (data.answer) {
                                    const content = data.answer;
                                    fullAnswer += content;
                                    if (onData) {
                                        onData({
                                            type: 'chunk',
                                            content: content,
                                            fullAnswer: fullAnswer
                                        });
                                    }
                                }
                                break;

                            case 'message_end':
                                if (data.conversation_id) {
                                    conversationIdFromResponse = data.conversation_id;
                                }
                                if (onData) {
                                    onData({
                                        type: 'end',
                                        conversationId: conversationIdFromResponse,
                                        fullAnswer: fullAnswer
                                    });
                                }
                                break;
                            case 'session_created':
                                if (data.session_id && onData) {
                                    onData({
                                        type: 'chunk',
                                        sessionId: data.session_id
                                    });
                                }
                                break;
                            case 'error':
                                const errorMsg = data.message || 'Unknown error';
                                if (onData) {
                                    onData({
                                        type: 'error',
                                        message: errorMsg
                                    });
                                }
                                throw new Error(errorMsg);
                        }
                    } catch (e) {
                        if (e instanceof Error && e.message.includes('JSON')) {
                            console.error('JSON Parse Error:', e, 'Raw data:', jsonStr);
                        } else {
                            // Re-throw if it's our own error from the switch case
                            throw e;
                        }
                    }
                }
            }
        }

        return {
            success: true,
            conversationId: conversationIdFromResponse,
            answer: fullAnswer
        };

    } catch (error) {
        console.error("Error communicating with Dify:", error);
        if (onData) {
            onData({
                type: 'error',
                message: error instanceof Error ? error.message : "Network or API error"
            })
        }
        throw error;
    }
};                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     
