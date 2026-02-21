export const mockChatMessages = [
  {
    id: 1,
    type: 'user',
    text: 'How do I access the user guide for this chatbot?',
    timestamp: '09:45 AM',
  },
  {
    id: 2,
    type: 'bot',
    text: 'User guides can be found at pspd-guardian-help-dev.cbp.dhs.gov',
    timestamp: '09:46 AM',
    link: 'https://pspd-guardian-help-dev.cbp.dhs.gov',
    showFeedback: true,
  },
  {
    id: 3,
    type: 'user',
    text: 'Yes thank you!',
    timestamp: '09:47 AM',
  },
  {
    id: 4,
    type: 'bot',
    text: 'How else can we help you today?',
    timestamp: '09:49 AM',
    showFeedback: false,
  },
];

export const mockChatHistory = [];

export const mockAgentStatus = {
  connected: true,
  label: 'ADK Agent Status',
  detail: 'Connected to Spanner Vector Search',
};

export const mockConnectionStatus = {
  connected: true,
  label: 'Connected',
};

export const mockServiceAuth = {
  authenticated: true,
  label: 'Service Account Authentication',
};
