export interface APIResponse<T> {
  success: boolean;
  data: T;
  message?: string;
}

export interface PaginatedResponse<T> {
  success: boolean;
  data: T[];
  pagination: {
    page: number;
    page_size: number;
    total_items: number;
    total_pages: number;
  };
  message?: string;
}
