export type Paginated<T> = {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
};

export type Collection = {
  id: number;
  title: string;
  products_count: number;
};

export type Product = {
  id: number;
  title: string;
  slug: string;
  description: string | null;
  inventory: number;
  price: number;
  price_with_tax: number;
  collection: string | null;
  is_available: boolean;
};

export type CartItem = {
  id: number;
  product: Pick<Product, 'id' | 'title'> & { unit_price: number };
  quantity: number;
  unit_price: number;
  total_price: number;
};

export type Cart = {
  id: string;
  items: CartItem[];
  total_price: number;
};

export type CheckoutPayload = {
  cart_id: string;
  first_name: string;
  last_name: string;
  email: string;
  phone: string;
};

export type Order = {
  id: number;
  payment_status_label: string;
  total_price: number;
};

const API_BASE = '/api/store';

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(init?.headers ?? {}),
    },
    ...init,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(error.detail ?? JSON.stringify(error));
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json();
}

export const api = {
  collections: () => request<Paginated<Collection>>('/collections/'),
  products: (params: URLSearchParams) => request<Paginated<Product>>(`/products/?${params.toString()}`),
  createCart: () => request<Cart>('/carts/', { method: 'POST', body: JSON.stringify({}) }),
  getCart: (cartId: string) => request<Cart>(`/carts/${cartId}/`),
  addCartItem: (cartId: string, productId: number, quantity = 1) =>
    request<CartItem>(`/carts/${cartId}/items/`, {
      method: 'POST',
      body: JSON.stringify({ product_id: productId, quantity }),
    }),
  updateCartItem: (cartId: string, itemId: number, quantity: number) =>
    request<CartItem>(`/carts/${cartId}/items/${itemId}/`, {
      method: 'PATCH',
      body: JSON.stringify({ quantity }),
    }),
  deleteCartItem: (cartId: string, itemId: number) =>
    request<void>(`/carts/${cartId}/items/${itemId}/`, { method: 'DELETE' }),
  checkout: (payload: CheckoutPayload) =>
    request<Order>('/carts/checkout/', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
};

export function money(value: number | string) {
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(Number(value));
}

export function productImage(product: Product) {
  const title = product.title.toLowerCase();
  const query = title.includes('lamp')
    ? 'photo-1507473885765-e6ed057f782c'
    : title.includes('jacket')
      ? 'photo-1542291026-7eec264c27ff'
      : title.includes('pack')
        ? 'photo-1622560480605-d83c853bc5c3'
        : title.includes('mug')
          ? 'photo-1514228742587-6b1558fcca3d'
          : 'photo-1491553895911-0055eca6402d';
  return `https://images.unsplash.com/${query}?auto=format&fit=crop&w=900&q=80`;
}
