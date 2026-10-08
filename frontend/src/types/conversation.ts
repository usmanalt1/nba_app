export interface ConversationExchange {
    question: string;
    answer: string;
    /** Seconds, as a string: the API parses it out of the Redis key. */
    time_requested: string;
}
