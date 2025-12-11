"use client";

import { CheckCircle, ChevronLeft, RotateCcw, ShoppingCart, XCircle } from "lucide-react";
import Image from "next/image";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { Skeleton } from "@/components/ui/skeleton";
import { odooApi } from "@/lib/api";
import { useAuthStore, useCartStore } from "@/lib/store";
import { Order } from "@/lib/types";
import { formatCurrency, formatDate, formatDateTime, getImageUrl, getOrderStatusColor, isLocalImage } from "@/lib/utils";
import { toast } from "sonner";

interface OrderDetailPageProps {
  params: Promise<{ id: string }>;
}

export default function OrderDetailPage({ params }: OrderDetailPageProps) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const isNewOrder = searchParams.get("new") === "true";
  
  const { isAuthenticated } = useAuthStore();
  const { fetchCart } = useCartStore();

  const [order, setOrder] = useState<Order | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [orderId, setOrderId] = useState<number | null>(null);
  const [isRestoring, setIsRestoring] = useState(false);
  const [isReordering, setIsReordering] = useState(false);
  const [isCancelling, setIsCancelling] = useState(false);

  useEffect(() => {
    const getParams = async () => {
      const { id } = await params;
      setOrderId(parseInt(id));
    };
    getParams();
  }, [params]);

  useEffect(() => {
    if (!isAuthenticated) {
      router.push("/login?redirect=/account/orders");
      return;
    }

    if (!orderId) return;

    const fetchOrder = async () => {
      try {
        const response = await odooApi.getOrder(orderId);
        if (response.success && response.data) {
          setOrder(response.data);
        } else {
          setError("Order not found");
        }
      } catch (err) {
        setError("Failed to load order");
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchOrder();
  }, [isAuthenticated, orderId, router]);

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

  const handleRestore = async () => {
    if (!order) return;
    setIsRestoring(true);
    try {
      const response = await odooApi.restoreOrder(order.id);
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
      setIsRestoring(false);
    }
  };

  const handleReorder = async () => {
    if (!order) return;
    setIsReordering(true);
    try {
      const response = await odooApi.reorder(order.id);
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
      setIsReordering(false);
    }
  };

  const handleCancel = async () => {
    if (!order) return;
    if (!confirm("Are you sure you want to cancel this order?")) return;
    
    setIsCancelling(true);
    try {
      const response = await odooApi.cancelOrder(order.id);
      if (response.success) {
        toast.success("Order cancelled");
        setOrder(response.data);
      } else {
        toast.error(response.message || "Failed to cancel order");
      }
    } catch (err) {
      toast.error("Failed to cancel order");
      console.error(err);
    } finally {
      setIsCancelling(false);
    }
  };

  if (isLoading) {
    return (
      <div className="container py-8">
        <Skeleton className="h-6 w-32 mb-6" />
        <Skeleton className="h-10 w-64 mb-8" />
        <div className="grid lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2 space-y-4">
            <Skeleton className="h-48 w-full" />
            <Skeleton className="h-32 w-full" />
          </div>
          <div>
            <Skeleton className="h-64 w-full" />
          </div>
        </div>
      </div>
    );
  }

  if (error || !order) {
    return (
      <div className="container py-8">
        <div className="text-center py-12">
          <p className="text-destructive">{error || "Order not found"}</p>
          <Button asChild variant="outline" className="mt-4">
            <Link href="/account/orders">Back to Orders</Link>
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="container py-8">
      {/* Success Banner */}
      {isNewOrder && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-6 flex items-center gap-3">
          <CheckCircle className="h-6 w-6 text-green-600 shrink-0" />
          <div>
            <p className="font-semibold text-green-800">Order Placed Successfully!</p>
            <p className="text-sm text-green-700">
              Thank you for your order. We&apos;ll process it shortly.
            </p>
          </div>
        </div>
      )}

      {/* Breadcrumb */}
      <nav className="mb-6">
        <Link
          href="/account/orders"
          className="inline-flex items-center text-sm text-muted-foreground hover:text-foreground transition-colors"
        >
          <ChevronLeft className="h-4 w-4 mr-1" />
          Back to Orders
        </Link>
      </nav>

      {/* Order Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start gap-4 mb-8">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Order {order.name}</h1>
          <p className="text-muted-foreground mt-1">
            {order.date_order ? `Placed on ${formatDateTime(order.date_order)}` : `Created on ${formatDateTime(order.create_date)}`}
          </p>
          {order.is_draft && (
            <p className="text-yellow-700 font-medium mt-2">
              This order was not completed. You can restore it to your cart to continue.
            </p>
          )}
        </div>
        <div className="flex items-center gap-3">
          <Badge className={`text-sm ${getOrderStatusColor(order.state)}`}>
            {getStatusLabel(order.state)}
          </Badge>
          {order.can_restore && (
            <Button onClick={handleRestore} disabled={isRestoring}>
              <ShoppingCart className="mr-2 h-4 w-4" />
              {isRestoring ? "Restoring..." : "Continue Order"}
            </Button>
          )}
          {order.can_reorder && (
            <Button variant="outline" onClick={handleReorder} disabled={isReordering}>
              <RotateCcw className="mr-2 h-4 w-4" />
              {isReordering ? "Adding..." : "Reorder"}
            </Button>
          )}
          {order.can_cancel && (
            <Button variant="destructive" onClick={handleCancel} disabled={isCancelling}>
              <XCircle className="mr-2 h-4 w-4" />
              {isCancelling ? "Cancelling..." : "Cancel"}
            </Button>
          )}
        </div>
      </div>

      <div className="grid lg:grid-cols-3 gap-8">
        {/* Order Items */}
        <div className="lg:col-span-2 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Order Items</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="divide-y">
                {order.lines?.map((line) => (
                  <div key={line.id} className="flex gap-4 py-4 first:pt-0 last:pb-0">
                    <div className="relative w-20 h-20 rounded-md overflow-hidden bg-muted shrink-0">
                      <Image
                        src={getImageUrl(line.image)}
                        alt={line.product_name}
                        fill
                        unoptimized={isLocalImage(getImageUrl(line.image))}
                        className="object-cover"
                        sizes="80px"
                      />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="font-medium">{line.product_name}</p>
                      <p className="text-sm text-muted-foreground mt-1">
                        Qty: {line.quantity} × {formatCurrency(line.price_unit, order.currency)}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="font-semibold">
                        {formatCurrency(line.price_subtotal, order.currency)}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Addresses */}
          <div className="grid sm:grid-cols-2 gap-6">
            {order.shipping_address && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-base">Shipping Address</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="font-medium">{order.shipping_address.name}</p>
                  <p className="text-sm text-muted-foreground mt-1">
                    {order.shipping_address.street}
                    {order.shipping_address.street2 && <>, {order.shipping_address.street2}</>}
                    <br />
                    {order.shipping_address.city}
                    {order.shipping_address.state && `, ${order.shipping_address.state}`}
                    {order.shipping_address.zip && ` ${order.shipping_address.zip}`}
                    <br />
                    {order.shipping_address.country}
                  </p>
                  {order.shipping_address.phone && (
                    <p className="text-sm text-muted-foreground mt-2">
                      Phone: {order.shipping_address.phone}
                    </p>
                  )}
                </CardContent>
              </Card>
            )}

            {order.invoice_address && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-base">Billing Address</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="font-medium">{order.invoice_address.name}</p>
                  <p className="text-sm text-muted-foreground mt-1">
                    {order.invoice_address.street}
                    {order.invoice_address.street2 && <>, {order.invoice_address.street2}</>}
                    <br />
                    {order.invoice_address.city}
                    {order.invoice_address.state && `, ${order.invoice_address.state}`}
                    {order.invoice_address.zip && ` ${order.invoice_address.zip}`}
                    <br />
                    {order.invoice_address.country}
                  </p>
                </CardContent>
              </Card>
            )}
          </div>

          {/* Notes */}
          {order.note && (
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Order Notes</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">{order.note}</p>
              </CardContent>
            </Card>
          )}
        </div>

        {/* Order Summary */}
        <div>
          <Card className="sticky top-24">
            <CardHeader>
              <CardTitle>Order Summary</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Subtotal</span>
                <span>{formatCurrency(order.subtotal, order.currency)}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Tax</span>
                <span>{formatCurrency(order.tax_total, order.currency)}</span>
              </div>

              <Separator />

              <div className="flex justify-between font-semibold text-lg">
                <span>Total</span>
                <span>{formatCurrency(order.total, order.currency)}</span>
              </div>

              <Separator />

              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Order Number</span>
                  <span>{order.name}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Order Date</span>
                  <span>{formatDate(order.date_order)}</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
