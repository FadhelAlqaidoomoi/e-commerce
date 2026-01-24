"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { ChevronLeft, Loader2 } from "lucide-react";

import { useAuthStore, useCartStore } from "@/lib/store";
import { odooApi } from "@/lib/api";
import { formatCurrency } from "@/lib/utils";
import { Address, AddressInput } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

export default function CheckoutPage() {
  const router = useRouter();
  const { user, partner, isAuthenticated } = useAuthStore();
  const { cart, clearCart } = useCartStore();

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [addresses, setAddresses] = useState<Address[]>([]);
  const [selectedAddressId, setSelectedAddressId] = useState<string>("");
  const [useNewAddress, setUseNewAddress] = useState(false);
  const [newAddress, setNewAddress] = useState({
    name: "",
    street: "",
    street2: "",
    city: "",
    zip: "",
    phone: "",
    country_id: 0,
    state_id: 0,
  });
  const [notes, setNotes] = useState("");

  useEffect(() => {
    if (!isAuthenticated) {
      router.push("/login?redirect=/checkout");
      return;
    }

    if (!cart || cart.lines.length === 0) {
      router.push("/cart");
      return;
    }

    // Fetch saved addresses
    const partnerAddresses = partner?.addresses;
    if (partnerAddresses && partnerAddresses.length > 0) {
      setAddresses(partnerAddresses);
      const firstAddress = partnerAddresses[0];
      if (firstAddress) {
        setSelectedAddressId(firstAddress.id.toString());
      }
    } else {
      setUseNewAddress(true);
    }
  }, [isAuthenticated, cart, partner, router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);

    try {
      let shippingAddressId: number | undefined;

      if (useNewAddress) {
        // Create new address first
        const addressResponse = await odooApi.addAddress(newAddress);
        if (!addressResponse.success || !addressResponse.data) {
          throw new Error(addressResponse.message || "Failed to create address");
        }
        shippingAddressId = addressResponse.data.id;
      } else if (selectedAddressId) {
        shippingAddressId = parseInt(selectedAddressId);
      }

      // Get the address details for the order
      const selectedAddress = useNewAddress
        ? newAddress
        : addresses.find(a => a.id === parseInt(selectedAddressId));

      if (!selectedAddress) {
        throw new Error("Please select or create a shipping address");
      }

      // Create the order with the address data
      const orderResponse = await odooApi.createOrder({
        shipping_address: {
          name: selectedAddress.name,
          street: selectedAddress.street,
          street2: 'street2' in selectedAddress ? selectedAddress.street2 : "",
          city: selectedAddress.city,
          zip: 'zip' in selectedAddress ? selectedAddress.zip || "" : "",
          phone: 'phone' in selectedAddress ? selectedAddress.phone || "" : "",
          country_id: 'country_id' in selectedAddress ? selectedAddress.country_id : (selectedAddress.country?.id || 0),
          email: user?.email || partner?.email || "",
        },
        use_same_address: true,
        ...(notes ? { note: notes } : {}),
      });

      if (!orderResponse.success || !orderResponse.data) {
        throw new Error(orderResponse.message || "Failed to create order");
      }

      // Clear cart and redirect to order confirmation
      clearCart();
      router.push(`/account/orders/${orderResponse.data.id}?new=true`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!isAuthenticated || !cart || cart.lines.length === 0) {
    return (
      <div className="container py-8">
        <div className="flex items-center justify-center min-h-[400px]">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        </div>
      </div>
    );
  }

  return (
    <div className="container py-8">
      {/* Breadcrumb */}
      <nav className="mb-6">
        <Link
          href="/cart"
          className="inline-flex items-center text-sm text-muted-foreground hover:text-foreground transition-colors"
        >
          <ChevronLeft className="h-4 w-4 mr-1" />
          Back to Cart
        </Link>
      </nav>

      <h1 className="text-3xl font-bold tracking-tight mb-8">Checkout</h1>

      {error && (
        <div className="bg-destructive/10 text-destructive px-4 py-3 rounded-md mb-6">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit}>
        <div className="grid lg:grid-cols-3 gap-8">
          {/* Checkout Form */}
          <div className="lg:col-span-2 space-y-6">
            {/* Contact Information */}
            <Card>
              <CardHeader>
                <CardTitle>Contact Information</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid sm:grid-cols-2 gap-4">
                  <div>
                    <Label>Name</Label>
                    <Input value={user?.name || partner?.name || ""} disabled />
                  </div>
                  <div>
                    <Label>Email</Label>
                    <Input value={user?.email || partner?.email || ""} disabled />
                  </div>
                </div>
                {partner?.phone && (
                  <div>
                    <Label>Phone</Label>
                    <Input value={partner.phone} disabled />
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Shipping Address */}
            <Card>
              <CardHeader>
                <CardTitle>Shipping Address</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {addresses.length > 0 && (
                  <div className="space-y-3">
                    <div className="flex items-center gap-2">
                      <input
                        type="radio"
                        id="existing-address"
                        name="address-type"
                        checked={!useNewAddress}
                        onChange={() => setUseNewAddress(false)}
                        className="h-4 w-4"
                      />
                      <Label htmlFor="existing-address" className="cursor-pointer">
                        Use existing address
                      </Label>
                    </div>

                    {!useNewAddress && (
                      <Select
                        value={selectedAddressId}
                        onValueChange={setSelectedAddressId}
                      >
                        <SelectTrigger>
                          <SelectValue placeholder="Select an address" />
                        </SelectTrigger>
                        <SelectContent>
                          {addresses.map((addr) => (
                            <SelectItem key={addr.id} value={addr.id.toString()}>
                              {addr.name} - {addr.street}, {addr.city}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    )}

                    <Separator />

                    <div className="flex items-center gap-2">
                      <input
                        type="radio"
                        id="new-address"
                        name="address-type"
                        checked={useNewAddress}
                        onChange={() => setUseNewAddress(true)}
                        className="h-4 w-4"
                      />
                      <Label htmlFor="new-address" className="cursor-pointer">
                        Add new address
                      </Label>
                    </div>
                  </div>
                )}

                {(useNewAddress || addresses.length === 0) && (
                  <div className="space-y-4">
                    <div>
                      <Label htmlFor="name">Full Name *</Label>
                      <Input
                        id="name"
                        required
                        value={newAddress.name}
                        onChange={(e) =>
                          setNewAddress({ ...newAddress, name: e.target.value })
                        }
                      />
                    </div>
                    <div>
                      <Label htmlFor="street">Street Address *</Label>
                      <Input
                        id="street"
                        required
                        value={newAddress.street}
                        onChange={(e) =>
                          setNewAddress({ ...newAddress, street: e.target.value })
                        }
                      />
                    </div>
                    <div>
                      <Label htmlFor="street2">Apartment, Suite, etc.</Label>
                      <Input
                        id="street2"
                        value={newAddress.street2}
                        onChange={(e) =>
                          setNewAddress({ ...newAddress, street2: e.target.value })
                        }
                      />
                    </div>
                    <div className="grid sm:grid-cols-2 gap-4">
                      <div>
                        <Label htmlFor="city">City *</Label>
                        <Input
                          id="city"
                          required
                          value={newAddress.city}
                          onChange={(e) =>
                            setNewAddress({ ...newAddress, city: e.target.value })
                          }
                        />
                      </div>
                      <div>
                        <Label htmlFor="zip">ZIP / Postal Code *</Label>
                        <Input
                          id="zip"
                          required
                          value={newAddress.zip}
                          onChange={(e) =>
                            setNewAddress({ ...newAddress, zip: e.target.value })
                          }
                        />
                      </div>
                    </div>
                    <div>
                      <Label htmlFor="phone">Phone</Label>
                      <Input
                        id="phone"
                        type="tel"
                        value={newAddress.phone}
                        onChange={(e) =>
                          setNewAddress({ ...newAddress, phone: e.target.value })
                        }
                      />
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Order Notes */}
            <Card>
              <CardHeader>
                <CardTitle>Order Notes</CardTitle>
              </CardHeader>
              <CardContent>
                <textarea
                  className="w-full min-h-[100px] p-3 border rounded-md resize-none focus:outline-none focus:ring-2 focus:ring-ring"
                  placeholder="Any special instructions for your order..."
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                />
              </CardContent>
            </Card>
          </div>

          {/* Order Summary */}
          <div>
            <Card className="sticky top-24">
              <CardHeader>
                <CardTitle>Order Summary</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* Order Items */}
                <div className="space-y-3">
                  {cart.lines.map((line) => (
                    <div key={line.id} className="flex justify-between text-sm">
                      <span className="text-muted-foreground">
                        {line.product_name} × {line.quantity}
                      </span>
                      <span>{formatCurrency(line.price_subtotal, cart.currency)}</span>
                    </div>
                  ))}
                </div>

                <Separator />

                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Subtotal</span>
                  <span>{formatCurrency(cart.subtotal, cart.currency)}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Tax</span>
                  <span>{formatCurrency(cart.tax_total, cart.currency)}</span>
                </div>

                <Separator />

                <div className="flex justify-between font-semibold text-lg">
                  <span>Total</span>
                  <span>{formatCurrency(cart.total, cart.currency)}</span>
                </div>
              </CardContent>
              <CardFooter>
                <Button
                  type="submit"
                  className="w-full"
                  size="lg"
                  disabled={isSubmitting}
                >
                  {isSubmitting ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Processing...
                    </>
                  ) : (
                    "Place Order"
                  )}
                </Button>
              </CardFooter>
            </Card>
          </div>
        </div>
      </form>
    </div>
  );
}
