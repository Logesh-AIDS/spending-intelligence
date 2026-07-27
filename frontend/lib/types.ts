import { AxiosError } from 'axios';

export interface ApiError {
  status: number;
  message: string;
  code?: string;
}

export interface ApiErrorResponse {
  error: ApiError;
}

export type ApiErrorType = AxiosError<ApiErrorResponse>;

export const isApiError = (error: unknown): error is ApiErrorType => {
  return error instanceof AxiosError && error.response?.data?.error !== undefined;
};

export const getApiErrorMessage = (error: unknown): string => {
  if (isApiError(error)) {
    return error.response?.data?.error?.message || 'An error occurred';
  }
  if (error instanceof Error) {
    return error.message;
  }
  return 'An unknown error occurred';
};
