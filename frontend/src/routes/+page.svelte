<script>
  import { onMount } from 'svelte';
  import { fetchCorpusSamples, fetchModels, translateText } from '$lib/api.js';
  import ModelPicker from '$lib/components/ModelPicker.svelte';
  import TranslateBox from '$lib/components/TranslateBox.svelte';
  import ResultCard from '$lib/components/ResultCard.svelte';

  /** @type {Array<{name: string, bidirectional: boolean, peeky: boolean, bleu: number|null}>} */
  let models = [];
  let selectedModel = '';
  let inputText = '';
  let outputText = '';
  let loading = false;
  let error = '';
  let modelsError = '';
  let samples = [
    'Maayong buntag.',
    'Asa ka paingon?',
    'Palihog tabangi ko.'
  ];
  let corpusMessage = 'Loading local demo corpus...';

  onMount(async () => {
    const [modelsResult, samplesResult] = await Promise.allSettled([
      fetchModels(),
      fetchCorpusSamples()
    ]);

    if (modelsResult.status === 'fulfilled') {
      models = modelsResult.value;
      if (models.length) selectedModel = models[0].name;
    } else {
      modelsError = modelsResult.reason instanceof Error ? modelsResult.reason.message : String(modelsResult.reason);
    }

    if (samplesResult.status === 'fulfilled' && samplesResult.value.length) {
      samples = samplesResult.value.map((sample) => sample.source_text);
      corpusMessage = `Loaded ${samplesResult.value.length} local demo corpus samples.`;
    } else if (samplesResult.status === 'rejected') {
      corpusMessage = samplesResult.reason instanceof Error ? samplesResult.reason.message : String(samplesResult.reason);
    } else {
      corpusMessage = 'Local corpus examples are unavailable right now.';
    }
  });

  function useSample(text) {
    inputText = text;
  }

  $: canTranslate = models.length > 0 && !!selectedModel;

  /** @param {CustomEvent<string>} event */
  async function handleTranslate(event) {
    const text = event.detail;

    if (!selectedModel) {
      error = 'No model is available in interface mode.';
      return;
    }

    loading = true;
    error = '';
    outputText = '';

    try {
      const result = await translateText(selectedModel, text);
      outputText = result.translated_text;
    } catch (err) {
      error = err instanceof Error ? err.message : String(err);
    } finally {
      loading = false;
    }
  }
</script>

<svelte:head>
  <title>SalinWika | Cebuano to Tagalog</title>
  <meta
    name="description"
    content="SalinWika is a local interface for Cebuano to Tagalog translation demos."
  />
</svelte:head>

<main class="page">
  <header class="masthead">
    <div>
      <p class="masthead__brand">SalinWika</p>
      <h1>Cebuano to Tagalog</h1>
    </div>
    <p class="masthead__description">A local translation demo built from the project corpus.</p>
  </header>

  <section class="examples" aria-labelledby="examples-heading">
    <div class="examples__heading">
      <div>
        <p class="examples__label">Corpus examples</p>
        <h2 id="examples-heading">Choose text to translate</h2>
      </div>
      <p class="examples__message">{corpusMessage}</p>
    </div>
    <div class="examples__buttons">
      {#each samples as sample}
        <button class="examples__button" type="button" on:click={() => useSample(sample)}>{sample}</button>
      {/each}
    </div>
  </section>

  {#if modelsError}
    <p class="page__error">Could not load models: {modelsError}</p>
  {/if}

  {#if models.length}
    <div class="page__model">
      <ModelPicker {models} bind:selected={selectedModel} />
    </div>
  {:else}
    <p class="page__status">No local demo model is available yet.</p>
  {/if}

  <section class="panels">
    <TranslateBox bind:value={inputText} {loading} ready={canTranslate} on:translate={handleTranslate} />
    <div class="panels__divider" aria-hidden="true"></div>
    <ResultCard text={outputText} {loading} {error} />
  </section>
</main>

<style>
  .page {
    max-width: 1100px;
    margin: 0 auto;
    padding: 2.25rem 1.5rem 3.5rem;
  }

  .masthead {
    display: flex;
    align-items: end;
    justify-content: space-between;
    gap: 2rem;
    padding: 0 0 1.5rem;
    border-bottom: 1px solid var(--color-border);
  }

  .masthead__brand,
  .examples__label {
    margin: 0;
    font-family: var(--font-mono);
    font-size: 0.72rem;
    letter-spacing: 0;
    text-transform: uppercase;
    color: var(--color-accent-teal);
  }

  .masthead h1 {
    margin: 0.35rem 0 0;
    font-family: var(--font-display);
    font-size: clamp(2.4rem, 5vw, 4.5rem);
    line-height: 1;
    letter-spacing: 0;
    color: #f4f5f5;
  }

  .masthead__description {
    max-width: 31ch;
    margin: 0;
    color: var(--color-text-muted);
    line-height: 1.5;
  }

  .examples {
    padding: 1.5rem 0;
    border-bottom: 1px solid var(--color-border);
  }

  .examples__heading {
    display: flex;
    justify-content: space-between;
    align-items: end;
    gap: 1.5rem;
  }

  .examples h2 {
    margin: 0.3rem 0 0;
    font-size: 1.15rem;
  }

  .examples__message {
    max-width: 36ch;
    margin: 0;
    color: var(--color-text-muted);
    font-size: 0.9rem;
    text-align: right;
  }

  .examples__buttons {
    display: flex;
    flex-wrap: wrap;
    gap: 0.65rem;
    margin-top: 0.75rem;
  }

  .examples__button {
    border: 1px solid var(--color-border);
    background: transparent;
    color: var(--color-text);
    border-radius: 4px;
    padding: 0.58rem 0.9rem;
    cursor: pointer;
    transition: background 0.15s ease, border-color 0.15s ease;
  }

  .examples__button:hover {
    background: var(--color-surface-raised);
    border-color: var(--color-accent-teal);
  }

  .page__model {
    width: 100%;
    margin: 1.5rem 0;
  }

  .page__error {
    color: var(--color-error);
  }

  .page__status {
    color: var(--color-text-muted);
  }

  .panels {
    display: grid;
    grid-template-columns: minmax(0, 1fr) auto minmax(0, 1fr);
    gap: 1.25rem;
    align-items: stretch;
  }

  .panels__divider {
    align-self: stretch;
    width: 1px;
    background-image: repeating-linear-gradient(
      to bottom,
      var(--color-accent-gold) 0 6px,
      transparent 6px 14px
    );
  }

  @media (max-width: 720px) {
    .page {
      padding: 1.5rem 1rem 2.5rem;
    }

    .masthead,
    .examples__heading {
      align-items: start;
      flex-direction: column;
      gap: 0.8rem;
    }

    .examples__message {
      text-align: left;
    }

    .panels {
      grid-template-columns: 1fr;
    }

    .panels__divider {
      display: none;
    }
  }
</style>
