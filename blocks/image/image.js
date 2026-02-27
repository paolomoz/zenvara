/*
 * Image Block
 * Displays a standalone image with 16:9 aspect ratio
 */

export default function decorate(block) {
  // The image block is simple - just ensure proper structure
  const picture = block.querySelector('picture');
  if (picture) {
    // Move picture to be direct child of block
    block.textContent = '';
    block.appendChild(picture);
  }
}
