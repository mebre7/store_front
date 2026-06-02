import React, { FormEvent, useEffect, useMemo, useState } from 'react';
import ReactDOM from 'react-dom/client';
import { CheckCircle2, Minus, PackageCheck, Plus, Search, ShoppingBag, Trash2 } from 'lucide-react';
import { api, Cart, Collection, money, Order, Product, productImage } from './lib/api';
import './styles.css';

const cartKey = 'storefront.cartId';

function App() {
  const [products, setProducts] = useState<Product[]>([]);
  const [collections, setCollections] = useState<Collection[]>([]);
  const [cart, setCart] = useState<Cart | null>(null);
  const [query, setQuery] = useState('');
  const [collection, setCollection] = useState('all');
  const [loading, setLoading] = useState(true);
  const [notice, setNotice] = useState('');
  const [order, setOrder] = useState<Order | null>(null);

  const cartCount = useMemo(() => cart?.items.reduce((total, item) => total + item.quantity, 0) ?? 0, [cart]);

  useEffect(() => {
    api.collections().then((data) => setCollections(data.results)).catch(console.error);
  }, []);

  useEffect(() => {
    const params = new URLSearchParams({ available: 'true' });
    if (query) params.set('search', query);
    if (collection !== 'all') params.set('collection', collection);

    setLoading(true);
    api.products(params)
      .then((data) => setProducts(data.results))
      .catch((error) => setNotice(error.message))
      .finally(() => setLoading(false));
  }, [query, collection]);

  useEffect(() => {
    const existingCartId = localStorage.getItem(cartKey);
    if (existingCartId) {
      api.getCart(existingCartId).then(setCart).catch(() => localStorage.removeItem(cartKey));
    }
  }, []);

  async function ensureCart() {
    if (cart) return cart;
    const newCart = await api.createCart();
    localStorage.setItem(cartKey, newCart.id);
    setCart(newCart);
    return newCart;
  }

  async function addToCart(product: Product) {
    const activeCart = await ensureCart();
    await api.addCartItem(activeCart.id, product.id, 1);
    const freshCart = await api.getCart(activeCart.id);
    setCart(freshCart);
    setNotice(`${product.title} added to cart.`);
  }

  async function updateQuantity(itemId: number, quantity: number) {
    if (!cart) return;
    if (quantity < 1) {
      await api.deleteCartItem(cart.id, itemId);
    } else {
      await api.updateCartItem(cart.id, itemId, quantity);
    }
    setCart(await api.getCart(cart.id));
  }

  async function submitCheckout(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!cart) return;
    const form = new FormData(event.currentTarget);
    const completedOrder = await api.checkout({
      cart_id: cart.id,
      first_name: String(form.get('first_name')),
      last_name: String(form.get('last_name')),
      email: String(form.get('email')),
      phone: String(form.get('phone') ?? ''),
    });
    setOrder(completedOrder);
    setCart(null);
    localStorage.removeItem(cartKey);
  }

  return (
    <main>
      <header className="app-header">
        <div>
          <p className="eyebrow">Production storefront</p>
          <h1>Curated goods for sharper everyday systems.</h1>
        </div>
        <div className="cart-pill" aria-label={`${cartCount} cart items`}>
          <ShoppingBag size={18} />
          <span>{cartCount}</span>
        </div>
      </header>

      <section className="toolbar" aria-label="Catalog filters">
        <label className="search-box">
          <Search size={18} />
          <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search products" />
        </label>
        <select value={collection} onChange={(event) => setCollection(event.target.value)}>
          <option value="all">All collections</option>
          {collections.map((item) => (
            <option key={item.id} value={item.id}>
              {item.title}
            </option>
          ))}
        </select>
      </section>

      {notice && (
        <button className="notice" onClick={() => setNotice('')}>
          <CheckCircle2 size={18} />
          {notice}
        </button>
      )}

      <section className="layout">
        <div className="catalog" aria-live="polite">
          {loading ? (
            <div className="empty-state">Loading catalog...</div>
          ) : products.length === 0 ? (
            <div className="empty-state">No products match this search.</div>
          ) : (
            products.map((product) => (
              <article className="product-card" key={product.id}>
                <img src={productImage(product)} alt="" />
                <div className="product-body">
                  <span>{product.collection ?? 'General'}</span>
                  <h2>{product.title}</h2>
                  <p>{product.description}</p>
                  <div className="product-actions">
                    <strong>{money(product.price)}</strong>
                    <button onClick={() => addToCart(product)}>
                      <Plus size={18} />
                      Add
                    </button>
                  </div>
                </div>
              </article>
            ))
          )}
        </div>

        <aside className="checkout-panel" aria-label="Cart and checkout">
          <div className="panel-heading">
            <PackageCheck size={20} />
            <h2>Checkout</h2>
          </div>

          {order ? (
            <div className="success-state">
              <CheckCircle2 size={28} />
              <h3>Order #{order.id} placed</h3>
              <p>{money(order.total_price)} total, payment {order.payment_status_label.toLowerCase()}.</p>
            </div>
          ) : (
            <>
              <div className="cart-lines">
                {!cart || cart.items.length === 0 ? (
                  <p className="muted">Your cart is ready when you are.</p>
                ) : (
                  cart.items.map((item) => (
                    <div className="cart-line" key={item.id}>
                      <div>
                        <strong>{item.product.title}</strong>
                        <span>{money(item.total_price)}</span>
                      </div>
                      <div className="stepper">
                        <button aria-label="Decrease quantity" onClick={() => updateQuantity(item.id, item.quantity - 1)}>
                          {item.quantity === 1 ? <Trash2 size={15} /> : <Minus size={15} />}
                        </button>
                        <span>{item.quantity}</span>
                        <button aria-label="Increase quantity" onClick={() => updateQuantity(item.id, item.quantity + 1)}>
                          <Plus size={15} />
                        </button>
                      </div>
                    </div>
                  ))
                )}
              </div>

              <div className="total-row">
                <span>Total</span>
                <strong>{money(cart?.total_price ?? 0)}</strong>
              </div>

              <form onSubmit={submitCheckout}>
                <div className="name-grid">
                  <input name="first_name" placeholder="First name" required />
                  <input name="last_name" placeholder="Last name" required />
                </div>
                <input name="email" type="email" placeholder="Email" required />
                <input name="phone" placeholder="Phone" />
                <button className="primary" disabled={!cart || cart.items.length === 0}>
                  Place order
                </button>
              </form>
            </>
          )}
        </aside>
      </section>
    </main>
  );
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
