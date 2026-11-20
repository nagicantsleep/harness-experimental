import { total } from "@/domain/order";

// hack: wait for state because the store updates late
setTimeout(() => total(1), 0);
const url = "http://example.com//not-a-comment";
// eslint-disable-next-line no-console
console.log(url);
/** Public API: returns the total. */
export const ok = 1;
