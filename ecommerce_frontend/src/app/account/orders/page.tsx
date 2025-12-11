"use client";

import { ChevronLeft, Eye, Package, RotateCcw, ShoppingCart } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { odooApi } from "@/lib/api";
import { useAuthStore, useCartStore } from "@/lib/store";
import { Order } from "@/lib/types";
import { formatCurrency, formatDate, getOrderStatusColor } from "@/lib/utils";
import { toast } from "sonner";

export default function OrdersPage() {
  const router = useRouter();
  const { isAuthenticated } = useAuthStore();
  const { fetchCart } = useCartStore();

  const [orders, setOrders] = useState<Order[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [restoringId, setRestoringId] = useState<number | null>(null);
  const [reorderingId, setReorderingId] = useState<number | null>(null);

  useEffect(() => {
    if (!isAuthenticated) {
      router.push("/login?redirect=/account/orders");
      return;
    }

    const fetchOrders = async () => {
      try {
        const response = await odooApi.getOrders();
        console.log('Orders API response:', response);
        if (response.success && response.data) {
          setOrders(response.data.orders || []);
        } else {
          setError(response.message || "Failed to load orders");
        }
      } catch (err) {
        setError("Failed to load orders");
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchOrders();
  }, [isAuthenticated, router]);

  if (!isAuthenticated) {
    return null;
  }

  const getStatusLabel = (state: string) => {
    const labels: Record<string, string> = {
      draft: "Incomplete",
      sent: "Quotation Sent",
      sale: "Confirmed",
      done: "Done",
      cancel: "Cancelled",
    };
    return labels[state] || state;
  };

  const handleRestore = async (orderId: number) => {
    setRestoringId(orderId);
    try {
      const response = await odooApi.restoreOrder(orderId);
      if (response.success) {
        toast.success("Order restored to cart");
        await fetchCart();
        router.push("/cart");
      } else {
        toast.error(response.message || "Failed to restore order");
      }
    } catch (err) {
      toast.error("Failed to restore order");
      console.error(err);
    } finally {
      setRestoringId(null);
    }
  };

  const handleReorder = async (orderId: number) => {
    setReorderingId(orderId);
    try {
      const response = await odooApi.reorder(orderId);
      if (response.success) {
        toast.success("Items added to cart");
        await fetchCart();
        router.push("/cart");
      } else {
        toast.error(response.message || "Failed to reorder");
      }
    } catch (err) {
      toast.error("Failed to reorder");
      console.error(err);
    } finally {
      setReorderingId(null);
    }
  };

  return (
    <div className="container py-8">
      {/* Breadcrumb */}
      <nav className="mb-6">
        <Link
          href="/account"
          className="inline-flex items-center text-sm text-muted-foreground hover:text-foreground transition-colors"
        >
          <ChevronLeft className="h-4 w-4 mr-1" />
          Back to Account
        </Link>
      </nav>

      <h1 className="text-3xl font-bold tracking-tight mb-8">My Orders</h1>

      {isLoading ? (
        <div className="space-y-4">
          {Array.from({ length: 3 }).map((_, i) => (
            <Card key={i}>
              <CardContent className="p-6">
                <div className="flex justify-between items-start">
                  <div className="space-y-2">
                    <Skeleton className="h-5 w-32" />
                    <Skeleton className="h-4 w-48" />
                  </div>
                  <Skeleton className="h-6 w-20" />
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : error ? (
        <div className="text-center py-12">
          <p className="text-destructive">{error}</p>
          <Button
            variant="outline"
            className="mt-4"
            onClick={() => window.location.reload()}
          >
            Try Again
          </Button>
        </div>
      ) : orders.length === 0 ? (
        <div className="text-center py-12">
          <Package className="mx-auto h-16 w-16 text-muted-foreground mb-4" />
          <h2 className="text-xl font-semibold mb-2">No orders yet</h2>
          <p className="text-muted-foreground mb-6">
            You haven&apos;t placed any orders yet.
          </p>
          <Button asChild>
            <Link href="/shop">Start Shopping</Link>
          </Button>
        </div>
      ) : (
        <div className="space-y-4">
          {orders.map((order) => (
            <Card key={order.id} className={order.is_current_cart ? "border-blue-300 bg-blue-50/50" : order.is_draft ? "border-yellow-300 bg-yellow-50/50" : ""}>
              <CardContent className="p-6">
                <div className="flex flex-col sm:flex-row justify-between gap-4">
                  <div className="space-y-1">
                    <div className="flex items-center gap-3">
                      <h3 className="font-semibold">Order {order.name}</h3>
                      <Badge className={getOrderStatusColor(order.state)}>
                        {getStatusLabel(order.state)}
                      </Badge>
                      {order.is_current_cart && (
                        <Badge variant="outline" className="border-blue-500 text-blue-600">
                          Current Cart
                        </Badge>
                      )}
                    </div>
                    <p className="text-sm text-muted-foreground">
                      {order.date_order ? `Placed on ${formatDate(order.date_order)}` : `Created on ${formatDate(order.create_date)}`}
                    </p>
                    {order.line_count !== undefined && (
                      <p className="text-sm text-muted-foreground">
                        {order.line_count} item{order.line_count !== 1 ? "s" : ""}
                      </p>
                    )}
                    {order.is_current_cart && (
                      <p className="text-sm text-blue-700 font-medium">
                        This is your active shopping cart
                      </p>
                    )}
                    {order.is_draft && !order.is_current_cart && (
                      <p className="text-sm text-yellow-700 font-medium">
                        This order was not completed
                      </p>
                    )}
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="text-right">
                      <p className="font-semibold text-lg">
                        {formatCurrency(order.total, order.currency)}
                      </p>
                    </div>
                    <div className="flex gap-2">
                      {order.is_current_cart && (
                        <Button asChild variant="default" size="sm">
                          <Link href="/cart">
                            <ShoppingCart className="mr-2 h-4 w-4" />
                            Go to Cart
                          </Link>
                        </Button>
                      )}
                      {order.can_restore && (
                        <Button 
                          variant="default" 
                          size="sm"
                          onClick={() => handleRestore(order.id)}
                          disabled={restoringId === order.id}
                        >
                          <ShoppingCart className="mr-2 h-4 w-4" />
                          {restoringId === order.id ? "Restoring..." : "Continue"}
                        </Button>
                      )}
                      {order.can_reorder && (
                        <Button 
                          variant="outline" 
                          size="sm"
                          onClick={() => handleReorder(order.id)}
                          disabled={reorderingId === order.id}
                        >
                          <RotateCcw className="mr-2 h-4 w-4" />
                          {reorderingId === order.id ? "Adding..." : "Reorder"}
                        </Button>
                      )}
                      <Button asChild variant="outline" size="sm">
                        <Link href={`/account/orders/${order.id}`}>
                          <Eye className="mr-2 h-4 w-4" />
                          View
                        </Link>
                      </Button>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
