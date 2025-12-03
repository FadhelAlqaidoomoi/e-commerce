"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { User, Package, MapPin, LogOut } from "lucide-react";

import { useAuthStore } from "@/lib/store";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";

export default function AccountPage() {
  const router = useRouter();
  const { user, partner, isAuthenticated, logout } = useAuthStore();

  useEffect(() => {
    if (!isAuthenticated) {
      router.push("/login?redirect=/account");
    }
  }, [isAuthenticated, router]);

  const handleLogout = async () => {
    await logout();
    router.push("/");
  };

  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="container py-8">
      <h1 className="text-3xl font-bold tracking-tight mb-8">My Account</h1>

      <div className="grid md:grid-cols-3 gap-8">
        {/* Sidebar */}
        <div className="space-y-4">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center gap-4">
                <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center">
                  <User className="w-8 h-8 text-primary" />
                </div>
                <div>
                  <h2 className="font-semibold">{user?.name || partner?.name}</h2>
                  <p className="text-sm text-muted-foreground">{user?.email || partner?.email}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <nav className="space-y-1">
            <Link
              href="/account"
              className="flex items-center gap-3 px-4 py-2 rounded-md bg-muted font-medium"
            >
              <User className="w-4 h-4" />
              Profile
            </Link>
            <Link
              href="/account/orders"
              className="flex items-center gap-3 px-4 py-2 rounded-md hover:bg-muted transition-colors"
            >
              <Package className="w-4 h-4" />
              Orders
            </Link>
            <Link
              href="/account/addresses"
              className="flex items-center gap-3 px-4 py-2 rounded-md hover:bg-muted transition-colors"
            >
              <MapPin className="w-4 h-4" />
              Addresses
            </Link>
            <button
              onClick={handleLogout}
              className="w-full flex items-center gap-3 px-4 py-2 rounded-md hover:bg-muted transition-colors text-left text-destructive"
            >
              <LogOut className="w-4 h-4" />
              Sign Out
            </button>
          </nav>
        </div>

        {/* Main Content */}
        <div className="md:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle>Profile Information</CardTitle>
              <CardDescription>Your personal details</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid sm:grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium text-muted-foreground">
                    Full Name
                  </label>
                  <p className="mt-1">{user?.name || partner?.name || "-"}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-muted-foreground">
                    Email
                  </label>
                  <p className="mt-1">{user?.email || partner?.email || "-"}</p>
                </div>
              </div>

              <Separator />

              <div className="grid sm:grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium text-muted-foreground">
                    Phone
                  </label>
                  <p className="mt-1">{partner?.phone || "-"}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-muted-foreground">
                    Mobile
                  </label>
                  <p className="mt-1">{partner?.mobile || "-"}</p>
                </div>
              </div>

              {partner?.whatsapp_number && (
                <>
                  <Separator />
                  <div>
                    <label className="text-sm font-medium text-muted-foreground">
                      WhatsApp
                    </label>
                    <p className="mt-1">{partner.whatsapp_number}</p>
                    {partner.whatsapp_opt_in && (
                      <p className="text-xs text-green-600 mt-1">
                        ✓ Opted in for WhatsApp messages
                      </p>
                    )}
                  </div>
                </>
              )}

              <Separator />

              <div>
                <label className="text-sm font-medium text-muted-foreground">
                  Default Address
                </label>
                {partner?.street ? (
                  <p className="mt-1">
                    {partner.street}
                    {partner.street2 && `, ${partner.street2}`}
                    <br />
                    {partner.city}
                    {partner.state && `, ${partner.state.name}`}
                    {partner.zip && ` ${partner.zip}`}
                    <br />
                    {partner.country?.name}
                  </p>
                ) : (
                  <p className="mt-1 text-muted-foreground">No address saved</p>
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
