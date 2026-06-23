import { useState, useEffect, useCallback, useRef } from "react";
import { Link } from "react-router-dom";
import { ShoppingCart, Star, Search, SlidersHorizontal } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { productsApi, type Product } from "@/lib/api";
import { formatCurrency } from "@/lib/utils";
import { useCartStore } from "@/store/cart";
import { flyToCart } from "@/lib/flyToCart";

const PAGE_SIZE = 20;

export function Catalog() {
  const [products, setProducts] = useState<Product[]>([]);
  const [categories, setCategories] = useState<string[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string>("");
  const [search, setSearch] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState("");
  const [skip, setSkip] = useState(0);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const { addItem } = useCartStore();

  useEffect(() => {
    productsApi.categories().then(setCategories);
  }, []);

  useEffect(() => {
    const t = setTimeout(() => setDebouncedSearch(search), 300);
    return () => clearTimeout(t);
  }, [search]);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const res = await productsApi.list({
        category: selectedCategory || undefined,
        search: debouncedSearch || undefined,
        skip,
        limit: PAGE_SIZE,
      });
      setProducts(res.items);
      setTotal(res.total);
    } finally {
      setLoading(false);
    }
  }, [selectedCategory, debouncedSearch, skip]);

  useEffect(() => {
    setSkip(0);
  }, [selectedCategory, debouncedSearch]);

  useEffect(() => {
    load();
  }, [load]);

  const handleAddToCart = (product: Product, cardEl: HTMLElement | null) => {
    if (cardEl) flyToCart(cardEl);
    addItem(product);
  };

  const totalPages = Math.ceil(total / PAGE_SIZE);
  const currentPage = Math.floor(skip / PAGE_SIZE) + 1;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex flex-col sm:flex-row gap-4 mb-8">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
          <Input
            className="pl-9"
            placeholder="Search products..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <div className="flex items-center gap-2">
          <SlidersHorizontal className="h-4 w-4 text-gray-500" />
          <span className="text-sm text-gray-500 hidden sm:inline">Category:</span>
          <select
            className="h-10 rounded-md border border-gray-200 px-3 text-sm bg-white cursor-pointer focus:outline-none focus:ring-2 focus:ring-gray-900"
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
          >
            <option value="">All</option>
            {categories.map((c) => (
              <option key={c} value={c}>
                {c.replace(/-/g, " ")}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="flex items-center justify-between mb-4">
        <p className="text-sm text-gray-500">
          {loading ? "Loading..." : `${total} product${total !== 1 ? "s" : ""}`}
        </p>
        {selectedCategory && (
          <Badge variant="secondary" className="cursor-pointer" onClick={() => setSelectedCategory("")}>
            {selectedCategory} ✕
          </Badge>
        )}
      </div>

      {loading ? (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
          {Array.from({ length: 20 }).map((_, i) => (
            <div key={i} className="rounded-xl bg-gray-100 animate-pulse aspect-square" />
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
          {products.map((product) => (
            <ProductCard key={product.id} product={product} onAddToCart={handleAddToCart} />
          ))}
        </div>
      )}

      {!loading && totalPages > 1 && (
        <div className="flex justify-center items-center gap-2 mt-8">
          <Button
            variant="outline"
            size="sm"
            disabled={currentPage === 1}
            onClick={() => setSkip(Math.max(0, skip - PAGE_SIZE))}
          >
            Previous
          </Button>
          <span className="text-sm text-gray-500">
            Page {currentPage} of {totalPages}
          </span>
          <Button
            variant="outline"
            size="sm"
            disabled={currentPage === totalPages}
            onClick={() => setSkip(skip + PAGE_SIZE)}
          >
            Next
          </Button>
        </div>
      )}
    </div>
  );
}

function ProductCard({
  product,
  onAddToCart,
}: {
  product: Product;
  onAddToCart: (p: Product, cardEl: HTMLElement | null) => void;
}) {
  const cardRef = useRef<HTMLDivElement>(null);
  const discountedPrice = product.price * (1 - product.discount_percentage / 100);

  return (
    <div
      ref={cardRef}
      className="group flex flex-col rounded-xl border border-gray-100 bg-white hover:shadow-md transition-shadow overflow-hidden"
    >
      <Link to={`/products/${product.id}`} className="block cursor-pointer">
        <div className="aspect-square bg-gray-50 overflow-hidden">
          {product.thumbnail ? (
            <img
              src={product.thumbnail}
              alt={product.title}
              className="h-full w-full object-cover group-hover:scale-105 transition-transform duration-300"
            />
          ) : (
            <div className="h-full w-full flex items-center justify-center text-gray-300">
              <ShoppingCart className="h-8 w-8" />
            </div>
          )}
        </div>
      </Link>

      <div className="p-3 flex flex-col flex-1">
        {product.category && (
          <span className="text-xs text-gray-400 capitalize mb-1">
            {product.category.replace(/-/g, " ")}
          </span>
        )}
        <Link
          to={`/products/${product.id}`}
          className="text-sm font-medium text-gray-900 line-clamp-2 flex-1 cursor-pointer hover:text-gray-600 transition-colors"
        >
          {product.title}
        </Link>

        <div className="flex items-center gap-1 mt-1">
          <Star className="h-3 w-3 fill-yellow-400 text-yellow-400" />
          <span className="text-xs text-gray-500">{product.rating.toFixed(1)}</span>
        </div>

        <div className="flex items-center gap-2 mt-2">
          <span className="font-semibold text-sm">{formatCurrency(discountedPrice)}</span>
          {product.discount_percentage > 0 && (
            <span className="text-xs text-gray-400 line-through">{formatCurrency(product.price)}</span>
          )}
        </div>

        <Button
          size="sm"
          className="mt-3 w-full"
          onClick={() => onAddToCart(product, cardRef.current)}
          disabled={product.stock === 0}
        >
          {product.stock === 0 ? "Out of stock" : "Add to cart"}
        </Button>
      </div>
    </div>
  );
}
