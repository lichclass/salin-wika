<script>
  /** @type {string} */
  export let text = '';
  /** @type {boolean} */
  export let loading = false;
  /** @type {string} */
  export let error = '';
</script>

<section class="result" aria-labelledby="result-heading">
  <div class="result__header">
    <span id="result-heading" class="result__eyebrow">Target</span>
    <span class="result__hint">Tagalog output</span>
  </div>
  <div class="result__body" aria-live="polite">
    {#if loading}
      <p class="result__status">Running translation...</p>
    {:else if error}
      <p class="result__error">{error}</p>
    {:else if text}
      <p>{text}</p>
    {:else}
      <p class="result__status">Your translation will appear here.</p>
    {/if}
  </div>
</section>

<style>
  .result {
    display: flex;
    flex: 1 1 auto;
    width: 100%;
    flex-direction: column;
    gap: 0.75rem;
    padding: 1rem;
    background: rgba(26, 34, 44, 0.92);
    border: 1px solid var(--color-border);
    border-radius: 6px;
    min-height: 100%;
    box-sizing: border-box;
  }

  .result__header {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    gap: 0.75rem;
  }

  .result__eyebrow {
    font-family: var(--font-mono);
    font-size: 0.7rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--color-accent-gold);
  }

  .result__hint {
    color: var(--color-text-muted);
    font-size: 0.85rem;
  }

  .result__body {
    flex: 1;
    background: var(--color-surface-raised);
    border: 1px solid var(--color-border);
    border-radius: 4px;
    padding: 0.9rem;
    min-height: 14rem;
    height: 100%;
    font-size: 1rem;
    line-height: 1.6;
    white-space: pre-wrap;
  }

  .result__status {
    color: var(--color-text-muted);
    font-style: italic;
  }

  .result__error {
    color: var(--color-error);
  }
</style>
