<script>
  /** @type {Array<{name: string, bidirectional: boolean, peeky: boolean, bleu: number|null}>} */
  export let models = [];
  /** @type {string} */
  export let selected = '';

  $: selectedModel = models.find((model) => model.name === selected) ?? null;
</script>

<section class="picker" aria-labelledby="model-heading">
  <div class="picker__header">
    <div>
      <span class="picker__label">Modelo</span>
      <h2 id="model-heading">Translation model</h2>
    </div>
    {#if selectedModel}
      <div class="picker__summary">
        {#if selectedModel.bidirectional}
          <span>Bidirectional</span>
        {/if}
        {#if selectedModel.peeky}
          <span>Peeky decoder</span>
        {/if}
        {#if selectedModel.bleu != null}
          <span>BLEU {selectedModel.bleu.toFixed(1)}</span>
        {/if}
      </div>
    {/if}
  </div>

  <select bind:value={selected} class="picker__select" aria-label="Select translation model">
    {#each models as model (model.name)}
      <option value={model.name}>
        {model.name}{model.bleu != null ? ` · BLEU ${model.bleu.toFixed(1)}` : ''}
      </option>
    {/each}
  </select>

  {#if selectedModel}
    <p class="picker__details">
      {selectedModel.name} is the active run for Cebuano to Tagalog translation.
    </p>
  {/if}
</section>

<style>
  .picker {
    display: flex;
    width: 100%;
    flex-direction: column;
    gap: 0.75rem;
    padding: 1rem;
    background: rgba(33, 43, 55, 0.9);
    border: 1px solid var(--color-border);
    border-radius: 6px;
    box-sizing: border-box;
  }

  .picker__label {
    font-family: var(--font-mono);
    font-size: 0.7rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--color-text-muted);
  }

  .picker__header {
    display: flex;
    justify-content: space-between;
    gap: 1rem;
    align-items: start;
  }

  .picker__header h2 {
    margin: 0.25rem 0 0;
    font-size: 1.05rem;
    letter-spacing: -0.01em;
  }

  .picker__summary {
    display: flex;
    flex-wrap: wrap;
    gap: 0.4rem;
    justify-content: flex-end;
  }

  .picker__summary span {
    padding: 0.3rem 0.55rem;
    border-radius: 4px;
    background: rgba(212, 162, 76, 0.12);
    border: 1px solid rgba(212, 162, 76, 0.22);
    color: var(--color-accent-gold);
    font-size: 0.78rem;
    white-space: nowrap;
  }

  .picker__select {
    width: 100%;
    background: var(--color-surface-raised);
    color: var(--color-text);
    border: 1px solid var(--color-border);
    border-radius: 4px;
    padding: 0.5rem 0.75rem;
    font-size: 0.95rem;
    box-sizing: border-box;
  }

  .picker__details {
    margin: 0;
    color: rgba(211, 221, 231, 0.7);
    font-size: 0.72rem;
    line-height: 1.5;
    font-style: italic;
  }
</style>
