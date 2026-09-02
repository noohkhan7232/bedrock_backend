from core.constants.base import CONSTANTS


TEMPLATE_RESPONSES = {
  'block': (
'''I'm sorry, I am unable to process that request. Please try rephrasing your query.'''
  ),
  'contact_sales': (
f'''For questions about pricing, plans, or adding to your account, you can reach our sales team at {CONSTANTS.CONTACTS.SALES_CONTACT}.'''
  ),
  'empty': (
'''It looks like your message was empty. Could you please try sending your message again?'''
  ),
  'support_escalation': (
f'''I'm sorry I couldn't resolve this for you. It sounds like our technical support team needs to investigate this. You can reach them directly at {CONSTANTS.CONTACTS.SUPPORT_CONTACT} or through the 'Help' widget in the app.'''
  ),
  'support_inquiry': (
f'''For bug reports, feature suggestions, or general support questions, you can contact our team by emailing {CONSTANTS.CONTACTS.SUPPORT_CONTACT} or using the 'Help' widget in the app.'''
  ),
}
