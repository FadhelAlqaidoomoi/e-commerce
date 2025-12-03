"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { ChevronLeft, Package, Eye } from "lucide-react";

import { useAuthStore } from "@/lib/store";
import { odooApi } from "@/lib/api";
import { Order } from "@/lib/types";
import { formatCurrency, formatDate, getOrderStatusColor } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";

export default function OrdersPage() {
  const router = useRouter();
  const { isAuthenticated } = useAuthStore();

  const [orders, setOrders] = useState<Order[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!isAuthenticated) {
      router.push("/login?redirect=/account/orders");
      return;
    }

    const fetchOrders = async () => {
      try {
        const response = await odooApi.getOrders();
        if (response.success && response.data) {
          setOrders(response.data.orders || []);
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
      draft: "Draft",
      sent: "Quotation Sent",
      sale: "Confirmed",
      done: "Done",
      cancel: "Cancelled",
    };
    return labels[state] || state;
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
            <Card key={order.id}>
              <CardContent className="p-6">
                <div className="flex flex-col sm:flex-row justify-between gap-4">
                  <div className="space-y-1">
                    <div className="flex items-center gap-3">
                      <h3 className="font-semibold">Order {order.name}</h3>
                      <Badge className={getOrderStatusColor(order.state)}>
                        {getStatusLabel(order.state)}
                      </Badge>
                    </div>
                    <p className="text-sm text-muted-foreground">
                      Placed on {formatDate(order.date_order)}
                    </p>
                    {order.lines && (
                      <p className="text-sm text-muted-foreground">
                        {order.lines.length} item{order.lines.length !== 1 ? "s" : ""}
                      </p>
                    )}
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="text-right">
                      <p className="font-semibold text-lg">
                        {formatCurrency(order.amount_total, order.currency)}
                      </p>
                    </div>
                    <Button asChild variant="outline" size="sm">
                      <Link href={`/account/orders/${order.id}`}>
                        <Eye className="mr-2 h-4 w-4" />
                        View
                      </Link>
                    </Button>
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
