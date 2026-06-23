import { useState, useEffect, useRef } from "react";
import { Link, useParams } from "react-router-dom";
import { ShoppingCart, Star, ChevronLeft, Truck, ShieldCheck, RotateCcw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { productsApi, type Product, type Review } from "@/lib/api";
import { formatCurrency, formatDate } from "@/lib/utils";
import { useCartStore } from "@/store/cart";
import { flyToCart } from "@/lib/flyToCart";

function Stars({ value, className = "h-4 w-4" }: { value: number; className?: string }) {
  return (
    <div className="flex items-center">
      {Array.from({ length: 5 }).map((_, i) => (
        <Star
          key={i}
          className={`${className} ${
            i < Math.round(value) ? "fill-yellow-400 text-yellow-400" : "text-gray-300"
          }`}
        />
      ))}
    </div>
  );
}

export function ProductDetail() {
  const { id } = useParams<{ id: string }>();
  const productId = parseInt(id ?? "0");

  const [product, setProduct] = useState<Product | null>(null);
  const [loading, setLoading] = useState(true);
  const [notFound, setNotFound] = useState(false);
  const [activeImage, setActiveImage] = useState(0);

  const { addItem } = useCartStore();
  const galleryRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setLoading(true);
    setNotFound(false);
    setActiveImage(0);
    productsApi
      .get(productId)
      .then(setProduct)
      .catch(() => setNotFound(true))
      .finally(() => setLoading(false));
  }, [productId]);

  if (loading) {
    return (
      <div className="max-w-6xl mx-auto px-4 py-8">
        <div className="grid md:grid-cols-2 gap-8">
          <div className="aspect-square rounded-2xl bg-gray-100 animate-pulse" />
          <div className="space-y-4">
            <div className="h-8 w-2/3 rounded bg-gray-100 animate-pulse" />
            <div className="h-4 w-1/3 rounded bg-gray-100 animate-pulse" />
            <div className="h-24 rounded bg-gray-100 animate-pulse" />
          </div>
        </div>
      </div>
    );
  }

  if (notFound || !product) {
    return (
      <div className="max-w-6xl mx-auto px-4 py-16 text-center text-gray-400">
        <p className="text-lg">Product not found</p>
        <Button className="mt-4" asChild>
          <Link to="/">Back to Products</Link>
        </Button>
      </div>
    );
  }

  const images = product.images && product.images.length > 0 ? product.images : product.thumbnail ? [product.thumbnail] : [];
  const reviews: Review[] = product.reviews ?? [];
  const discountedPrice = product.price * (1 - product.discount_percentage / 100);
  const reviewAvg =
    reviews.length > 0
      ? reviews.reduce((sum, r) => sum + (r.rating ?? 0), 0) / reviews.length
      : product.rating;

  const handleAddToCart = () => {
    if (galleryRef.current) flyToCart(galleryRef.current);
    addItem(product);
  };

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <Button variant="ghost" size="sm" className="mb-4 -ml-2" asChild>
        <Link to="/">
          <ChevronLeft className="h-4 w-4 mr-1" />
          Back to Products
        </Link>
      </Button>

      <div className="grid md:grid-cols-2 gap-8">
        {/* Gallery */}
        <div>
          <div ref={galleryRef} className="aspect-square rounded-2xl bg-gray-50 overflow-hidden border border-gray-100 flex items-center justify-center">
            {images.length > 0 ? (
              <img
                src={images[activeImage]}
                alt={product.title}
                className="h-full w-full object-contain"
              />
            ) : (
              <ShoppingCart className="h-16 w-16 text-gray-200" />
            )}
          </div>
          {images.length > 1 && (
            <div className="flex gap-2 mt-3 flex-wrap">
              {images.map((img, i) => (
                <button
                  key={i}
                  onClick={() => setActiveImage(i)}
                  className={`h-16 w-16 rounded-lg overflow-hidden border bg-gray-50 cursor-pointer transition-all ${
                    i === activeImage ? "border-gray-900 ring-2 ring-gray-900/10" : "border-gray-200 hover:border-gray-400"
                  }`}
                >
                  <img src={img} alt={`${product.title} ${i + 1}`} className="h-full w-full object-cover" />
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Info */}
        <div className="flex flex-col">
          {product.category && (
            <span className="text-xs text-gray-400 capitalize mb-2">{product.category.replace(/-/g, " ")}</span>
          )}
          <h1 className="text-2xl sm:text-3xl font-bold text-gray-900">{product.title}</h1>
          {product.brand && <p className="text-sm text-gray-500 mt-1">by {product.brand}</p>}

          <div className="flex items-center gap-2 mt-3">
            <Stars value={reviewAvg} />
            <span className="text-sm text-gray-500">
              {reviewAvg.toFixed(1)} · {reviews.length} review{reviews.length !== 1 ? "s" : ""}
            </span>
          </div>

          <div className="flex items-center gap-3 mt-4">
            <span className="text-3xl font-bold">{formatCurrency(discountedPrice)}</span>
            {product.discount_percentage > 0 && (
              <>
                <span className="text-lg text-gray-400 line-through">{formatCurrency(product.price)}</span>
                <Badge variant="success">-{product.discount_percentage.toFixed(0)}%</Badge>
              </>
            )}
          </div>

          <div className="mt-3">
            {product.stock > 0 ? (
              <span className="text-sm text-green-600 font-medium">In stock ({product.stock} available)</span>
            ) : (
              <span className="text-sm text-red-500 font-medium">Out of stock</span>
            )}
          </div>

          {product.description && (
            <p className="text-sm text-gray-600 leading-relaxed mt-4">{product.description}</p>
          )}

          <Button className="mt-6 w-full sm:w-auto sm:px-10 self-start" size="lg" onClick={handleAddToCart} disabled={product.stock === 0}>
            <ShoppingCart className="h-4 w-4" />
            {product.stock === 0 ? "Out of stock" : "Add to cart"}
          </Button>

          <div className="grid sm:grid-cols-3 gap-3 mt-6">
            {product.shipping_information && (
              <InfoTile icon={<Truck className="h-4 w-4" />} label="Shipping" value={product.shipping_information} />
            )}
            {product.warranty_information && (
              <InfoTile icon={<ShieldCheck className="h-4 w-4" />} label="Warranty" value={product.warranty_information} />
            )}
            {product.return_policy && (
              <InfoTile icon={<RotateCcw className="h-4 w-4" />} label="Returns" value={product.return_policy} />
            )}
          </div>
        </div>
      </div>

      {/* Reviews */}
      <div className="mt-12">
        <h2 className="text-xl font-bold text-gray-900 mb-4">
          Reviews <span className="text-gray-400 font-normal">({reviews.length})</span>
        </h2>
        {reviews.length === 0 ? (
          <p className="text-gray-400 text-sm">No reviews yet.</p>
        ) : (
          <div className="grid sm:grid-cols-2 gap-4">
            {reviews.map((review, i) => (
              <div key={i} className="rounded-xl border border-gray-100 bg-white p-4">
                <div className="flex items-center justify-between">
                  <Stars value={review.rating ?? 0} className="h-3.5 w-3.5" />
                  {review.date && <span className="text-xs text-gray-400">{formatDate(review.date)}</span>}
                </div>
                {review.comment && <p className="text-sm text-gray-700 mt-2">{review.comment}</p>}
                {review.reviewerName && (
                  <p className="text-xs text-gray-400 mt-2">— {review.reviewerName}</p>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function InfoTile({ icon, label, value }: { icon: React.ReactNode; label: string; value: string }) {
  return (
    <div className="rounded-xl border border-gray-100 bg-gray-50/60 p-3">
      <div className="flex items-center gap-1.5 text-gray-500 mb-1">
        {icon}
        <span className="text-xs font-medium uppercase tracking-wide">{label}</span>
      </div>
      <p className="text-xs text-gray-700">{value}</p>
    </div>
  );
}
