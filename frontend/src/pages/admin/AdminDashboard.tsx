import { useState } from 'react'
import { Table, Tag, Button, Modal, Select, Input, message, Typography, Space, Tabs } from 'antd'
import { CheckCircleOutlined, CloseCircleOutlined, LogoutOutlined } from '@ant-design/icons'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '../../api/client'
import { clearToken } from './AdminLogin'
import type { EnterpriseApplication, Banner, Skill, Policy, ContactInfo } from '../../types/cms'

const { TextArea } = Input
const { Title } = Typography

/* ── 通用 API hooks ── */

function useAdminAPI<T>(key: string, url: string) {
  return {
    list: () => useQuery<T[]>({ queryKey: [key], queryFn: () => api.get(url).then(r => r.data) }),
    create: (queryClient: any) => useMutation({
      mutationFn: (data: any) => api.post(url, data).then(r => r.data),
      onSuccess: () => queryClient.invalidateQueries({ queryKey: [key] }),
    }),
    update: (queryClient: any) => useMutation({
      mutationFn: ({ id, ...data }: any) => api.put(`${url}/${id}`, data).then(r => r.data),
      onSuccess: () => queryClient.invalidateQueries({ queryKey: [key] }),
    }),
    remove: (queryClient: any) => useMutation({
      mutationFn: (id: number) => api.delete(`${url}/${id}`),
      onSuccess: () => queryClient.invalidateQueries({ queryKey: [key] }),
    }),
  }
}

/* ── 入驻审核面板 ── */

function ApplicationPanel() {
  const queryClient = useQueryClient()
  const { data: apps, isLoading } = useQuery<EnterpriseApplication[]>({
    queryKey: ['applications'],
    queryFn: () => api.get('/admin/applications').then(r => r.data),
  })
  const reviewMut = useMutation({
    mutationFn: ({ id, status, reject_reason }: any) =>
      api.put(`/admin/applications/${id}`, { status, reject_reason }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['applications'] }),
  })

  const handleReview = (id: number, status: string) => {
    if (status === 'rejected') {
      // 简单处理：默认拒绝理由
    }
    reviewMut.mutate({ id, status, reject_reason: status === 'rejected' ? '暂不符合入驻条件' : '' })
  }

  const columns = [
    { title: '企业名称', dataIndex: 'company_name', key: 'company_name' },
    { title: '联系人', dataIndex: 'contact_name', key: 'contact_name' },
    { title: '手机', dataIndex: 'contact_phone', key: 'contact_phone' },
    { title: '行业', dataIndex: 'industry', key: 'industry' },
    { title: '规模', dataIndex: 'scale', key: 'scale' },
    {
      title: '状态', dataIndex: 'status', key: 'status',
      render: (s: string) => {
        const colors: Record<string, string> = { pending: 'orange', approved: 'green', rejected: 'red' }
        const labels: Record<string, string> = { pending: '待审核', approved: '已通过', rejected: '已拒绝' }
        return <Tag color={colors[s]}>{labels[s] || s}</Tag>
      },
    },
    {
      title: '操作', key: 'action',
      render: (_: any, r: EnterpriseApplication) => (
        r.status === 'pending' ? (
          <Space>
            <Button type="primary" size="small" icon={<CheckCircleOutlined />}
              onClick={() => handleReview(r.id, 'approved')} loading={reviewMut.isPending}>
              通过
            </Button>
            <Button danger size="small" icon={<CloseCircleOutlined />}
              onClick={() => handleReview(r.id, 'rejected')} loading={reviewMut.isPending}>
              拒绝
            </Button>
          </Space>
        ) : null
      ),
    },
  ]

  return <Table dataSource={apps} columns={columns} rowKey="id" loading={isLoading} />
}

/* ── Banner 管理 ── */

function BannerPanel() {
  const queryClient = useQueryClient()
  const { data, isLoading } = useQuery<Banner[]>({ queryKey: ['admin-banners'], queryFn: () => api.get('/admin/banners').then(r => r.data) })
  const createMut = useMutation({ mutationFn: (d: any) => api.post('/admin/banners', d), onSuccess: () => queryClient.invalidateQueries({ queryKey: ['admin-banners'] }) })
  const deleteMut = useMutation({ mutationFn: (id: number) => api.delete(`/admin/banners/${id}`), onSuccess: () => queryClient.invalidateQueries({ queryKey: ['admin-banners'] }) })
  const [modalOpen, setModalOpen] = useState(false)
  const [form, setForm] = useState({ title: '', subtitle: '', button_text: '了解更多', button_link: '#apply' })

  const handleCreate = async () => {
    await createMut.mutateAsync(form)
    message.success('Banner 已创建')
    setModalOpen(false)
    setForm({ title: '', subtitle: '', button_text: '了解更多', button_link: '#apply' })
  }

  const columns = [
    { title: '标题', dataIndex: 'title', key: 'title' },
    { title: '副标题', dataIndex: 'subtitle', key: 'subtitle' },
    { title: '按钮文字', dataIndex: 'button_text', key: 'button_text' },
    { title: '排序', dataIndex: 'sort_order', key: 'sort_order' },
    { title: '状态', dataIndex: 'is_active', key: 'is_active', render: (v: boolean) => v ? <Tag color="green">启用</Tag> : <Tag>禁用</Tag> },
    {
      title: '操作', key: 'action',
      render: (_: any, r: Banner) => <Button danger size="small" onClick={() => deleteMut.mutate(r.id)} loading={deleteMut.isPending}>删除</Button>,
    },
  ]

  return (
    <div>
      <Button type="primary" onClick={() => setModalOpen(true)} style={{ marginBottom: 16 }}>新增 Banner</Button>
      <Table dataSource={data} columns={columns} rowKey="id" loading={isLoading} />
      <Modal title="新增 Banner" open={modalOpen} onOk={handleCreate} onCancel={() => setModalOpen(false)} confirmLoading={createMut.isPending}>
        <Input placeholder="标题" value={form.title} onChange={e => setForm({ ...form, title: e.target.value })} style={{ marginBottom: 12 }} />
        <Input placeholder="副标题" value={form.subtitle} onChange={e => setForm({ ...form, subtitle: e.target.value })} style={{ marginBottom: 12 }} />
        <Input placeholder="按钮文字" value={form.button_text} onChange={e => setForm({ ...form, button_text: e.target.value })} style={{ marginBottom: 12 }} />
        <Input placeholder="按钮链接" value={form.button_link} onChange={e => setForm({ ...form, button_link: e.target.value })} />
      </Modal>
    </div>
  )
}

/* ── Skill 管理 ── */

function SkillPanel() {
  const queryClient = useQueryClient()
  const { data, isLoading } = useQuery<Skill[]>({ queryKey: ['admin-skills'], queryFn: () => api.get('/admin/skills').then(r => r.data) })
  const deleteMut = useMutation({ mutationFn: (id: number) => api.delete(`/admin/skills/${id}`), onSuccess: () => queryClient.invalidateQueries({ queryKey: ['admin-skills'] }) })
  const columns = [
    { title: '标识', dataIndex: 'key', key: 'key' },
    { title: '名称', dataIndex: 'name', key: 'name' },
    { title: '一句话描述', dataIndex: 'summary', key: 'summary', ellipsis: true },
    { title: '排序', dataIndex: 'sort_order', key: 'sort_order' },
    { title: '状态', dataIndex: 'is_active', key: 'is_active', render: (v: boolean) => v ? <Tag color="green">启用</Tag> : <Tag>禁用</Tag> },
    {
      title: '操作', key: 'action',
      render: (_: any, r: Skill) => <Button danger size="small" onClick={() => deleteMut.mutate(r.id)} loading={deleteMut.isPending}>删除</Button>,
    },
  ]
  return <Table dataSource={data} columns={columns} rowKey="id" loading={isLoading} />
}

/* ── 主布局 ── */

export default function AdminDashboard() {
  const handleLogout = () => {
    clearToken()
    window.location.reload()
  }

  const items = [
    { key: 'applications', label: '入驻审核', children: <ApplicationPanel /> },
    { key: 'banners', label: 'Banner 管理', children: <BannerPanel /> },
    { key: 'skills', label: 'Skill 管理', children: <SkillPanel /> },
  ]

  return (
    <div style={{ padding: 24 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <Title level={3}>管理后台</Title>
        <Button icon={<LogoutOutlined />} onClick={handleLogout}>退出</Button>
      </div>
      <Tabs items={items} />
    </div>
  )
}
