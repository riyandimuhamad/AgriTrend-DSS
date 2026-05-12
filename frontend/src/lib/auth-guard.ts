import { redirect } from "@tanstack/react-router";
import { isAuthenticated } from "./auth";

export function requireAuth() {
  if (!isAuthenticated()) {
    throw redirect({ to: "/login" });
  }
}
