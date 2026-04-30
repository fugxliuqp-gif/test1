import { useQuery, useMutation } from '@tanstack/react-query'
import api from '../api/client'
import type { Banner, Skill, Policy, ContactInfo, ApplyForm } from '../types/cms'

export function useBanners() {
  return useQuery({
    queryKey: ['banners'],
    queryFn: () => api.get<Banner[]>('/cms/banners').then(r => r.data),
  })
}

export function useSkills() {
  return useQuery({
    queryKey: ['skills'],
    queryFn: () => api.get<Skill[]>('/cms/skills').then(r => r.data),
  })
}

export function usePolicies() {
  return useQuery({
    queryKey: ['policies'],
    queryFn: () => api.get<Policy[]>('/cms/policies').then(r => r.data),
  })
}

export function useContacts() {
  return useQuery({
    queryKey: ['contacts'],
    queryFn: () => api.get<ContactInfo[]>('/cms/contact').then(r => r.data),
  })
}

export function useApply() {
  return useMutation({
    mutationFn: (data: ApplyForm) =>
      api.post('/apply', data).then(r => r.data as { tracking_code: string }),
  })
}
