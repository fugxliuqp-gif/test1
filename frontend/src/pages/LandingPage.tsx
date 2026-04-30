import { useState, useMemo, useEffect } from 'react'
import { Form, Input, Select, Button, message, Checkbox } from 'antd'
import { useBanners, useSkills, usePolicies, useContacts, useApply } from '../hooks/useCms'
import '../styles/site.css'

/* ── 工具函数 ── */

function getSkillIcon(key: string) {
  const icons: Record<string, string> = {
    'skill-a': '📂',
    'skill-b': '📤',
    'skill-c': '🛡️',
    'skill-d': '⚙️',
  }
  return icons[key] || '🤖'
}

function getSkillTags(capabilitiesStr?: string): string[] {
  if (!capabilitiesStr) return []
  try {
    const arr = JSON.parse(capabilitiesStr)
    return Array.isArray(arr) ? arr.slice(0, 4) : []
  } catch {
    return capabilitiesStr.split(',').slice(0, 4)
  }
}

/* ── 子组件 ── */

function SkillCard({ skill }: { skill: any }) {
  const tags = getSkillTags(skill.capabilities)
  const [expanded, setExpanded] = useState(false)

  return (
    <div className="skill-card" onClick={() => setExpanded(!expanded)}>
      <span className="skill-icon">{skill.icon || getSkillIcon(skill.key)}</span>
      <div className="skill-name">{skill.name}</div>
      <div className="skill-summary">{skill.summary}</div>
      <div className="skill-tags">
        {tags.map((t, i) => <span key={i} className="skill-tag">{t}</span>)}
      </div>
      {expanded && skill.description && (
        <div style={{ marginTop: 16, paddingTop: 16, borderTop: '1px solid #eee', fontSize: '0.9rem', color: '#666', lineHeight: 1.8 }}>
          {skill.description}
        </div>
      )}
    </div>
  )
}

function ApplySection() {
  const [form] = Form.useForm()
  const apply = useApply()
  const [trackingCode, setTrackingCode] = useState('')
  const [submitted, setSubmitted] = useState(false)

  const handleSubmit = async (values: any) => {
    try {
      const result = await apply.mutateAsync(values)
      setTrackingCode(result.tracking_code)
      setSubmitted(true)
      message.success('申请提交成功！')
    } catch {
      message.error('提交失败，请稍后重试')
    }
  }

  if (submitted) {
    return (
      <div className="apply-success">
        <div style={{ fontSize: '4rem' }}>✅</div>
        <h3>申请已收到！</h3>
        <p>我们将在 1-2 个工作日内与您联系</p>
        <div className="tracking">{trackingCode}</div>
        <p style={{ fontSize: '0.85rem' }}>请保存此查询码，用于查询申请进度</p>
      </div>
    )
  }

  return (
    <Form form={form} layout="vertical" onFinish={handleSubmit} size="large">
      <Form.Item name="company_name" label="企业名称" rules={[{ required: true, message: '请输入企业名称' }]}>
        <Input placeholder="请输入企业全称" />
      </Form.Item>
      <Form.Item name="credit_code" label="统一社会信用代码" rules={[{ required: true, message: '请输入信用代码' }]}>
        <Input placeholder="18 位信用代码" />
      </Form.Item>
      <Form.Item name="industry" label="所属行业" rules={[{ required: true, message: '请选择行业' }]}>
        <Select placeholder="请选择行业">
          <Select.Option value="化工">化工</Select.Option>
          <Select.Option value="制药">制药</Select.Option>
          <Select.Option value="钢铁">钢铁</Select.Option>
          <Select.Option value="食品">食品</Select.Option>
          <Select.Option value="电力">电力</Select.Option>
          <Select.Option value="其他">其他</Select.Option>
        </Select>
      </Form.Item>
      <Form.Item name="scale" label="企业规模" rules={[{ required: true }]}>
        <Select placeholder="请选择规模">
          <Select.Option value="50人以下">50人以下</Select.Option>
          <Select.Option value="50-200人">50-200人</Select.Option>
          <Select.Option value="200-500人">200-500人</Select.Option>
          <Select.Option value="500-1000人">500-1000人</Select.Option>
          <Select.Option value="1000人以上">1000人以上</Select.Option>
        </Select>
      </Form.Item>
      <Form.Item name="contact_name" label="联系人" rules={[{ required: true }]}>
        <Input placeholder="姓名" />
      </Form.Item>
      <Form.Item name="contact_phone" label="手机号" rules={[{ required: true, pattern: /^1\d{10}$/, message: '请输入正确手机号' }]}>
        <Input placeholder="11 位手机号" />
      </Form.Item>
      <Form.Item name="contact_email" label="邮箱" rules={[{ required: true, type: 'email' }]}>
        <Input placeholder="邮箱地址" />
      </Form.Item>
      <Form.Item name="requirements" label="需求描述">
        <Input.TextArea rows={3} placeholder="请描述您的具体需求场景（选填）" />
      </Form.Item>
      <Form.Item>
        <Button type="primary" htmlType="submit" block loading={apply.isPending} style={{ height: 48, borderRadius: 24, fontSize: 16 }}>
          提交入驻申请
        </Button>
      </Form.Item>
    </Form>
  )
}

/* ── 主页面 ── */

export default function LandingPage() {
  const { data: banners } = useBanners()
  const { data: skills } = useSkills()
  const { data: policies } = usePolicies()
  const { data: contacts } = useContacts()

  const banner = banners?.[0]
  const heroBg = banner?.image_url || ''

  const heroStyle = useMemo(() => ({
    backgroundImage: heroBg
      ? `linear-gradient(135deg, rgba(13,71,161,0.7), rgba(0,0,0,0.6)), url('${heroBg}')`
      : 'linear-gradient(135deg, #0d47a1, #1a237e)',
    backgroundSize: 'cover' as const,
    backgroundPosition: 'center' as const,
  }), [heroBg])

  const manager = contacts?.find((c: any) => c.type === 'manager')
  const email = contacts?.find((c: any) => c.type === 'email')
  const address = contacts?.find((c: any) => c.type === 'address')

  return (
    <div>
      {/* 导航栏 */}
      <nav className="navbar">
        <div className="nav-inner">
          <div className="nav-logo">
            <span>南京流苏智慧</span>
          </div>
          <div className="nav-links">
            <a href="#home">首页</a>
            <a href="#about">关于我们</a>
            <a href="#skills">核心产品</a>
            <a href="#policy">政策合规</a>
            <a className="nav-btn" href="#apply">申请试用</a>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section id="home" className="hero" style={heroStyle}>
        <div className="hero-overlay" />
        <div className="hero-content">
          <h1>{banner?.title || '智驭安全，赋能工业'}</h1>
          <p>{banner?.subtitle || 'AI 智能体驱动的工业安全底座'}</p>
          <div className="hero-btns">
            <a href="#apply" className="hero-btn-primary">{banner?.button_text || '申请入驻'}</a>
            <a href="#skills" className="hero-btn-secondary">了解 Skill</a>
          </div>
        </div>
      </section>

      {/* 关于我们 */}
      <section id="about" className="section about">
        <div className="section-inner">
          <h2 className="section-title">关于我们</h2>
          <div className="about-content">
            <p>
              南京流苏智慧信息技术有限公司成立于 2023 年，作为国内领先的
              <strong>AI 驱动的安全生产信息化解决方案提供商</strong>，
              我们深耕工业制造与高危作业领域，专注于 AI 智能体在安全生产场景的深度研发。
            </p>
            <p style={{ marginTop: 20 }}>
              我们以 <strong>AI 智能体为核心引擎</strong>，融合机器学习、计算机视觉与知识图谱技术，
              构建覆盖风险识别、智能预警、动态决策的全链路安全管理体系。
              让隐患无所遁形，让预防先于事故。
            </p>
            <p style={{ marginTop: 20 }}>
              自成立以来，我们已成功服务多家大中型政企客户，助力企业实现从
              <strong>"被动防御"向"主动智能预防"</strong>的根本性跨越。
            </p>
          </div>
        </div>
      </section>

      {/* Skill 展示 */}
      <section id="skills" className="section" style={{ background: '#fff' }}>
        <div className="section-inner">
          <h2 className="section-title">AI 智能体平台</h2>
          <p className="section-subtitle">
            基于 AI 智能体架构的工业安全管理平台，Skill 即产品，可组合、可复用、可编排
          </p>
          <div className="skill-grid">
            {skills?.map((s: any) => <SkillCard key={s.id} skill={s} />)}
          </div>
        </div>
      </section>

      {/* 政策合规 */}
      <section id="policy" className="section">
        <div className="section-inner">
          <h2 className="section-title">政策驱动与合规保障</h2>
          <p className="section-subtitle">
            平台架构严格遵循国家及应急管理部最新颁布的安全生产数字化建设指导文件
          </p>
          <div className="policy-grid">
            {policies?.map((p: any) => (
              <div key={p.id} className="policy-card">
                <div className="policy-dept">{p.dept}</div>
                {p.doc_number && <div className="policy-doc-num">{p.doc_number}</div>}
                <div className="policy-title">{p.title}</div>
                <div className="policy-desc">{p.description}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* 入驻申请 */}
      <section id="apply" className="section apply-section">
        <div className="section-inner">
          <h2 className="section-title">申请入驻</h2>
          <p className="section-subtitle">
            填写以下信息，我们的客户经理将为您开通专属演示环境
          </p>
          <div className="apply-form-wrap">
            <ApplySection />
          </div>
        </div>
      </section>

      {/* 页脚 */}
      <footer className="footer">
        <div className="footer-inner">
          <div>
            <h4>南京流苏智慧信息技术有限公司</h4>
            {manager && <p><strong>客户经理：</strong>{manager.value}</p>}
            {email && <p><strong>电子邮箱：</strong>{email.value}</p>}
            {address && <p><strong>办公地址：</strong>{address.value}</p>}
          </div>
          <div>
            <h4>联系我们</h4>
            {manager && <p><strong>客户经理：</strong>{manager.value}</p>}
            {email && <p><strong>电子邮箱：</strong>{email.value}</p>}
            {address && <p><strong>办公地址：</strong>{address.value}</p>}
          </div>
        </div>
        <div className="footer-bottom">
          <p>© 2026 南京流苏智慧信息技术有限公司 &nbsp;|&nbsp; <a href="https://beian.miit.gov.cn/" target="_blank">苏ICP备2023033527号</a></p>
        </div>
      </footer>
    </div>
  )
}
