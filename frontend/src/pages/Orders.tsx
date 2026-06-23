import { useState, useEffect } from "react";
import { Link, useParams } from "react-router-dom";
import { Package, ChevronRight, Truck, CheckCircle, XCircle, Clock } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ordersApi, type Order, type OrderStatus } from "@/lib/api";
import { formatCurrency, formatDate } from "@/lib/utils";

function StatusBadge({ status }: { status: OrderStatus }) {
  const config: Record<OrderStatus, { label: string; variant: "default" | "secondary" | "success" | "warning" | "destructive" | "outline"; icon: React.ReactNode }> = {
    placed: { label: "Placed", variant: "secondary", icon: <Clock className="h-3 w-3" /> },
    out_for_delivery: { label: "Out for Delivery", variant: "warning", icon: <Truck className="h-3 w-3" /> },
    delivered: { label: "Delivered", variant: "success", icon: <CheckCircle className="h-3 w-3" /> },
    cancelled: { label: "Cancelled", variant: "destructive", icon: <XCircle className="h-3 w-3" /> },
  };
  const { label, variant, icon } = config[status];
  return (
    <Badge variant={variant} className="flex items-center gap-1">
      {icon}
      {label}
    </Badge>
  );
}

export function Orders() {
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    ordersApi.list().then(setOrders).finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-8">
        <div className="space-y-4">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="h-24 rounded-xl bg-gray-100 animate-pulse" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-6">My Orders</h1>

      {orders.length === 0 ? (
        <div className="text-center py-16 text-gray-400">
          <Package className="h-12 w-12 mx-auto mb-3 opacity-30" />
          <p className="text-lg">No orders yet</p>
          <Button className="mt-4" asChild>
            <Link to="/">Start shopping</Link>
          </Button>
        </div>
      ) : (
        <div className="space-y-3">
          {orders.map((order) => (
            <Link
              key={order.id}
              to={`/orders/${order.id}`}
              className="flex items-center gap-4 p-4 bg-white rounded-xl border border-gray-100 hover:shadow-md transition-shadow"
            >
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 flex-wrap">
                  <span className="font-mono font-semibold text-sm">{order.order_code}</span>
                  <StatusBadge status={order.status} />
                </div>
                <p className="text-sm text-gray-500 mt-1">
                  {formatDate(order.created_at)} · {order.items.length} item{order.items.length !== 1 ? "s" : ""}
                </p>
              </div>
              <div className="flex items-center gap-2">
                <span className="font-semibold">{formatCurrency(order.total)}</span>
                <ChevronRight className="h-4 w-4 text-gray-400" />
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}

export function OrderDetail() {
  const [order, setOrder] = useState<Order | null>(null);
  const [loading, setLoading] = useState(true);
  const [cancelling, setCancelling] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const { id } = useParams<{ id: string }>();
  const orderId = parseInt(id ?? "0");

  useEffect(() => {
    ordersApi.get(orderId).then(setOrder).finally(() => setLoading(false));
  }, [orderId]);

  const handleCancel = async () => {
    if (!order) return;
    setCancelling(true);
    setError(null);
    try {
      const updated = await ordersApi.cancel(order.id);
      setOrder(updated);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Could not cancel order");
    } finally {
      setCancelling(false);
    }
  };

  if (loading) return <div className="max-w-2xl mx-auto px-4 py-8 text-gray-400">Loading...</div>;
  if (!order) return <div className="max-w-2xl mx-auto px-4 py-8 text-gray-400">Order not found</div>;

  const canCancel = order.status === "placed" || order.status === "out_for_delivery";

  return (
    <div className="max-w-2xl mx-auto px-4 py-8 space-y-6">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm text-gray-500 mb-1">Order</p>
          <h1 className="text-2xl font-bold font-mono">{order.order_code}</h1>
        </div>
        <StatusBadge status={order.status} />
      </div>

      <div className="bg-white rounded-xl border border-gray-100 p-4 space-y-3">
        <h2 className="font-semibold text-sm text-gray-500 uppercase tracking-wide">Tracking</h2>
        <div className="grid grid-cols-2 gap-3 text-sm">
          <div>
            <p className="text-gray-400">Carrier</p>
            <p className="font-medium">{order.carrier ?? "—"}</p>
          </div>
          <div>
            <p className="text-gray-400">Tracking #</p>
            <p className="font-medium font-mono">{order.tracking ?? "—"}</p>
          </div>
          <div>
            <p className="text-gray-400">ETA</p>
            <p className="font-medium">{order.eta ? formatDate(order.eta) : "—"}</p>
          </div>
          <div>
            <p className="text-gray-400">Placed</p>
            <p className="font-medium">{formatDate(order.created_at)}</p>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-xl border border-gray-100 p-4 space-y-3">
        <h2 className="font-semibold text-sm text-gray-500 uppercase tracking-wide">Items</h2>
        <div className="space-y-3">
          {order.items.map((item) => (
            <div key={item.id} className="flex gap-3 items-center">
              {item.product_thumbnail && (
                <img
                  src={item.product_thumbnail}
                  alt={item.product_title ?? ""}
                  className="h-12 w-12 rounded-lg object-cover bg-gray-50"
                />
              )}
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium truncate">{item.product_title}</p>
                <p className="text-xs text-gray-400">Qty: {item.quantity}</p>
              </div>
              <p className="text-sm font-medium">{formatCurrency(item.unit_price * item.quantity)}</p>
            </div>
          ))}
        </div>
        <div className="border-t pt-3 flex justify-between font-semibold">
          <span>Total</span>
          <span>{formatCurrency(order.total)}</span>
        </div>
      </div>

      {error && <p className="text-red-500 text-sm">{error}</p>}

      {canCancel && (
        <Button variant="destructive" onClick={handleCancel} disabled={cancelling}>
          {cancelling ? "Cancelling..." : "Cancel Order"}
        </Button>
      )}

      <Button variant="outline" asChild>
        <Link to="/orders">← Back to Orders</Link>
      </Button>
    </div>
  );
}
