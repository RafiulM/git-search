import { currentUser } from "@clerk/nextjs/server";

export async function getCurrentUser() {
  return await currentUser();
}
