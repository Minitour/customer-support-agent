import { Link, useNavigate } from "react-router-dom";
import { ShoppingCart, ShoppingBag, Package, LogOut } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useAuthStore } from "@/store/auth";
import { useCartStore } from "@/store/cart";

export function Navbar() {
  const { user, logout } = useAuthStore();
  const { items, setOpen } = useCartStore();
  const navigate = useNavigate();

  const itemCount = items.reduce((sum, i) => sum + i.quantity, 0);

  const handleLogout = () => {
    logout();
    navigate("/signin");
  };

  return (
    <header className="sticky top-0 z-40 bg-white border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 items-center justify-between">
          <Link to="/" className="flex items-center gap-2 font-bold text-xl text-gray-900">
            <ShoppingBag className="h-6 w-6" />
            ShopEase
          </Link>

          <nav className="flex items-center gap-1">
            <Button variant="ghost" size="sm" asChild>
              <Link to="/"><span className="hidden sm:inline">Products</span></Link>
            </Button>
            {user && (
              <Button variant="ghost" size="sm" asChild>
                <Link to="/orders">
                  <Package className="h-4 w-4 sm:mr-1" />
                  <span className="hidden sm:inline">My Orders</span>
                </Link>
              </Button>
            )}
          </nav>

          <div className="flex items-center gap-2">
            {user ? (
              <>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setOpen(true)}
                  className="relative"
                >
                  <ShoppingCart className="h-4 w-4" />
                  {itemCount > 0 && (
                    <span className="absolute -top-1.5 -right-1.5 h-4 w-4 rounded-full bg-gray-900 text-white text-xs flex items-center justify-center">
                      {itemCount}
                    </span>
                  )}
                </Button>
                <Button variant="ghost" size="sm" onClick={handleLogout}>
                  <LogOut className="h-4 w-4" />
                </Button>
              </>
            ) : (
              <>
                <Button variant="ghost" size="sm" asChild>
                  <Link to="/signin">Sign In</Link>
                </Button>
                <Button size="sm" asChild>
                  <Link to="/signup">Sign Up</Link>
                </Button>
              </>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}
