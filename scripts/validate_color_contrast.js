/**
 * Color Contrast Validator
 * Validates WCAG AA/AAA compliance for Analog Quest color palette
 */

// Convert hex to RGB
function hexToRgb(hex) {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  return result ? {
    r: parseInt(result[1], 16),
    g: parseInt(result[2], 16),
    b: parseInt(result[3], 16)
  } : null;
}

// Calculate relative luminance
function getLuminance(rgb) {
  const rsRGB = rgb.r / 255;
  const gsRGB = rgb.g / 255;
  const bsRGB = rgb.b / 255;

  const r = rsRGB <= 0.03928 ? rsRGB / 12.92 : Math.pow((rsRGB + 0.055) / 1.055, 2.4);
  const g = gsRGB <= 0.03928 ? gsRGB / 12.92 : Math.pow((gsRGB + 0.055) / 1.055, 2.4);
  const b = bsRGB <= 0.03928 ? bsRGB / 12.92 : Math.pow((bsRGB + 0.055) / 1.055, 2.4);

  return 0.2126 * r + 0.7152 * g + 0.0722 * b;
}

// Calculate contrast ratio
function getContrastRatio(color1, color2) {
  const lum1 = getLuminance(hexToRgb(color1));
  const lum2 = getLuminance(hexToRgb(color2));

  const lighter = Math.max(lum1, lum2);
  const darker = Math.min(lum1, lum2);

  return (lighter + 0.05) / (darker + 0.05);
}

// WCAG compliance check
function checkWCAG(ratio, level = 'AA', size = 'normal') {
  const requirements = {
    'AA': { normal: 4.5, large: 3.0 },
    'AAA': { normal: 7.0, large: 4.5 }
  };

  const required = requirements[level][size];
  const passes = ratio >= required;

  return {
    ratio: ratio.toFixed(2),
    required: required.toFixed(1),
    passes,
    level,
    size
  };
}

// Analog Quest color palette
const colors = {
  cream: '#FEF9ED',
  brown: '#5D524B',
  brownDark: '#451B25',
  teal: '#CAE1E1',
  tealLight: '#DCEAEA',
};

console.log('='.repeat(60));
console.log('WCAG Color Contrast Validation - Analog Quest');
console.log('='.repeat(60));
console.log();

// Test combinations
const combinations = [
  { fg: 'brown', bg: 'cream', desc: 'Brown text on Cream background' },
  { fg: 'brownDark', bg: 'cream', desc: 'Brown Dark text on Cream background' },
  { fg: 'brown', bg: 'tealLight', desc: 'Brown text on Teal Light background' },
  { fg: 'brownDark', bg: 'tealLight', desc: 'Brown Dark text on Teal Light background' },
];

let allPass = true;

combinations.forEach((combo) => {
  const ratio = getContrastRatio(colors[combo.fg], colors[combo.bg]);
  const aaCheck = checkWCAG(ratio, 'AA', 'normal');
  const aaaCheck = checkWCAG(ratio, 'AAA', 'normal');
  const aaLargeCheck = checkWCAG(ratio, 'AA', 'large');

  console.log(`${combo.desc}`);
  console.log(`  Foreground: ${colors[combo.fg]}`);
  console.log(`  Background: ${colors[combo.bg]}`);
  console.log(`  Contrast Ratio: ${ratio.toFixed(2)}:1`);
  console.log(`  WCAG AA (normal text ≥18pt):  ${aaCheck.passes ? '✓ PASS' : '✗ FAIL'} (requires ${aaCheck.required}:1)`);
  console.log(`  WCAG AA (large text ≥18pt):   ${aaLargeCheck.passes ? '✓ PASS' : '✗ FAIL'} (requires ${aaLargeCheck.required}:1)`);
  console.log(`  WCAG AAA (normal text):       ${aaaCheck.passes ? '✓ PASS' : '✗ FAIL'} (requires ${aaaCheck.required}:1)`);

  if (!aaCheck.passes) {
    allPass = false;
    console.log(`  ⚠️  WARNING: Does not meet WCAG AA for normal text!`);
  }

  console.log();
});

console.log('='.repeat(60));
if (allPass) {
  console.log('✓ All color combinations pass WCAG AA standards');
} else {
  console.log('⚠️  Some color combinations do not meet WCAG AA standards');
  console.log('   Consider using only for large text or adjusting colors');
}
console.log('='.repeat(60));

// Export results for reference
const results = combinations.map(combo => ({
  combination: combo.desc,
  foreground: colors[combo.fg],
  background: colors[combo.bg],
  ratio: getContrastRatio(colors[combo.fg], colors[combo.bg]).toFixed(2),
  wcagAA: checkWCAG(getContrastRatio(colors[combo.fg], colors[combo.bg]), 'AA', 'normal'),
  wcagAAA: checkWCAG(getContrastRatio(colors[combo.fg], colors[combo.bg]), 'AAA', 'normal'),
}));

console.log('\nDetailed Results (JSON):');
console.log(JSON.stringify(results, null, 2));
