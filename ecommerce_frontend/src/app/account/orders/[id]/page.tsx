"use client";

import { CheckCircle, ChevronLeft } from "lucide-react";
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
import { useAuthStore } from "@/lib/store";
import { Order } from "@/lib/types";
import { formatCurrency, formatDate, formatDateTime, getOrderStatusColor, getPlaceholderImage, isLocalImage } from "@/lib/utils";

interface OrderDetailPageProps {
  params: Promise<{ id: string }>;
}

export default function OrderDetailPage({ params }: OrderDetailPageProps) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const isNewOrder = searchParams.get("new") === "true";
  
  const { isAuthenticated } = useAuthStore();

  const [order, setOrder] = useState<Order | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [orderId, setOrderId] = useState<number | null>(null);

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
      draft: "Draft",
      sent: "Quotation Sent",
      sale: "Confirmed",
      done: "Done",
      cancel: "Cancelled",
    };
    return labels[state] || state;
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
            Placed on {formatDateTime(order.date_order)}
          </p>
        </div>
        <Badge className={`text-sm ${getOrderStatusColor(order.state)}`}>
          {getStatusLabel(order.state)}
        </Badge>
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
                        src={line.image || getPlaceholderImage(80, 80)}
                        alt={line.product_name}
                        fill
                        unoptimized={isLocalImage(line.image)}
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
            {order.partner_shipping && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-base">Shipping Address</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="font-medium">{order.partner_shipping.name}</p>
                  <p className="text-sm text-muted-foreground mt-1">
                    {order.partner_shipping.street}
                    {order.partner_shipping.street2 && <>, {order.partner_shipping.street2}</>}
                    <br />
                    {order.partner_shipping.city}
                    {order.partner_shipping.state && `, ${order.partner_shipping.state.name}`}
                    {order.partner_shipping.zip && ` ${order.partner_shipping.zip}`}
                    <br />
                    {order.partner_shipping.country?.name}
                  </p>
                  {order.partner_shipping.phone && (
                    <p className="text-sm text-muted-foreground mt-2">
                      Phone: {order.partner_shipping.phone}
                    </p>
                  )}
                </CardContent>
              </Card>
            )}

            {order.partner_invoice && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-base">Billing Address</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="font-medium">{order.partner_invoice.name}</p>
                  <p className="text-sm text-muted-foreground mt-1">
                    {order.partner_invoice.street}
                    {order.partner_invoice.street2 && <>, {order.partner_invoice.street2}</>}
                    <br />
                    {order.partner_invoice.city}
                    {order.partner_invoice.state && `, ${order.partner_invoice.state.name}`}
                    {order.partner_invoice.zip && ` ${order.partner_invoice.zip}`}
                    <br />
                    {order.partner_invoice.country?.name}
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
                <span>{formatCurrency(order.amount_untaxed, order.currency)}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Tax</span>
                <span>{formatCurrency(order.amount_tax, order.currency)}</span>
              </div>

              <Separator />

              <div className="flex justify-between font-semibold text-lg">
                <span>Total</span>
                <span>{formatCurrency(order.amount_total, order.currency)}</span>
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
