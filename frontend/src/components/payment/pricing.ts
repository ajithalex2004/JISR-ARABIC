// Plan prices (USD, 5% UAE VAT included). The server is the source of truth for what is charged;
// these label the plan cards and upgrade prompts.
export const TERM_USD = 10;
export const ANNUAL_LIST_USD = 30;
export const ANNUAL_USD = 25.5;
export const AED_PER_USD = 3.6725;
export const usd = (n: number) => `USD ${n.toFixed(2)}`;
export const aed = (n: number) => `AED ${(n * AED_PER_USD).toFixed(2)}`;
