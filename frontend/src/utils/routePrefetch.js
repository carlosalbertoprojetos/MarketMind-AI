const routeImporters = {
  dashboard: () => import('../pages/Dashboard'),
  createCampaign: () => import('../pages/CreateCampaign'),
  campaignDetail: () => import('../pages/CampaignDetail'),
  campaignPreview: () => import('../pages/CampaignPreviewPage'),
  calendar: () => import('../pages/CalendarPage'),
  credentials: () => import('../pages/CredentialsPage'),
  media: () => import('../pages/MediaLibraryPage'),
  finalContent: () => import('../pages/FinalContentPage'),
  about: () => import('../pages/AboutPage'),
  login: () => import('../pages/Login'),
  register: () => import('../pages/Register'),
  notFound: () => import('../pages/NotFoundPage'),
}

const prefetchedRoutes = new Set()

export function preloadRoute(name) {
  const importer = routeImporters[name]
  if (!importer || prefetchedRoutes.has(name)) return Promise.resolve(null)
  prefetchedRoutes.add(name)
  return importer().catch((error) => {
    prefetchedRoutes.delete(name)
    throw error
  })
}

export function preloadRoutes(names = []) {
  return Promise.allSettled(names.map((name) => preloadRoute(name)))
}

export function buildPrefetchHandlers(names = []) {
  let started = false
  const trigger = () => {
    if (started) return
    started = true
    void preloadRoutes(names)
  }
  return {
    onMouseEnter: trigger,
    onFocus: trigger,
    onTouchStart: trigger,
  }
}

export function preloadRoutesWhenIdle(names = []) {
  const trigger = () => {
    void preloadRoutes(names)
  }

  if (typeof window === 'undefined') {
    trigger()
    return () => {}
  }

  if ('requestIdleCallback' in window) {
    const handle = window.requestIdleCallback(trigger, { timeout: 1500 })
    return () => window.cancelIdleCallback?.(handle)
  }

  const handle = window.setTimeout(trigger, 300)
  return () => window.clearTimeout(handle)
}
