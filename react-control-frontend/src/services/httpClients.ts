import axios from "axios";

const commonHeaders = {
  "Content-Type": "application/json",
};

export const integrationApiClient = axios.create({
  baseURL: "/api",
  timeout: 10_000,
  headers: commonHeaders,
});

export const directApiClient = axios.create({
  baseURL: "/directapi",
  timeout: 10_000,
  headers: commonHeaders,
});

export const generationApiClient = axios.create({
  baseURL: "/generationapi",
  timeout: 10_000,
  headers: commonHeaders,
});
