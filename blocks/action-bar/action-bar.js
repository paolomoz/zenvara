/**
 * Action Bar Block
 * Displays metadata text (like publication date) and action buttons (like, save, share)
 * @param {Element} block The action-bar block element
 */
export default function decorate(block) {
  // Get the content rows
  const rows = [...block.children];

  // Create wrapper structure
  const wrapper = document.createElement('div');
  wrapper.className = 'action-bar-wrapper';

  // First row is the meta text (e.g., "Published 00/00/00")
  if (rows[0]) {
    const metaText = document.createElement('div');
    metaText.className = 'action-bar-meta';
    metaText.innerHTML = rows[0].innerHTML;
    wrapper.appendChild(metaText);
  }

  // Second row contains the action buttons
  if (rows[1]) {
    const actions = document.createElement('div');
    actions.className = 'action-bar-actions';

    // Process each action button from the row
    const buttons = rows[1].querySelectorAll('div > div');
    buttons.forEach((btn) => {
      const actionButton = document.createElement('button');
      actionButton.className = 'action-bar-button';
      actionButton.type = 'button';

      // Get button type from content or data attribute
      const buttonText = btn.textContent.trim().toLowerCase();
      actionButton.setAttribute('data-action', buttonText);
      actionButton.setAttribute('aria-label', buttonText);

      // Add appropriate icon based on action type
      const icon = document.createElement('span');
      icon.className = 'action-bar-icon';

      if (buttonText.includes('like') || buttonText.includes('heart')) {
        icon.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path></svg>';
      } else if (buttonText.includes('save') || buttonText.includes('bookmark')) {
        icon.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"></path></svg>';
      } else if (buttonText.includes('share')) {
        icon.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="18" cy="5" r="3"></circle><circle cx="6" cy="12" r="3"></circle><circle cx="18" cy="19" r="3"></circle><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"></line><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"></line></svg>';
      }

      actionButton.appendChild(icon);
      actions.appendChild(actionButton);
    });

    wrapper.appendChild(actions);
  }

  // Clear and rebuild block
  block.textContent = '';
  block.appendChild(wrapper);
}
