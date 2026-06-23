const BASE_URL = "/api/v1";

function getToken(): string | null {
  return localStorage.getItem("token");
}

async function request<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(`${BASE_URL}${path}`, { ...options, headers });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Unknown error" }));
    throw new Error(err.detail ?? `HTTP ${res.status}`);
  }
  return res.json() as Promise<T>;
}

// Auth
export const authApi = {
  signup: (email: string, password: string, name: string) =>
    request<{ access_token: string }>("/auth/signup", {
      method: "POST",
      body: JSON.stringify({ email, password, name }),
    }),
  signin: (email: string, password: string) =>
    request<{ access_token: string }>("/auth/signin", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),
  me: () => request<{ id: number; email: string; name: string }>("/auth/me"),
};

// Products
export interface Review {
  rating?: number;
  comment?: string;
  date?: string;
  reviewerName?: string;
}

export interface Product {
  id: number;
  title: string;
  description?: string;
  category?: string;
  price: number;
  discount_percentage: number;
  rating: number;
  stock: number;
  brand?: string;
  sku?: string;
  thumbnail?: string;
  warranty_information?: string;
  shipping_information?: string;
  return_policy?: string;
  images?: string[];
  reviews?: Review[];
}

export interface ProductListResponse {
  items: Product[];
  total: number;
  skip: number;
  limit: number;
}

export const productsApi = {
  list: (params: { category?: string; search?: string; skip?: number; limit?: number } = {}) => {
    const qs = new URLSearchParams();
    if (params.category) qs.set("category", params.category);
    if (params.search) qs.set("search", params.search);
    if (params.skip !== undefined) qs.set("skip", String(params.skip));
    if (params.limit !== undefined) qs.set("limit", String(params.limit));
    return request<ProductListResponse>(`/products?${qs}`);
  },
  categories: () => request<string[]>("/products/categories"),
  get: (id: number) => request<Product>(`/products/${id}`),
};

// Orders
export type OrderStatus =
  | "created"
  | "received"
  | "processing"
  | "shipped"
  | "delivered"
  | "cancelled";

export interface OrderItem {
  id: number;
  product_id: number;
  quantity: number;
  unit_price: number;
  product_title?: string;
  product_thumbnail?: string;
}

export interface Order {
  id: number;
  order_code: string;
  status: OrderStatus;
  carrier?: string;
  tracking?: string;
  eta?: string;
  delivered_at?: string;
  total: number;
  created_at: string;
  items: OrderItem[];
}

export const ordersApi = {
  checkout: (items: { product_id: number; quantity: number }[]) =>
    request<Order>("/orders", { method: "POST", body: JSON.stringify({ items }) }),
  list: () => request<Order[]>("/orders"),
  get: (id: number) => request<Order>(`/orders/${id}`),
  cancel: (id: number) => request<Order>(`/orders/${id}/cancel`, { method: "POST" }),
};

// Chat streaming
export function streamChat(
  messages: { role: string; content: string }[],
  onEvent: (event: { type: string; content?: string; name?: string; input?: string; output?: string }) => void,
  onDone: () => void,
  onError: (err: string) => void
): AbortController {
  const controller = new AbortController();
  const token = getToken();

  fetch(`${BASE_URL}/chat/stream`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: JSON.stringify({ messages }),
    signal: controller.signal,
  })
    .then(async (res) => {
      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: "Stream error" }));
        onError(err.detail ?? "Stream error");
        return;
      }
      const reader = res.body!.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n\n");
        buffer = lines.pop() ?? "";
        for (const line of lines) {
          if (line.startsWith("data: ")) {
            try {
              const data = JSON.parse(line.slice(6));
              if (data.type === "done") {
                onDone();
              } else {
                onEvent(data);
              }
            } catch {
              // skip malformed
            }
          }
        }
      }
      onDone();
    })
    .catch((err) => {
      if (err.name !== "AbortError") onError(String(err));
    });

  return controller;
}
