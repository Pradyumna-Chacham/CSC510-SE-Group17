import { create } from 'zustand';

const useSessionStore = create((set) => ({
  currentSessionId: null,
  projectContext: '',
  domain: '',
  useCases: [],
  
  setCurrentSession: (sessionId) => set({ currentSessionId: sessionId }),
  setProjectContext: (context) => set({ projectContext: context }),
  setDomain: (domain) => set({ domain: domain }),
  setUseCases: (useCases) => set({ useCases: useCases }),
  
  clearSession: () => set({
    currentSessionId: null,
    projectContext: '',
    domain: '',
    useCases: [],
  }),
}));

export default useSessionStore;