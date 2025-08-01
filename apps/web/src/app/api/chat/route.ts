import { openai } from "@ai-sdk/openai";
import { streamText } from "ai";

export async function POST() {
  // Authentication disabled - chat not available
  return new Response("Chat feature requires authentication", { status: 401 });
}
