export interface Banner {
  id: number
  title: string
  subtitle?: string
  image_url: string
  button_text: string
  button_link: string
  sort_order: number
  is_active: boolean
}

export interface Skill {
  id: number
  key: string
  name: string
  icon?: string
  summary: string
  description?: string
  scenarios?: string
  capabilities?: string
  platforms?: string
  sort_order: number
  is_active: boolean
}

export interface Policy {
  id: number
  dept: string
  doc_number?: string
  title: string
  description?: string
  sort_order: number
  is_active: boolean
}

export interface ContactInfo {
  id: number
  type: string
  label: string
  value: string
  display_order: number
}

export interface EnterpriseApplication {
  id: number
  company_name: string
  credit_code: string
  industry: string
  scale: string
  contact_name: string
  contact_phone: string
  contact_email: string
  interested_skills?: string
  requirements?: string
  current_systems?: string
  status: string
  reject_reason?: string
  tracking_code: string
  created_at: string
}

export interface ApplyForm {
  company_name: string
  credit_code: string
  industry: string
  scale: string
  contact_name: string
  contact_phone: string
  contact_email: string
  interested_skills?: string
  requirements?: string
  current_systems?: string
}
