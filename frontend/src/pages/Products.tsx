import { useEffect, useState, FormEvent } from 'react';
import { Package, Plus, X } from 'lucide-react';
import { Card, CardContent, CardHeader } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { productsApi } from '../services/api';
import { formatDate } from '../lib/utils';
import type { Product, Category } from '../types';
import toast from 'react-hot-toast';

export default function Products() {
  const [products, setProducts] = useState<Product[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [name, setName] = useState('');
  const [sku, setSku] = useState('');
  const [description, setDescription] = useState('');

  const load = () => {
    productsApi.list().then((res) => setProducts(res.data.products || [])).catch(() => {});
    productsApi.categories().then((res) => setCategories(res.data || [])).catch(() => {});
  };

  useEffect(() => { load(); }, []);

  const handleCreate = async (e: FormEvent) => {
    e.preventDefault();
    try {
      await productsApi.create({ name, sku: sku || undefined, description: description || undefined, category_ids: [] });
      toast.success('Product created');
      setShowForm(false);
      setName(''); setSku(''); setDescription('');
      load();
    } catch {
      toast.error('Failed to create product');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Products</h1>
          <p className="text-gray-500 mt-1">Manage your product catalog</p>
        </div>
        <Button onClick={() => setShowForm(true)}>
          <Plus className="w-4 h-4 mr-2" /> Add Product
        </Button>
      </div>

      {/* Create Form */}
      {showForm && (
        <Card>
          <CardHeader>
            <div className="flex justify-between items-center">
              <h3 className="text-sm font-semibold">New Product</h3>
              <button onClick={() => setShowForm(false)} className="text-gray-400 hover:text-gray-600">
                <X className="w-4 h-4" />
              </button>
            </div>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleCreate} className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Input label="Product Name" value={name} onChange={(e) => setName(e.target.value)} required />
              <Input label="SKU" value={sku} onChange={(e) => setSku(e.target.value)} placeholder="Optional" />
              <Input label="Description" value={description} onChange={(e) => setDescription(e.target.value)} placeholder="Optional" />
              <div className="md:col-span-3">
                <Button type="submit">Create Product</Button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}

      {/* Product Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {products.map((product) => (
          <Card key={product.id} className="hover:shadow-md transition-shadow">
            <CardContent className="py-5">
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-brand-50 flex items-center justify-center">
                    <Package className="w-5 h-5 text-brand-600" />
                  </div>
                  <div>
                    <h3 className="text-sm font-semibold text-gray-900">{product.name}</h3>
                    {product.sku && (
                      <p className="text-xs text-gray-500">SKU: {product.sku}</p>
                    )}
                  </div>
                </div>
                <Badge variant={product.is_active ? 'active' : 'closed'}>
                  {product.is_active ? 'Active' : 'Inactive'}
                </Badge>
              </div>
              {product.description && (
                <p className="text-sm text-gray-600 mt-3 line-clamp-2">{product.description}</p>
              )}
              <div className="flex items-center gap-2 mt-3">
                {product.categories.map((cat) => (
                  <span key={cat.id} className="px-2 py-0.5 bg-gray-100 text-gray-600 rounded text-xs">
                    {cat.name}
                  </span>
                ))}
              </div>
              <p className="text-xs text-gray-400 mt-3">Added {formatDate(product.created_at)}</p>
            </CardContent>
          </Card>
        ))}
        {products.length === 0 && (
          <div className="col-span-full text-center py-16">
            <Package className="w-10 h-10 text-gray-300 mx-auto mb-3" />
            <p className="text-sm text-gray-400">No products yet. Add your first product.</p>
          </div>
        )}
      </div>
    </div>
  );
}
