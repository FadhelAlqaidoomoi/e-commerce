import { notFound } from "next/navigation";
import { OdooApiClient } from "@/lib/api";
import { ProductDetail } from "./product-detail";

interface ProductPageProps {
  params: Promise<{
    id: string;
  }>;
}

async function getProduct(id: number) {
  const api = new OdooApiClient();
  try {
    const response = await api.getProduct(id, true);
    return response.data;
  } catch (error) {
    console.error("Failed to fetch product:", error);
    return null;
  }
}

export default async function ProductPage({ params }: ProductPageProps) {
  const { id } = await params;
  const productId = parseInt(id);

  if (isNaN(productId)) {
    notFound();
  }

  const product = await getProduct(productId);

  if (!product) {
    notFound();
  }

  return (
    <div className="container py-8">
      <ProductDetail product={product} />
    </div>
  );
}

export async function generateMetadata({ params }: ProductPageProps) {
  const { id } = await params;
  const productId = parseInt(id);
  
  if (isNaN(productId)) {
    return { title: "Product Not Found" };
  }

  const product = await getProduct(productId);

  if (!product) {
    return { title: "Product Not Found" };
  }

  return {
    title: product.name,
    description: product.description_short,
  };
}
