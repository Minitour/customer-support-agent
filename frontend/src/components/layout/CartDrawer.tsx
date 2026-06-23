import { useNavigate } from "react-router-dom";
import { X, Trash2, Plus, Minus } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useCartStore } from "@/store/cart";
import { formatCurrency } from "@/lib/utils";
import { ordersApi } from "@/lib/api";
import { useAuthStore } from "@/store/auth";
import { useState } from "react";

export function CartDrawer() {
  const { items, open, setOpen, removeItem, updateQuantity, clear, total } = useCartStore();
  const { user } = useAuthStore();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleCheckout = async () => {
    if (!user) {
      navigate("/signin");
      setOpen(false);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const orderItems = items.map((i) => ({
        product_id: i.product.id,
        quantity: i.quantity,
      }));
      const order = await ordersApi.checkout(orderItems);
      clear();
      setOpen(false);
      navigate(`/orders/${order.id}`);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Checkout failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      {/* Backdrop — always in DOM, fades in/out */}
      <div
        className="fixed inset-0 z-40 bg-black/40 transition-opacity duration-300"
        style={{ opacity: open ? 1 : 0, pointerEvents: open ? "auto" : "none" }}
        onClick={() => setOpen(false)}
      />
      {/* Drawer panel — slides in from the right */}
      <div
        className="fixed right-0 top-0 z-50 h-full w-full max-w-md bg-white shadow-2xl flex flex-col transition-transform duration-300 ease-[cubic-bezier(0.25,1,0.5,1)]"
        style={{ transform: open ? "translateX(0)" : "translateX(100%)", pointerEvents: open ? "auto" : "none" }}
      >
        <div className="flex items-center justify-between p-4 border-b">
          <h2 className="text-lg font-semibold">Your Cart</h2>
          <Button variant="ghost" size="icon" onClick={() => setOpen(false)}>
            <X className="h-5 w-5" />
          </Button>
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {items.length === 0 ? (
            <div className="text-center text-gray-400 py-12">Your cart is empty</div>
          ) : (
            items.map((item) => (
              <div key={item.product.id} className="flex gap-3 items-start">
                {item.product.thumbnail && (
                  <img
                    src={item.product.thumbnail}
                    alt={item.product.title}
                    className="h-16 w-16 rounded-lg object-cover bg-gray-50 flex-shrink-0"
                  />
                )}
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium truncate">{item.product.title}</p>
                  <p className="text-sm text-gray-500">{formatCurrency(item.product.price)}</p>
                  <div className="flex items-center gap-2 mt-1">
                    <Button
                      variant="outline"
                      size="icon"
                      className="h-6 w-6"
                      onClick={() => updateQuantity(item.product.id, item.quantity - 1)}
                    >
                      <Minus className="h-3 w-3" />
                    </Button>
                    <span className="text-sm w-4 text-center">{item.quantity}</span>
                    <Button
                      variant="outline"
                      size="icon"
                      className="h-6 w-6"
                      onClick={() => updateQuantity(item.product.id, item.quantity + 1)}
                    >
                      <Plus className="h-3 w-3" />
                    </Button>
                  </div>
                </div>
                <Button
                  variant="ghost"
                  size="icon"
                  className="text-gray-400 hover:text-red-500"
                  onClick={() => removeItem(item.product.id)}
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
            ))
          )}
        </div>

        {items.length > 0 && (
          <div className="border-t p-4 space-y-3">
            {error && <p className="text-red-500 text-sm">{error}</p>}
            <div className="flex justify-between font-semibold">
              <span>Total</span>
              <span>{formatCurrency(total())}</span>
            </div>
            <Button className="w-full" onClick={handleCheckout} disabled={loading}>
              {loading ? "Placing order..." : "Checkout"}
            </Button>
          </div>
        )}
      </div>
    </>
  );
}
