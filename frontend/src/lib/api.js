const DEMO_MODELS = [
  { name: 'cebuano-tagalog-demo', bidirectional: false, peeky: false, bleu: 92.4 },
  { name: 'cebuano-tagalog-lite', bidirectional: true, peeky: false, bleu: 88.7 }
];

const DEMO_CORPUS = [
  { source_text: 'Maayong buntag.', target_text: 'Magandang umaga.' },
  { source_text: 'Asa ka paingon?', target_text: 'Saan ka pupunta?' },
  { source_text: 'Palihog tabangi ko.', target_text: 'Pakiusap, tulungan mo ako.' },
  { source_text: 'Dako kaayo ang kalipay nako.', target_text: 'Napakasaya ko ngayon.' },
  { source_text: 'Unsa imong ngalan?', target_text: 'Ano ang iyong pangalan?' },
  { source_text: 'Mao ra ni ang akong gusto.', target_text: 'Iyan lang ang gusto ko.' }
];

const DEMO_TRANSLATIONS = new Map(
  DEMO_CORPUS.map(({ source_text, target_text }) => [source_text.trim().toLowerCase(), target_text])
);

/** @returns {Promise<Array<{name: string, bidirectional: boolean, peeky: boolean, bleu: number|null}>>} */
export async function fetchModels() {
  return DEMO_MODELS;
}

/** @returns {Promise<Array<{source_text: string, target_text: string}>>} */
export async function fetchCorpusSamples() {
  return DEMO_CORPUS;
}

/** @returns {Promise<{status: string}>} */
export async function fetchHealth() {
  return { status: 'local-interface' };
}

/**
 * @param {string} modelName
 * @param {string} text
 * @returns {Promise<{model_name: string, source_text: string, translated_text: string}>}
 */
export async function translateText(modelName, text) {
  const normalized = text.trim();

  if (!normalized) {
    throw new Error('Please enter some Cebuano text to translate.');
  }

  const translated = DEMO_TRANSLATIONS.get(normalized.toLowerCase());

  if (!translated) {
    throw new Error('This local demo can translate the provided corpus examples only. Choose an example above to try it.');
  }

  return {
    model_name: modelName,
    source_text: normalized,
    translated_text: translated
  };
}
