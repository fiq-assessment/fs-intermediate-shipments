'use client';
import { useEffect, useState } from 'react';

const API_BASE = 'http://localhost:4000';

// REQUIREMENTS:
// - Multi-filter UI (status, facility, date range, PO)
// - Inline quantity editing with optimistic updates
// - CSV upload with feedback

export default function ShipmentsPage() {
  const [shipments, setShipments] = useState<any[]>([]);
  const [facilities, setFacilities] = useState<any[]>([]);
  const [filters, setFilters] = useState<any>({});
  const [csvFile, setCsvFile] = useState<File | null>(null);
  const [uploadResult, setUploadResult] = useState<any>(null);

  useEffect(() => {
    fetchFacilities();
    fetchShipments();
  }, [filters]);

  const fetchFacilities = async () => {
    const res = await fetch(`${API_BASE}/facilities`);
    const data = await res.json();
    setFacilities(data.items || []);
  };

  const fetchShipments = async () => {
    const params = new URLSearchParams();
    if (filters.status) params.set('status', filters.status);
    if (filters.facilityId) params.set('facilityId', filters.facilityId);
    if (filters.po) params.set('po', filters.po);
    
    const res = await fetch(`${API_BASE}/shipments?${params}&limit=50`);
    const data = await res.json();
    setShipments(data.items || []);
  };

  const handleCSVUpload = async () => {
    if (!csvFile) return;
    
    const formData = new FormData();
    formData.append('file', csvFile);
    
    try {
      const res = await fetch(`${API_BASE}/shipments/import`, {
        method: 'POST',
        body: formData
      });
      const result = await res.json();
      setUploadResult(result);
      if (result.imported > 0) {
        fetchShipments();
      }
    } catch (err) {
      alert('Upload failed');
    }
  };

  return (
    <div style={{ padding: '2rem', maxWidth: '1400px', margin: '0 auto' }}>
      <h1 style={{ fontSize: '2rem', marginBottom: '2rem' }}>Shipments Management</h1>

      {/* CSV Upload */}
      <div style={{ background: 'white', padding: '1.5rem', borderRadius: '8px', marginBottom: '1rem', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
        <h2 style={{ marginBottom: '1rem' }}>CSV Import</h2>
        <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
          <input 
            type="file" 
            accept=".csv"
            onChange={e => setCsvFile(e.target.files?.[0] || null)}
          />
          <button 
            onClick={handleCSVUpload}
            disabled={!csvFile}
            style={{ padding: '0.5rem 1rem', background: '#3b82f6', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer' }}
          >
            Upload
          </button>
        </div>
        {uploadResult && (
          <div style={{ marginTop: '1rem', padding: '0.5rem', background: '#f0fdf4', borderRadius: '4px' }}>
            <p><strong>Imported:</strong> {uploadResult.imported}</p>
            {uploadResult.errors.length > 0 && (
              <details>
                <summary style={{ cursor: 'pointer' }}>Errors ({uploadResult.errors.length})</summary>
                {uploadResult.errors.map((err: string, i: number) => (
                  <div key={i} style={{ fontSize: '0.875rem', color: '#dc2626' }}>{err}</div>
                ))}
              </details>
            )}
          </div>
        )}
      </div>

      {/* Filters */}
      <div style={{ background: 'white', padding: '1.5rem', borderRadius: '8px', marginBottom: '1rem', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
          <div>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 500 }}>Status</label>
            <select 
              value={filters.status || ''}
              onChange={e => setFilters({...filters, status: e.target.value || undefined})}
              style={{ width: '100%', padding: '0.5rem', border: '1px solid #ddd', borderRadius: '6px' }}
            >
              <option value="">All</option>
              <option value="pending">Pending</option>
              <option value="in_transit">In Transit</option>
              <option value="delivered">Delivered</option>
            </select>
          </div>
          
          <div>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 500 }}>Facility</label>
            <select 
              value={filters.facilityId || ''}
              onChange={e => setFilters({...filters, facilityId: e.target.value || undefined})}
              style={{ width: '100%', padding: '0.5rem', border: '1px solid #ddd', borderRadius: '6px' }}
            >
              <option value="">All</option>
              {facilities.map(f => (
                <option key={f.id} value={f.id}>{f.name}</option>
              ))}
            </select>
          </div>
          
          <div>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 500 }}>PO Number</label>
            <input 
              type="text"
              value={filters.po || ''}
              onChange={e => setFilters({...filters, po: e.target.value || undefined})}
              placeholder="Search PO..."
              style={{ width: '100%', padding: '0.5rem', border: '1px solid #ddd', borderRadius: '6px' }}
            />
          </div>
        </div>
      </div>

      {/* Shipments Table */}
      <div style={{ background: 'white', padding: '1.5rem', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
        <h2 style={{ marginBottom: '1rem' }}>Shipments ({shipments.length})</h2>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ borderBottom: '2px solid #eee' }}>
              <th style={{ padding: '0.75rem', textAlign: 'left' }}>PO Number</th>
              <th style={{ padding: '0.75rem', textAlign: 'left' }}>Facility</th>
              <th style={{ padding: '0.75rem', textAlign: 'left' }}>Status</th>
              <th style={{ padding: '0.75rem', textAlign: 'left' }}>Items</th>
              <th style={{ padding: '0.75rem', textAlign: 'left' }}>Created</th>
            </tr>
          </thead>
          <tbody>
            {shipments.map(shipment => (
              <tr key={shipment.id} style={{ borderBottom: '1px solid #eee' }}>
                <td style={{ padding: '0.75rem' }}>{shipment.poNumber}</td>
                <td style={{ padding: '0.75rem' }}>{shipment.facilityName}</td>
                <td style={{ padding: '0.75rem' }}>
                  <span style={{ 
                    padding: '0.25rem 0.5rem', 
                    borderRadius: '4px',
                    background: shipment.status === 'delivered' ? '#d1fae5' : shipment.status === 'in_transit' ? '#fef3c7' : '#f3f4f6',
                    fontSize: '0.875rem'
                  }}>
                    {shipment.status}
                  </span>
                </td>
                <td style={{ padding: '0.75rem' }}>
                  {shipment.items.map((item: any, i: number) => (
                    <div key={i} style={{ fontSize: '0.875rem' }}>
                      {item.productName} × {item.quantity}
                    </div>
                  ))}
                </td>
                <td style={{ padding: '0.75rem', fontSize: '0.875rem', color: '#666' }}>
                  {new Date(shipment.createdAt).toLocaleDateString()}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

