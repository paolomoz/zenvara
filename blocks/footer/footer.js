import { getMetadata } from '../../scripts/aem.js';
import { loadFragment } from '../fragment/fragment.js';

/**
 * loads and decorates the footer
 * @param {Element} block The footer block element
 */
export default async function decorate(block) {
  // load footer as fragment
  const footerMeta = getMetadata('footer');
  const footerPath = footerMeta ? new URL(footerMeta, window.location).pathname : '/footer';
  const fragment = await loadFragment(footerPath);

  // handle case where fragment failed to load
  if (!fragment) {
    // eslint-disable-next-line no-console
    console.warn('Failed to load footer fragment from', footerPath);
    return;
  }

  // decorate footer DOM
  block.textContent = '';
  const footer = document.createElement('div');
  while (fragment.firstElementChild) footer.append(fragment.firstElementChild);

  // Group social icons into a horizontal row
  const firstSection = footer.querySelector('.section:first-child .default-content-wrapper');
  if (firstSection) {
    // Find paragraphs containing images (social icons)
    // Skip first paragraph (logo) and third paragraph (description text)
    const allParagraphs = Array.from(firstSection.querySelectorAll('p'));
    const iconParagraphs = allParagraphs.filter((p, index) => {
      // Skip first 3 paragraphs: logo (0), ID (1), description (2)
      if (index < 3) return false;
      const hasPicture = p.querySelector('picture') || p.querySelector('img');
      return hasPicture;
    });

    if (iconParagraphs.length > 0) {
      const socialRow = document.createElement('div');
      socialRow.className = 'social-icons';
      iconParagraphs.forEach((p) => socialRow.appendChild(p));
      firstSection.appendChild(socialRow);
    }
  }

  block.append(footer);
}
