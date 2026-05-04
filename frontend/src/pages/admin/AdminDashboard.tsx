import { useState, useEffect } from 'react'
import { Table, Tag, Button, Modal, Input, message, Typography, Space, Tabs, Form, Switch } from 'antd'
import { CheckCircleOutlined, CloseCircleOutlined, LogoutOutlined, PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '../../api/client'
import { clearToken } from './AdminLogin'
import type { EnterpriseApplication, Banner, Skill, Policy, ContactInfo } from '../../types/cms'
const { Title, Text } = Typography
const { TextArea } = Input

/* ── 通用编辑模态框 ── */

function EditModal({
  open, title, initialValues, onOk, onCancel, confirmLoading, children, width,
}: {
  open: boolean
  title: string
  initialValues?: Record<string, any>
  onOk: (values: any) => Promise<void>
  onCancel: () => void
  confirmLoading: boolean
  children: React.ReactNode
  width?: number
}) {
  const [form] = Form.useForm()
  useEffect(() => {
    if (open) {
      form.resetFields()
      if (initialValues) form.setFieldsValue(initialValues)
    }
  }, [open, initialValues, form])
  return (
    <Modal title={title} open={open} onOk={() => form.submit()} onCancel={onCancel} confirmLoading={confirmLoading} destroyOnClose width={width}>
      <Form form={form} layout="vertical" onFinish={onOk}>
        {children}
      </Form>
    </Modal>
  )
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

  const [detailModal, setDetailModal] = useState<EnterpriseApplication | null>(null)
  const [rejectModal, setRejectModal] = useState<{ id: number; open: boolean }>({ id: 0, open: false })
  const [rejectReason, setRejectReason] = useState('')

  const handleApprove = (id: number) => {
    reviewMut.mutate({ id, status: 'approved', reject_reason: '' })
  }

  const confirmReject = () => {
    reviewMut.mutate({
      id: rejectModal.id,
      status: 'rejected',
      reject_reason: rejectReason || '暂不符合入驻条件',
    })
    setRejectModal({ id: 0, open: false })
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
              onClick={(e) => { e.stopPropagation(); handleApprove(r.id) }} loading={reviewMut.isPending}>
              通过
            </Button>
            <Button danger size="small" icon={<CloseCircleOutlined />}
              onClick={(e) => { e.stopPropagation(); setRejectModal({ id: r.id, open: true }) }}>
              拒绝
            </Button>
          </Space>
        ) : null
      ),
    },
  ]

  const detailFields: { label: string; key: keyof EnterpriseApplication }[] = [
    { label: '企业名称', key: 'company_name' },
    { label: '统一信用代码', key: 'credit_code' },
    { label: '行业', key: 'industry' },
    { label: '规模', key: 'scale' },
    { label: '联系人', key: 'contact_name' },
    { label: '手机', key: 'contact_phone' },
    { label: '邮箱', key: 'contact_email' },
    { label: '感兴趣技能', key: 'interested_skills' },
    { label: '需求描述', key: 'requirements' },
    { label: '现有系统', key: 'current_systems' },
    { label: '跟踪代码', key: 'tracking_code' },
    { label: '创建时间', key: 'created_at' },
  ]

  return (
    <div>
      <Table dataSource={apps} columns={columns} rowKey="id" loading={isLoading}
        onRow={(record) => ({
          onClick: () => setDetailModal(record),
          style: { cursor: 'pointer' },
        })}
      />
      <Modal title="申请详情" open={!!detailModal} onCancel={() => setDetailModal(null)} footer={null} width={640}>
        {detailModal && (
          <div>
            {detailFields.map(f => (
              <div key={f.key} style={{ marginBottom: 8, display: 'flex' }}>
                <Text strong style={{ width: 120, flexShrink: 0 }}>{f.label}：</Text>
                <Text>{String(detailModal[f.key] ?? '-')}</Text>
              </div>
            ))}
            {detailModal.status === 'rejected' && detailModal.reject_reason && (
              <div style={{ marginBottom: 8, display: 'flex' }}>
                <Text strong style={{ width: 120, flexShrink: 0 }}>拒绝理由：</Text>
                <Text type="danger">{detailModal.reject_reason}</Text>
              </div>
            )}
          </div>
        )}
      </Modal>
      <Modal title="拒绝理由" open={rejectModal.open} onOk={confirmReject} onCancel={() => setRejectModal({ id: 0, open: false })} confirmLoading={reviewMut.isPending}>
        <TextArea placeholder="请输入拒绝理由" value={rejectReason} onChange={e => setRejectReason(e.target.value)} rows={3} />
      </Modal>
    </div>
  )
}

/* ── Banner 管理 ── */

function BannerPanel() {
  const queryClient = useQueryClient()
  const { data, isLoading } = useQuery<Banner[]>({
    queryKey: ['admin-banners'],
    queryFn: () => api.get('/admin/banners').then(r => r.data),
  })
  const createMut = useMutation({
    mutationFn: (d: any) => api.post('/admin/banners', d),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['admin-banners'] }),
  })
  const updateMut = useMutation({
    mutationFn: ({ id, ...d }: any) => api.put(`/admin/banners/${id}`, d),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['admin-banners'] }),
  })
  const deleteMut = useMutation({
    mutationFn: (id: number) => api.delete(`/admin/banners/${id}`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['admin-banners'] }),
  })

  const [editingRecord, setEditingRecord] = useState<Banner | null>(null)
  const [modalOpen, setModalOpen] = useState(false)

  const isEdit = !!editingRecord
  const modalTitle = isEdit ? '编辑 Banner' : '新增 Banner'

  const handleOpenCreate = () => {
    setEditingRecord(null)
    setModalOpen(true)
  }

  const handleOpenEdit = (r: Banner) => {
    setEditingRecord(r)
    setModalOpen(true)
  }

  const handleSubmit = async (values: any) => {
    if (isEdit) {
      await updateMut.mutateAsync({ id: editingRecord!.id, ...values })
      message.success('Banner 已更新')
    } else {
      await createMut.mutateAsync(values)
      message.success('Banner 已创建')
    }
    setModalOpen(false)
    setEditingRecord(null)
  }

  const columns = [
    { title: '标题', dataIndex: 'title', key: 'title' },
    { title: '副标题', dataIndex: 'subtitle', key: 'subtitle' },
    { title: '按钮文字', dataIndex: 'button_text', key: 'button_text' },
    { title: '排序', dataIndex: 'sort_order', key: 'sort_order' },
    { title: '状态', dataIndex: 'is_active', key: 'is_active', render: (v: boolean) => v ? <Tag color="green">启用</Tag> : <Tag>禁用</Tag> },
    {
      title: '操作', key: 'action',
      render: (_: any, r: Banner) => (
        <Space>
          <Button type="link" size="small" icon={<EditOutlined />} onClick={() => handleOpenEdit(r)}>编辑</Button>
          <Button danger size="small" icon={<DeleteOutlined />} onClick={() => deleteMut.mutate(r.id)} loading={deleteMut.isPending}>删除</Button>
        </Space>
      ),
    },
  ]

  return (
    <div>
      <Button type="primary" icon={<PlusOutlined />} onClick={handleOpenCreate} style={{ marginBottom: 16 }}>新增 Banner</Button>
      <Table dataSource={data} columns={columns} rowKey="id" loading={isLoading} />
      <EditModal
        open={modalOpen}
        title={modalTitle}
        initialValues={editingRecord || undefined}
        onOk={handleSubmit}
        onCancel={() => { setModalOpen(false); setEditingRecord(null) }}
        confirmLoading={createMut.isPending || updateMut.isPending}
      >
        <Form.Item name="title" label="标题" rules={[{ required: true, message: '请输入标题' }]}>
          <Input />
        </Form.Item>
        <Form.Item name="subtitle" label="副标题">
          <Input />
        </Form.Item>
        <Form.Item name="button_text" label="按钮文字">
          <Input />
        </Form.Item>
        <Form.Item name="button_link" label="按钮链接">
          <Input />
        </Form.Item>
        <Form.Item name="sort_order" label="排序" getValueFromEvent={(e) => Number(e.target.value)}>
          <Input type="number" />
        </Form.Item>
        <Form.Item name="is_active" label="启用" valuePropName="checked">
          <Switch />
        </Form.Item>
      </EditModal>
    </div>
  )
}

/* ── Skill 管理 ── */

function SkillPanel() {
  const queryClient = useQueryClient()
  const { data, isLoading } = useQuery<Skill[]>({
    queryKey: ['admin-skills'],
    queryFn: () => api.get('/admin/skills').then(r => r.data),
  })
  const createMut = useMutation({
    mutationFn: (d: any) => api.post('/admin/skills', d),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['admin-skills'] }),
  })
  const updateMut = useMutation({
    mutationFn: ({ id, ...d }: any) => api.put(`/admin/skills/${id}`, d),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['admin-skills'] }),
  })
  const deleteMut = useMutation({
    mutationFn: (id: number) => api.delete(`/admin/skills/${id}`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['admin-skills'] }),
  })

  const [editingRecord, setEditingRecord] = useState<Skill | null>(null)
  const [modalOpen, setModalOpen] = useState(false)

  const isEdit = !!editingRecord
  const modalTitle = isEdit ? '编辑 Skill' : '新增 Skill'

  const handleOpenCreate = () => {
    setEditingRecord(null)
    setModalOpen(true)
  }

  const handleOpenEdit = (r: Skill) => {
    setEditingRecord(r)
    setModalOpen(true)
  }

  const handleSubmit = async (values: any) => {
    if (isEdit) {
      await updateMut.mutateAsync({ id: editingRecord!.id, ...values })
      message.success('Skill 已更新')
    } else {
      await createMut.mutateAsync(values)
      message.success('Skill 已创建')
    }
    setModalOpen(false)
    setEditingRecord(null)
  }

  const columns = [
    { title: '标识', dataIndex: 'key', key: 'key' },
    { title: '名称', dataIndex: 'name', key: 'name' },
    { title: '一句话描述', dataIndex: 'summary', key: 'summary', ellipsis: true },
    { title: '排序', dataIndex: 'sort_order', key: 'sort_order' },
    { title: '状态', dataIndex: 'is_active', key: 'is_active', render: (v: boolean) => v ? <Tag color="green">启用</Tag> : <Tag>禁用</Tag> },
    {
      title: '操作', key: 'action',
      render: (_: any, r: Skill) => (
        <Space>
          <Button type="link" size="small" icon={<EditOutlined />} onClick={() => handleOpenEdit(r)}>编辑</Button>
          <Button danger size="small" icon={<DeleteOutlined />} onClick={() => deleteMut.mutate(r.id)} loading={deleteMut.isPending}>删除</Button>
        </Space>
      ),
    },
  ]

  return (
    <div>
      <Button type="primary" icon={<PlusOutlined />} onClick={handleOpenCreate} style={{ marginBottom: 16 }}>新增 Skill</Button>
      <Table dataSource={data} columns={columns} rowKey="id" loading={isLoading} />
      <EditModal
        open={modalOpen}
        title={modalTitle}
        initialValues={editingRecord || undefined}
        onOk={handleSubmit}
        onCancel={() => { setModalOpen(false); setEditingRecord(null) }}
        confirmLoading={createMut.isPending || updateMut.isPending}
        width={640}
      >
        <Form.Item name="key" label="标识" rules={[{ required: true, message: '请输入标识' }]}>
          <Input />
        </Form.Item>
        <Form.Item name="name" label="名称" rules={[{ required: true, message: '请输入名称' }]}>
          <Input />
        </Form.Item>
        <Form.Item name="icon" label="图标">
          <Input />
        </Form.Item>
        <Form.Item name="summary" label="一句话描述" rules={[{ required: true, message: '请输入描述' }]}>
          <Input />
        </Form.Item>
        <Form.Item name="description" label="详细描述">
          <TextArea rows={3} />
        </Form.Item>
        <Form.Item name="scenarios" label="适用场景">
          <TextArea rows={2} />
        </Form.Item>
        <Form.Item name="capabilities" label="能力说明">
          <TextArea rows={2} />
        </Form.Item>
        <Form.Item name="platforms" label="支持平台">
          <Input />
        </Form.Item>
        <Form.Item name="sort_order" label="排序" getValueFromEvent={(e) => Number(e.target.value)}>
          <Input type="number" />
        </Form.Item>
        <Form.Item name="is_active" label="启用" valuePropName="checked">
          <Switch />
        </Form.Item>
      </EditModal>
    </div>
  )
}

/* ── Policy 管理 ── */

function PolicyPanel() {
  const queryClient = useQueryClient()
  const { data, isLoading } = useQuery<Policy[]>({
    queryKey: ['admin-policies'],
    queryFn: () => api.get('/admin/policies').then(r => r.data),
  })
  const createMut = useMutation({
    mutationFn: (d: any) => api.post('/admin/policies', d),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['admin-policies'] }),
  })
  const updateMut = useMutation({
    mutationFn: ({ id, ...d }: any) => api.put(`/admin/policies/${id}`, d),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['admin-policies'] }),
  })
  const deleteMut = useMutation({
    mutationFn: (id: number) => api.delete(`/admin/policies/${id}`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['admin-policies'] }),
  })

  const [editingRecord, setEditingRecord] = useState<Policy | null>(null)
  const [modalOpen, setModalOpen] = useState(false)

  const isEdit = !!editingRecord
  const modalTitle = isEdit ? '编辑政策' : '新增政策'

  const handleOpenCreate = () => {
    setEditingRecord(null)
    setModalOpen(true)
  }

  const handleOpenEdit = (r: Policy) => {
    setEditingRecord(r)
    setModalOpen(true)
  }

  const handleSubmit = async (values: any) => {
    if (isEdit) {
      await updateMut.mutateAsync({ id: editingRecord!.id, ...values })
      message.success('政策已更新')
    } else {
      await createMut.mutateAsync(values)
      message.success('政策已创建')
    }
    setModalOpen(false)
    setEditingRecord(null)
  }

  const columns = [
    { title: '部门', dataIndex: 'dept', key: 'dept' },
    { title: '文号', dataIndex: 'doc_number', key: 'doc_number' },
    { title: '标题', dataIndex: 'title', key: 'title', ellipsis: true },
    { title: '排序', dataIndex: 'sort_order', key: 'sort_order' },
    { title: '状态', dataIndex: 'is_active', key: 'is_active', render: (v: boolean) => v ? <Tag color="green">启用</Tag> : <Tag>禁用</Tag> },
    {
      title: '操作', key: 'action',
      render: (_: any, r: Policy) => (
        <Space>
          <Button type="link" size="small" icon={<EditOutlined />} onClick={() => handleOpenEdit(r)}>编辑</Button>
          <Button danger size="small" icon={<DeleteOutlined />} onClick={() => deleteMut.mutate(r.id)} loading={deleteMut.isPending}>删除</Button>
        </Space>
      ),
    },
  ]

  return (
    <div>
      <Button type="primary" icon={<PlusOutlined />} onClick={handleOpenCreate} style={{ marginBottom: 16 }}>新增政策</Button>
      <Table dataSource={data} columns={columns} rowKey="id" loading={isLoading} />
      <EditModal
        open={modalOpen}
        title={modalTitle}
        initialValues={editingRecord || undefined}
        onOk={handleSubmit}
        onCancel={() => { setModalOpen(false); setEditingRecord(null) }}
        confirmLoading={createMut.isPending || updateMut.isPending}
      >
        <Form.Item name="dept" label="部门" rules={[{ required: true, message: '请输入部门' }]}>
          <Input />
        </Form.Item>
        <Form.Item name="doc_number" label="文号">
          <Input />
        </Form.Item>
        <Form.Item name="title" label="标题" rules={[{ required: true, message: '请输入标题' }]}>
          <Input />
        </Form.Item>
        <Form.Item name="description" label="描述">
          <TextArea rows={3} />
        </Form.Item>
        <Form.Item name="sort_order" label="排序" getValueFromEvent={(e) => Number(e.target.value)}>
          <Input type="number" />
        </Form.Item>
        <Form.Item name="is_active" label="启用" valuePropName="checked">
          <Switch />
        </Form.Item>
      </EditModal>
    </div>
  )
}

/* ── Contact 管理 ── */

function ContactPanel() {
  const queryClient = useQueryClient()
  const { data, isLoading } = useQuery<ContactInfo[]>({
    queryKey: ['admin-contacts'],
    queryFn: () => api.get('/admin/contacts').then(r => r.data),
  })
  const createMut = useMutation({
    mutationFn: (d: any) => api.post('/admin/contacts', d),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['admin-contacts'] }),
  })
  const updateMut = useMutation({
    mutationFn: ({ id, ...d }: any) => api.put(`/admin/contacts/${id}`, d),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['admin-contacts'] }),
  })
  const deleteMut = useMutation({
    mutationFn: (id: number) => api.delete(`/admin/contacts/${id}`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['admin-contacts'] }),
  })

  const [editingRecord, setEditingRecord] = useState<ContactInfo | null>(null)
  const [modalOpen, setModalOpen] = useState(false)

  const isEdit = !!editingRecord
  const modalTitle = isEdit ? '编辑联系方式' : '新增联系方式'

  const handleOpenCreate = () => {
    setEditingRecord(null)
    setModalOpen(true)
  }

  const handleOpenEdit = (r: ContactInfo) => {
    setEditingRecord(r)
    setModalOpen(true)
  }

  const handleSubmit = async (values: any) => {
    if (isEdit) {
      await updateMut.mutateAsync({ id: editingRecord!.id, ...values })
      message.success('联系方式已更新')
    } else {
      await createMut.mutateAsync(values)
      message.success('联系方式已创建')
    }
    setModalOpen(false)
    setEditingRecord(null)
  }

  const columns = [
    { title: '类型', dataIndex: 'type', key: 'type' },
    { title: '标签', dataIndex: 'label', key: 'label' },
    { title: '值', dataIndex: 'value', key: 'value', ellipsis: true },
    { title: '排序', dataIndex: 'display_order', key: 'display_order' },
    {
      title: '操作', key: 'action',
      render: (_: any, r: ContactInfo) => (
        <Space>
          <Button type="link" size="small" icon={<EditOutlined />} onClick={() => handleOpenEdit(r)}>编辑</Button>
          <Button danger size="small" icon={<DeleteOutlined />} onClick={() => deleteMut.mutate(r.id)} loading={deleteMut.isPending}>删除</Button>
        </Space>
      ),
    },
  ]

  return (
    <div>
      <Button type="primary" icon={<PlusOutlined />} onClick={handleOpenCreate} style={{ marginBottom: 16 }}>新增联系方式</Button>
      <Table dataSource={data} columns={columns} rowKey="id" loading={isLoading} />
      <EditModal
        open={modalOpen}
        title={modalTitle}
        initialValues={editingRecord || undefined}
        onOk={handleSubmit}
        onCancel={() => { setModalOpen(false); setEditingRecord(null) }}
        confirmLoading={createMut.isPending || updateMut.isPending}
      >
        <Form.Item name="type" label="类型" rules={[{ required: true, message: '请输入类型' }]}>
          <Input />
        </Form.Item>
        <Form.Item name="label" label="标签" rules={[{ required: true, message: '请输入标签' }]}>
          <Input />
        </Form.Item>
        <Form.Item name="value" label="值" rules={[{ required: true, message: '请输入值' }]}>
          <Input />
        </Form.Item>
        <Form.Item name="display_order" label="排序" getValueFromEvent={(e) => Number(e.target.value)}>
          <Input type="number" />
        </Form.Item>
      </EditModal>
    </div>
  )
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
    { key: 'policies', label: '政策管理', children: <PolicyPanel /> },
    { key: 'contacts', label: '联系方式管理', children: <ContactPanel /> },
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
